//! Étage d'écriture par défaut : le fichier MCAP de session dans `local_dir` (ADR-5955, ADR-d5f3). Traduit chaque
//! record du core en message mote.v1 sur son canal (SPEC-64c5 §9.1) ; poses et profondeur sont écrites telles que
//! l'hôte les a fournies, avec leur convention (ADR-6ded).

use std::io;

use mote_mcap::{v1, Channel, SessionWriter};
use mote_net::v1::envelope::Body;
use mote_net::EVENT_LIVE_DROPPED;

use crate::clock;
use crate::stages::{Live, SessionStart, Writer};
use crate::types::*;

const SCHEMA_VERSION: u32 = 1;

/// Ce que l'hôte déclare dans `session_info_json` (SPEC-fdb8 : appareil, versions, espace de tracking).
#[derive(Clone, Debug, Default, PartialEq)]
pub struct SessionMeta {
    pub device_model: String,
    pub os_build: String,
    /// JSON libre, recopié tel quel.
    pub sdk_versions: String,
    pub host_kind: String,
    pub tracking_space: String,
}

/// Lit `session_info_json` : un objet JSON, champs connus en chaînes (sauf `sdk_versions`, JSON libre), champs
/// inconnus ignorés. `None` si le JSON est invalide.
pub fn session_meta(json: Option<&str>) -> Option<SessionMeta> {
    let Some(json) = json else {
        return Some(SessionMeta::default());
    };
    let v: serde_json::Value = serde_json::from_str(json).ok()?;
    let obj = v.as_object()?;
    let text = |k: &str| match obj.get(k) {
        None | Some(serde_json::Value::Null) => Some(String::new()),
        Some(serde_json::Value::String(s)) => Some(s.clone()),
        Some(_) => None,
    };
    let sdk_versions = match obj.get("sdk_versions") {
        None | Some(serde_json::Value::Null) => String::new(),
        Some(serde_json::Value::String(s)) => s.clone(),
        Some(other) => other.to_string(),
    };
    Some(SessionMeta {
        device_model: text("device_model")?,
        os_build: text("os_build")?,
        sdk_versions,
        host_kind: text("host_kind")?,
        tracking_space: text("tracking_space")?,
    })
}

/// Identifiant de session : date UTC du démarrage, à la milliseconde (`AAAAMMJJ-HHMMSS-mmm`).
pub(crate) fn session_id(unix_ns: i64) -> String {
    let ms = unix_ns.div_euclid(1_000_000);
    let (secs, ms) = (ms.div_euclid(1000), ms.rem_euclid(1000));
    let (days, sod) = (secs.div_euclid(86_400), secs.rem_euclid(86_400));
    // Jours depuis 1970-01-01 vers date civile (algorithme de H. Hinnant).
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = yoe + era * 400 + i64::from(m <= 2);
    format!(
        "{y:04}{m:02}{d:02}-{:02}{:02}{:02}-{ms:03}",
        sod / 3600,
        sod % 3600 / 60,
        sod % 60
    )
}

fn config_json(c: &Config) -> String {
    // Le jeton d'authentification n'est jamais écrit.
    serde_json::json!({
        "codec": c.codec,
        "jpeg_quality": c.jpeg_quality,
        "kf_min_translation_m": c.kf_min_translation_m,
        "kf_min_rotation_rad": c.kf_min_rotation_rad,
        "kf_min_sharpness": c.kf_min_sharpness,
        "pair_max_dt_ns": c.pair_max_dt_ns,
        "flags": c.flags,
        "server_addr": c.server_addr,
        "net": {
            "live_queue_bytes": c.net.live_queue_bytes,
            "connect_timeout_ms": c.net.connect_timeout.as_millis() as u64,
            "reconnect_min_ms": c.net.reconnect_min.as_millis() as u64,
            "reconnect_max_ms": c.net.reconnect_max.as_millis() as u64,
            "resend_batch_ms": c.net.resend_batch.as_millis() as u64,
        },
    })
    .to_string()
}

fn pose3(p: &Pose) -> v1::Pose3 {
    v1::Pose3 {
        px: p.p[0],
        py: p.p[1],
        pz: p.p[2],
        qx: p.q[0],
        qy: p.q[1],
        qz: p.q[2],
        qw: p.q[3],
    }
}

/// Convention et pose, ou convention non précisée et pose absente.
fn split(p: Option<&ConventionPose>) -> (i32, Option<v1::Pose3>) {
    p.map_or((0, None), |p| (p.convention as i32, Some(pose3(&p.pose))))
}

