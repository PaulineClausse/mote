//! File live bornée en octets (ADR-c36f, SPEC-9df2) : quand une trame ne tient pas, les images et cartes de
//! profondeur les plus anciennes sont retirées ; les autres canaux ne le sont jamais, quitte à dépasser la borne
//! (leur volume est négligeable). Les messages retirés restent dans le fichier local et se rattrapent.

use std::collections::VecDeque;

use crate::frame::droppable;

/// Une trame en attente d'émission.
#[derive(Clone, Debug, PartialEq)]
pub struct Item {
    pub channel: String,
    pub seq: u64,
    /// `Envelope` encodée.
    pub bytes: Vec<u8>,
}

impl Item {
    fn droppable(&self) -> bool {
        droppable(&self.channel)
    }
}

#[derive(Debug)]
pub struct LiveQueue {
    items: VecDeque<Item>,
    bytes: usize,
    capacity: usize,
}

impl LiveQueue {
    pub fn new(capacity: usize) -> Self {
        LiveQueue {
            items: VecDeque::new(),
            bytes: 0,
            capacity,
        }
    }

    /// Ajoute une trame ; renvoie les trames retirées pour lui faire de la place (ou elle-même si c'est la seule
    /// retirable), une par événement `LIVE_DROPPED`.
    pub fn push(&mut self, item: Item) -> Vec<Item> {
        let mut dropped = Vec::new();
        while self.bytes + item.bytes.len() > self.capacity {
            match self.items.iter().position(Item::droppable) {
                Some(i) => {
                    let old = self.items.remove(i).unwrap();
                    self.bytes -= old.bytes.len();
                    dropped.push(old);
                }
                None => break,
            }
        }
        if self.bytes + item.bytes.len() > self.capacity && item.droppable() {
            dropped.push(item);
        } else {
            self.bytes += item.bytes.len();
            self.items.push_back(item);
        }
        dropped
    }

    /// Remet en tête une trame dont l'envoi a échoué.
    pub fn push_front(&mut self, item: Item) {
        self.bytes += item.bytes.len();
        self.items.push_front(item);
    }

    pub fn pop(&mut self) -> Option<Item> {
        let item = self.items.pop_front()?;
        self.bytes -= item.bytes.len();
        Some(item)
    }

    pub fn is_empty(&self) -> bool {
        self.items.is_empty()
    }

    /// Remplissage, de 0 à 1 (au-delà si des messages non retirables dépassent la borne).
    pub fn fill(&self) -> f32 {
        if self.capacity == 0 {
            return 0.0;
        }
        self.bytes as f32 / self.capacity as f32
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn item(channel: &str, seq: u64, len: usize) -> Item {
        Item {
            channel: channel.into(),
            seq,
            bytes: vec![0; len],
        }
    }

    fn ids(items: &[Item]) -> Vec<(&str, u64)> {
        items.iter().map(|i| (i.channel.as_str(), i.seq)).collect()
    }

    #[test]
    fn retire_les_images_et_profondeurs_les_plus_anciennes() {
        let mut q = LiveQueue::new(100);
        assert!(q.push(item("/cam/left/frame", 0, 40)).is_empty());
        assert!(q.push(item("/pose/hmd", 0, 10)).is_empty());
        assert!(q.push(item("/depth/left", 0, 40)).is_empty());
        // 90 octets en file : une trame de 40 en impose le retrait du plus ancien retirable.
        let dropped = q.push(item("/cam/right/frame", 0, 40));
        assert_eq!(ids(&dropped), [("/cam/left/frame", 0)]);
        let rest: Vec<_> = std::iter::from_fn(|| q.pop()).collect();
        assert_eq!(
            ids(&rest),
            [
                ("/pose/hmd", 0),
                ("/depth/left", 0),
                ("/cam/right/frame", 0)
            ]
        );
    }

    #[test]
    fn ne_retire_jamais_les_autres_canaux() {
        let mut q = LiveQueue::new(50);
        for (k, c) in [
            "/session/info",
            "/cam/left/intrinsics",
            "/pose/hmd",
            "/events",
            "/stats",
            "/session/end",
        ]
        .iter()
        .enumerate()
        {
            assert!(q.push(item(c, k as u64, 30)).is_empty(), "{c}");
        }
        assert!(
            q.fill() > 1.0,
            "la borne est dépassée plutôt que de perdre un message non retirable"
        );
        // Une image qui ne tient pas, sans rien de retirable devant elle, est elle-même retirée.
        let dropped = q.push(item("/cam/left/frame", 9, 10));
        assert_eq!(ids(&dropped), [("/cam/left/frame", 9)]);
    }

    #[test]
    fn la_borne_est_un_reglage() {
        let mut big = LiveQueue::new(1000);
        let mut small = LiveQueue::new(100);
        for s in 0..5 {
            assert!(big.push(item("/depth/left", s, 150)).is_empty());
            let _ = small.push(item("/depth/left", s, 50));
        }
        assert_eq!(
            ids(&std::iter::from_fn(|| small.pop()).collect::<Vec<_>>()),
            [("/depth/left", 3), ("/depth/left", 4)]
        );
    }
}
