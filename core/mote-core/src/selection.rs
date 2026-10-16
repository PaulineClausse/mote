//! Sélection des paires (ADR-53f5, FR-04) : une paire est retenue si la translation ou la rotation depuis la
//! dernière paire retenue dépasse son seuil, et si les deux images atteignent le seuil de netteté. Le mouvement est
//! évalué avec la pose de l'image gauche ; la décision porte toujours sur la paire entière.

use crate::types::{Config, FrameView, Pose, FLAG_RECORD_ALL};

/// Largeur visée de la luminance sous-échantillonnée sur laquelle la netteté est mesurée.
const SHARPNESS_WIDTH: usize = 320;

/// Netteté d'une image : variance du Laplacien 4-voisins sur la luminance (BT.601), moyennée par blocs carrés pour
/// ramener la largeur vers `SHARPNESS_WIDTH`. Unités : luminance 0-255, au carré. Lit le buffer de l'hôte sans le
/// copier.
pub fn sharpness(f: &FrameView) -> f32 {
    let (w, h) = (f.width as usize, f.height as usize);
    let k = (w / SHARPNESS_WIDTH).max(1);
    let (sw, sh) = (w / k, h / k);
    if sw < 3 || sh < 3 {
        return 0.0;
    }
    let mut luma = vec![0f32; sw * sh];
    for (by, row) in luma.chunks_exact_mut(sw).enumerate() {
        for (bx, out) in row.iter_mut().enumerate() {
            let mut sum = 0u32;
            for y in by * k..(by + 1) * k {
                let line = &f.rgba[y * f.stride..];
                for x in bx * k..(bx + 1) * k {
                    let p = &line[x * 4..x * 4 + 3];
                    sum += 77 * p[0] as u32 + 150 * p[1] as u32 + 29 * p[2] as u32;
                }
            }
            *out = sum as f32 / (256 * k * k) as f32;
        }
    }
    let (mut n, mut mean, mut m2) = (0f64, 0f64, 0f64);
    for y in 1..sh - 1 {
        for x in 1..sw - 1 {
            let c = luma[y * sw + x];
            let lap = (luma[y * sw + x - 1]
                + luma[y * sw + x + 1]
                + luma[(y - 1) * sw + x]
                + luma[(y + 1) * sw + x]
                - 4.0 * c) as f64;
            // Variance en une passe (Welford).
            n += 1.0;
            let d = lap - mean;
            mean += d / n;
            m2 += d * (lap - mean);
        }
    }
    (m2 / n) as f32
}

/// Translation (m) et rotation (rad) entre deux poses.
fn motion(a: &Pose, b: &Pose) -> (f64, f64) {
    let t =
        ((a.p[0] - b.p[0]).powi(2) + (a.p[1] - b.p[1]).powi(2) + (a.p[2] - b.p[2]).powi(2)).sqrt();
    let norm = |q: &[f64; 4]| q.iter().map(|v| v * v).sum::<f64>().sqrt();
    let (na, nb) = (norm(&a.q), norm(&b.q));
    if na == 0.0 || nb == 0.0 {
        return (t, 0.0);
    }
    let dot: f64 = a.q.iter().zip(&b.q).map(|(x, y)| x * y).sum::<f64>() / (na * nb);
    (t, 2.0 * dot.abs().min(1.0).acos())
}

/// État de la sélection : la pose gauche de la dernière paire retenue.
pub struct Selector {
    min_translation: f64,
    min_rotation: f64,
    min_sharpness: f32,
    record_all: bool,
    last: Option<Pose>,
}

impl Selector {
    pub fn new(c: &Config) -> Self {
        Selector {
            min_translation: c.kf_min_translation_m as f64,
            min_rotation: c.kf_min_rotation_rad as f64,
            min_sharpness: c.kf_min_sharpness,
            record_all: c.flags & FLAG_RECORD_ALL != 0,
            last: None,
        }
    }

    /// La paire doit-elle être retenue ? Sans pose gauche, ou sans paire retenue avant, le mouvement ne peut pas
    /// être évalué et ne bloque pas.
    pub fn wants(&self, left_pose: Option<&Pose>, sharp_left: f32, sharp_right: f32) -> bool {
        if self.record_all {
            return true;
        }
        let moved = match (left_pose, &self.last) {
            (Some(p), Some(last)) => {
                let (t, r) = motion(p, last);
                t > self.min_translation || r > self.min_rotation
            }
            _ => true,
        };
        moved && sharp_left >= self.min_sharpness && sharp_right >= self.min_sharpness
    }

    /// La paire est réellement entrée en file : elle devient la référence du mouvement.
    pub fn kept(&mut self, left_pose: Option<&Pose>) {
        if let Some(p) = left_pose {
            self.last = Some(*p);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn view(px: &[u8], w: u32, h: u32) -> FrameView<'_> {
        FrameView {
            t_ns: 0,
            src_time_ns: 0,
            src_domain: 0,
            width: w,
            height: h,
            stride: w as usize * 4,
            rgba: px,
            world_from_camera: None,
            exposure_ns: None,
            iso: 0,
        }
    }

    #[test]
    fn uniforme_nul_damier_eleve() {
        let flat = vec![90u8; 64 * 48 * 4];
        assert_eq!(sharpness(&view(&flat, 64, 48)), 0.0);
        let mut checker = Vec::new();
        for y in 0..48 {
            for x in 0..64 {
                let v = if (x / 4 + y / 4) % 2 == 0 { 0 } else { 255 };
                checker.extend_from_slice(&[v, v, v, 255]);
            }
        }
        assert!(sharpness(&view(&checker, 64, 48)) > 1000.0);
    }

    #[test]
    fn rotation_entre_quaternions() {
        let a = Pose {
            p: [0.0; 3],
            q: [0.0, 0.0, 0.0, 1.0],
        };
        let half = 0.3f64 / 2.0;
        let b = Pose {
            p: [0.3, 0.4, 0.0],
            q: [0.0, half.sin(), 0.0, half.cos()],
        };
        let (t, r) = motion(&a, &b);
        assert!((t - 0.5).abs() < 1e-12);
        assert!((r - 0.3).abs() < 1e-9);
        // q et -q sont la même rotation.
        let c = Pose {
            p: [0.0; 3],
            q: [0.0, 0.0, 0.0, -1.0],
        };
        assert!(motion(&a, &c).1 < 1e-9);
    }
}