fn image(pair_id: u64, f: EncodedFrame) -> v1::ImageFrame {
    let s = f.source;
    let (convention, world_from_camera) = split(s.world_from_camera.as_ref());
    v1::ImageFrame {
        pair_id,
        t_ns: s.t_ns,
        src_time_ns: s.src_time_ns,
        src_domain: s.src_domain as i32,
        width: s.width,
        height: s.height,
        codec: f.codec as i32,
        data: f.data,
        convention,
        world_from_camera,
        exposure_ns: s.exposure_ns,
        iso: s.exposure_ns.map(|_| s.iso),
        blur_score: s.blur_score,
    }
}

/// Écrit la session dans le fichier fixé par le core, puis met chaque message en file live si le flux est
/// configuré : un message n'est émis qu'après avoir été remis à l'écriture locale (SPEC-9df2).
#[derive(Default)]
pub struct McapWriter {
    file: Option<SessionWriter>,
    live: Option<Live>,
    /// Taille du fichier une fois fermé.
    closed_len: u64,
}

impl McapWriter {
    pub fn new() -> Self {
        Self::default()
    }

    /// Écrit un message sur son canal, puis le met en file live ; les images et profondeurs que la file retire
    /// donnent chacune un `LIVE_DROPPED`, écrit dans `/events` et remis à l'hôte.
    fn put<M: mote_proto::Message>(
        &mut self,
        channel: Channel,
        log_time_ns: i64,
        msg: M,
        body: fn(M) -> Body,
    ) -> io::Result<()> {
        let f = self
            .file
            .as_mut()
            .ok_or_else(|| io::Error::other("session MCAP non ouverte"))?;
        let seq = f.write(channel, log_time_ns, &msg)?;
        let Some(live) = &self.live else {
            return Ok(());
        };
        let dropped = live.net.push(channel.topic(), seq, body(msg));
        let notify = live.notify.clone();
        for (topic, seq) in dropped {
            let e = Event {
                t_ns: clock::now_ns(),
                kind: EVENT_LIVE_DROPPED,
                detail: format!("{topic} {seq}"),
            };
            notify(e.clone());
            self.put(Channel::Events, e.t_ns, event(e), Body::Event)?;
        }
        Ok(())
    }

    /// Écrit dans `/events` les événements du client réseau (connexion, coupure) reçus depuis le dernier appel.
    fn drain_net_events(&mut self) -> io::Result<()> {
        let pending: Vec<Event> = match &self.live {
            Some(live) => live.events.try_iter().collect(),
            None => return Ok(()),
        };
        for e in pending {
            self.put(Channel::Events, e.t_ns, event(e), Body::Event)?;
        }
        Ok(())
    }
}

fn event(e: Event) -> v1::Event {
    v1::Event {
        t_ns: e.t_ns,
        r#type: e.kind as i32,
        detail: e.detail,
    }
}

impl Writer for McapWriter {
    fn open(&mut self, config: &Config, session: SessionStart) -> io::Result<()> {
        let meta = session_meta(config.session_info_json.as_deref()).unwrap_or_default();
        let info = v1::SessionInfo {
            schema_version: SCHEMA_VERSION,
            session_id: session.id.clone(),
            start_unix_ns: session.start_unix_ns,
            start_t_ns: session.start_t_ns,
            device_model: meta.device_model,
            os_build: meta.os_build,
            sdk_versions: meta.sdk_versions,
            host_kind: meta.host_kind,
            core_version: env!("CARGO_PKG_VERSION").to_owned(),
            tracking_space: meta.tracking_space,
            config_json: config_json(config),
        };
        let (file, info_seq) = SessionWriter::create(&session.path, &info, session.start_t_ns)?;
        self.file = Some(file);
        self.live = session.live;
        if let Some(live) = &self.live {
            let _ = live.net.push(
                Channel::SessionInfo.topic(),
                info_seq,
                Body::SessionInfo(info),
            );
        }
        Ok(())
    }

