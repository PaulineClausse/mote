//! Encodage JPEG logiciel des images retenues, par libjpeg-turbo (ADR-86d6). Sur le casque, libjpeg-turbo est
//! compilé avec ses extensions NEON ; sur PC, avec SIMD seulement si nasm est présent.

use std::fmt;

use turbojpeg::{Compressor, Image, PixelFormat, Subsamp};

#[derive(Debug)]
pub enum Error {
    /// Le buffer ne fait pas `width * height * 4` octets, ou une dimension est nulle.
    Size,
    Turbo(turbojpeg::Error),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::Size => f.write_str("taille d'image incohérente"),
            Error::Turbo(e) => write!(f, "libjpeg-turbo : {e}"),
        }
    }
}

impl std::error::Error for Error {}

impl From<turbojpeg::Error> for Error {
    fn from(e: turbojpeg::Error) -> Self {
        Error::Turbo(e)
    }
}

/// Qualité par défaut quand l'hôte n'en donne pas (SPEC-fdb8).
pub const DEFAULT_QUALITY: u32 = 90;

/// Un encodeur JPEG réutilisable, pour un thread à la fois.
pub struct Jpeg {
    c: Compressor,
}

impl Jpeg {
    /// `quality` de 1 à 100. Sous-échantillonnage de la chrominance 4:2:0, le réglage courant des photos : la
    /// luminance, qui porte le détail utile au 3DGS, reste à pleine résolution.
    pub fn new(quality: u32) -> Result<Self, Error> {
        let mut c = Compressor::new()?;
        c.set_quality(quality.clamp(1, 100) as i32)?;
        c.set_subsamp(Subsamp::Sub2x2)?;
        Ok(Jpeg { c })
    }

    /// Encode une image RGBA8888 compacte (`width * 4` octets par ligne) ; l'alpha est ignoré.
    pub fn encode(&mut self, rgba: &[u8], width: u32, height: u32) -> Result<Vec<u8>, Error> {
        if width == 0 || height == 0 || rgba.len() != width as usize * height as usize * 4 {
            return Err(Error::Size);
        }
        let image = Image {
            pixels: rgba,
            width: width as usize,
            pitch: width as usize * 4,
            height: height as usize,
            format: PixelFormat::RGBA,
        };
        Ok(self.c.compress_to_vec(image)?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn produit_un_jpeg() {
        let px = vec![128u8; 16 * 8 * 4];
        let out = Jpeg::new(DEFAULT_QUALITY)
            .unwrap()
            .encode(&px, 16, 8)
            .unwrap();
        assert_eq!(&out[..2], &[0xFF, 0xD8], "marqueur SOI");
        assert_eq!(&out[out.len() - 2..], &[0xFF, 0xD9], "marqueur EOI");
    }

    #[test]
    fn taille_incoherente_refusee() {
        let px = vec![0u8; 10];
        assert!(Jpeg::new(90).unwrap().encode(&px, 16, 8).is_err());
    }
}
