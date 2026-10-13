//! Pousse des paires, ferme, relit le MCAP : chaque image est un ImageFrame JPEG décodable, les séquences sont
//! contiguës, /session/end donne le dernier seq de chaque canal, et la file pleine rend ERR_BUSY sans rien perdre
//! d'autre.

use std::collections::BTreeMap;

use prost::Message;
use sp4core::{synthetic_rgba, v1, Sp4, ERR_BUSY, OK};

fn read_mcap(path: &std::path::Path) -> BTreeMap<String, Vec<(u32, Vec<u8>)>> {
    let bytes = std::fs::read(path).unwrap();
    let mut out: BTreeMap<String, Vec<(u32, Vec<u8>)>> = BTreeMap::new();
    for m in mcap::MessageStream::new(&bytes).unwrap() {
        let m = m.unwrap();
        assert_eq!(m.channel.message_encoding, "protobuf");
        assert_eq!(m.channel.schema.as_ref().unwrap().encoding, "protobuf");
        out.entry(m.channel.topic.clone()).or_default().push((m.sequence, m.data.into_owned()));
    }
    out
}

#[test]
fn pairs_round_trip_through_mcap() {
    let dir = std::env::temp_dir().join(format!("sp4-test-{}", std::process::id()));
    let (w, h) = (128u32, 96u32);
    let mut s = Sp4::open(dir.clone(), 90, 2, 64).unwrap();
    let left = synthetic_rgba(w, h, 1);
    let right = synthetic_rgba(w, h, 2);
    for k in 0..10 {
        assert_eq!(s.push_pair(1_000 + k, &left, &right, w, h, 0), OK);
    }
    let path = s.close().unwrap();
    let stats = s.stats_json();
    assert!(stats.contains("\"pairs_encoded\":10") && stats.contains("\"pairs_dropped\":0"), "{stats}");

    let msgs = read_mcap(&path);
    for topic in ["/cam/left/frame", "/cam/right/frame"] {
        let v = &msgs[topic];
        assert_eq!(v.len(), 10, "{topic}");
        let mut seqs: Vec<u32> = v.iter().map(|(s, _)| *s).collect();
        seqs.sort();
        assert_eq!(seqs, (0..10).collect::<Vec<_>>(), "{topic}");
        for (_, data) in v {
            let f = v1::ImageFrame::decode(data.as_slice()).unwrap();
            assert_eq!((f.width, f.height, f.codec), (w, h, v1::ImageCodec::Jpeg as i32));
            let img = turbojpeg::decompress(&f.data, turbojpeg::PixelFormat::RGBA).unwrap();
            assert_eq!((img.width, img.height), (w as usize, h as usize));
        }
    }
    let info = v1::SessionInfo::decode(msgs["/session/info"][0].1.as_slice()).unwrap();
    assert!(info.config_json.contains("\"jpeg_quality\":90"), "{}", info.config_json);
    let end = v1::SessionEnd::decode(msgs["/session/end"][0].1.as_slice()).unwrap();
    assert_eq!(end.channels.iter().map(|c| c.last_seq).collect::<Vec<_>>(), vec![9, 9]);
    std::fs::remove_dir_all(dir).ok();
}

#[test]
fn full_queue_drops_the_pair_and_says_so() {
    let dir = std::env::temp_dir().join(format!("sp4-busy-{}", std::process::id()));
    let (w, h) = (1280u32, 1280u32);
    let mut s = Sp4::open(dir.clone(), 90, 1, 1).unwrap();
    let img = synthetic_rgba(w, h, 3);
    let codes: Vec<i32> = (0..8).map(|k| s.push_pair(k, &img, &img, w, h, 0)).collect();
    assert!(codes.contains(&ERR_BUSY), "{codes:?}");
    s.close().unwrap();
    let stats = s.stats_json();
    let dropped = codes.iter().filter(|&&c| c == ERR_BUSY).count();
    assert!(stats.contains(&format!("\"pairs_dropped\":{dropped}")), "{stats}");
    assert!(stats.contains(&format!("\"pairs_encoded\":{}", 8 - dropped)), "{stats}");
    std::fs::remove_dir_all(dir).ok();
}

#[test]
fn stride_is_honoured() {
    let dir = std::env::temp_dir().join(format!("sp4-stride-{}", std::process::id()));
    let (w, h, stride) = (16u32, 8u32, 16u32 * 4 + 12);
    let mut padded = vec![0u8; (stride * h) as usize];
    for y in 0..h as usize {
        for x in 0..w as usize {
            padded[y * stride as usize + x * 4..][..4].copy_from_slice(&[200, 10, 10, 255]);
        }
    }
    let mut s = Sp4::open(dir.clone(), 95, 1, 4).unwrap();
    assert_eq!(s.push_pair(0, &padded, &padded, w, h, stride), OK);
    let path = s.close().unwrap();
    let f = v1::ImageFrame::decode(read_mcap(&path)["/cam/left/frame"][0].1.as_slice()).unwrap();
    let img = turbojpeg::decompress(&f.data, turbojpeg::PixelFormat::RGBA).unwrap();
    let px = &img.pixels[(4 * w as usize + 8) * 4..][..3];
    assert!(px[0] > 180 && px[1] < 40 && px[2] < 40, "{px:?}");   // rouge partout, pas de marge recopiée
    std::fs::remove_dir_all(dir).ok();
}