    fn write(&mut self, record: Record) -> io::Result<()> {
        self.drain_net_events()?;
        match record {
            Record::Pair(p) => {
                let p = *p;
                let (t_l, t_r) = (p.left.source.t_ns, p.right.source.t_ns);
                self.put(Channel::LeftFrame, t_l, image(p.id, p.left), Body::Image)?;
                self.put(Channel::RightFrame, t_r, image(p.id, p.right), Body::Image)
            }
            Record::Intrinsics(i) => {
                let channel = if i.camera == 0 {
                    Channel::LeftIntrinsics
                } else {
                    Channel::RightIntrinsics
                };
                let (convention, hmd_from_camera) = split(i.hmd_from_camera.as_ref());
                let msg = v1::CameraIntrinsics {
                    width: i.width,
                    height: i.height,
                    fx: i.fx,
                    fy: i.fy,
                    cx: i.cx,
                    cy: i.cy,
                    model: i.model as i32,
                    dist: i.dist,
                    convention,
                    hmd_from_camera,
                };
                self.put(channel, clock::now_ns(), msg, Body::Intrinsics)
            }
            Record::HmdPose(p) => {
                let msg = v1::PoseSample {
                    t_ns: p.t_ns,
                    src_time_ns: p.src_time_ns,
                    src_domain: p.src_domain as i32,
                    convention: p.world_from_hmd.convention as i32,
                    world_from_hmd: Some(pose3(&p.world_from_hmd.pose)),
                    predicted: p.predicted,
                };
                self.put(Channel::HmdPose, p.t_ns, msg, Body::Pose)
            }
            Record::Depth(d) => {
                let channel = if d.eye == 0 {
                    Channel::LeftDepth
                } else {
                    Channel::RightDepth
                };
                let msg = v1::DepthFrame {
                    t_ns: d.t_ns,
                    src_time_ns: d.src_time_ns,
                    src_domain: d.src_domain as i32,
                    width: d.width,
                    height: d.height,
                    encoding: d.encoding as i32,
                    data: d.data,
                    convention: d.world_from_depth.convention as i32,
                    world_from_depth: Some(pose3(&d.world_from_depth.pose)),
                    fov_left_tan: d.fov[0],
                    fov_right_tan: d.fov[1],
                    fov_top_tan: d.fov[2],
                    fov_down_tan: d.fov[3],
                    near_z: d.near_z,
                    far_z: d.far_z,
                    min_depth: d.min_depth,
                    max_depth: d.max_depth,
                    src_predicted_display_time_ns: None,
                };
                self.put(channel, d.t_ns, msg, Body::Depth)
            }
            Record::Event(e) => self.put(Channel::Events, e.t_ns, event(e), Body::Event),
            Record::Stats(s) => {
                let msg = v1::Stats {
                    t_ns: s.t_ns,
                    pairs_pushed: s.pairs_pushed,
                    pairs_kept: s.pairs_kept,
                    pairs_dropped: s.pairs_dropped,
                    bytes_written: s.bytes_written,
                    bytes_sent: s.bytes_sent,
                    net_mbps: s.net_mbps,
                    encode_ms_avg: s.encode_ms_avg,
                    live_queue_fill: s.live_queue_fill,
                };
                self.put(Channel::Stats, s.t_ns, msg, Body::Stats)
            }
        }
    }

    fn flush(&mut self) -> io::Result<()> {
        self.drain_net_events()?;
        self.file
            .as_mut()
            .ok_or_else(|| io::Error::other("session MCAP non ouverte"))?
            .flush()
    }

    fn bytes_written(&self) -> u64 {
        self.file
            .as_ref()
            .map_or(self.closed_len, SessionWriter::bytes_written)
    }

    fn finish(&mut self) -> io::Result<()> {
        self.drain_net_events()?;
        let f = self
            .file
            .take()
            .ok_or_else(|| io::Error::other("session MCAP non ouverte"))?;
        let done = f.finish(clock::now_ns())?;
        self.closed_len = done.len;
        if let Some(live) = &self.live {
            let _ = live.net.push(
                Channel::SessionEnd.topic(),
                done.end_seq,
                Body::SessionEnd(done.end),
            );
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn session_id_date_utc() {
        // 2026-10-16T09:05:07.042Z
        assert_eq!(session_id(1_792_141_507_042_000_000), "20261016-090507-042");
        assert_eq!(session_id(0), "19700101-000000-000");
    }

    #[test]
    fn session_meta_champs_connus_et_json_invalide() {
        let m = session_meta(Some(
            r#"{"device_model":"Quest 3S","sdk_versions":{"mruk":"77"},"x":1}"#,
        ))
        .unwrap();
        assert_eq!(m.device_model, "Quest 3S");
        assert_eq!(m.sdk_versions, r#"{"mruk":"77"}"#);
        assert_eq!(session_meta(None), Some(SessionMeta::default()));
        assert_eq!(session_meta(Some("pas du json")), None);
        assert_eq!(session_meta(Some(r#"{"device_model":3}"#)), None);
    }
}
