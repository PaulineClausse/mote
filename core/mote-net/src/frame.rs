//! Cadrage des trames (ADR-c36f, SPEC-9df2) : une taille sur 4 octets, ordre réseau (big-endian), puis le message
//! protobuf (`Envelope` du casque vers le PC, `Control` du PC vers le casque).

use std::io::{self, Read, Write};

use mote_proto::v1::{self, envelope::Body};
use mote_proto::Message;

/// Taille maximale d'une trame (SPEC-9df2). Constante du protocole : les deux côtés doivent la partager.
pub const MAX_FRAME: usize = 64 << 20;

/// Écrit une trame déjà encodée.
pub fn write_frame(w: &mut impl Write, payload: &[u8]) -> io::Result<()> {
    if payload.len() > MAX_FRAME {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "trame de plus de 64 Mo",
        ));
    }
    w.write_all(&(payload.len() as u32).to_be_bytes())?;
    w.write_all(payload)
}

/// Lit une trame ; une taille annoncée au-delà de `MAX_FRAME` est une erreur de protocole.
pub fn read_frame(r: &mut impl Read) -> io::Result<Vec<u8>> {
    let mut len = [0u8; 4];
    r.read_exact(&mut len)?;
    let len = u32::from_be_bytes(len) as usize;
    if len > MAX_FRAME {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "trame de plus de 64 Mo",
        ));
    }
    let mut buf = vec![0u8; len];
    r.read_exact(&mut buf)?;
    Ok(buf)
}

/// `Envelope` encodée d'un message de canal.
pub fn envelope(channel: &str, seq: u64, body: Body) -> Vec<u8> {
    v1::Envelope {
        channel: channel.to_owned(),
        seq,
        body: Some(body),
    }
    .encode_to_vec()
}

/// Corps d'`Envelope` d'un message, d'après son canal (SPEC-64c5 §9.1) ; `None` pour un canal inconnu ou des octets
/// illisibles.
pub fn body_from_bytes(channel: &str, bytes: &[u8]) -> Option<Body> {
    Some(match channel {
        "/session/info" => Body::SessionInfo(v1::SessionInfo::decode(bytes).ok()?),
        "/cam/left/frame" | "/cam/right/frame" => Body::Image(v1::ImageFrame::decode(bytes).ok()?),
        "/cam/left/intrinsics" | "/cam/right/intrinsics" => {
            Body::Intrinsics(v1::CameraIntrinsics::decode(bytes).ok()?)
        }
        "/pose/hmd" => Body::Pose(v1::PoseSample::decode(bytes).ok()?),
        "/depth/left" | "/depth/right" => Body::Depth(v1::DepthFrame::decode(bytes).ok()?),
        "/events" => Body::Event(v1::Event::decode(bytes).ok()?),
        "/stats" => Body::Stats(v1::Stats::decode(bytes).ok()?),
        "/session/end" => Body::SessionEnd(v1::SessionEnd::decode(bytes).ok()?),
        _ => return None,
    })
}

/// Seuls les images et la profondeur peuvent être retirés du flux live (SPEC-9df2).
pub fn droppable(channel: &str) -> bool {
    channel.starts_with("/cam/") && channel.ends_with("/frame") || channel.starts_with("/depth/")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn aller_retour_et_ordre_reseau() {
        let mut buf = Vec::new();
        write_frame(&mut buf, b"abc").unwrap();
        assert_eq!(buf, [0, 0, 0, 3, b'a', b'b', b'c']);
        assert_eq!(read_frame(&mut &buf[..]).unwrap(), b"abc");
    }

    #[test]
    fn trame_trop_grosse_refusee() {
        let len = (MAX_FRAME as u32 + 1).to_be_bytes();
        let err = read_frame(&mut &len[..]).unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::InvalidData);
    }

    #[test]
    fn canaux_retirables() {
        for c in [
            "/cam/left/frame",
            "/cam/right/frame",
            "/depth/left",
            "/depth/right",
        ] {
            assert!(droppable(c), "{c}");
        }
        for c in [
            "/session/info",
            "/cam/left/intrinsics",
            "/pose/hmd",
            "/events",
            "/stats",
            "/session/end",
        ] {
            assert!(!droppable(c), "{c}");
        }
    }
}
