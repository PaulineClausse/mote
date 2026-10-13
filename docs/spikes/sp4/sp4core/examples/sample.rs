//! Écrit une petite session MCAP avec le vrai chemin du core (copie, JPEG, MCAP), pour tester verify_mcap.py sur PC.
//!
//!   cargo run --release --example sample -- <dossier> [paires] [largeur] [hauteur]

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let dir = std::path::PathBuf::from(args.get(1).expect("usage : sample <dossier> [paires] [w] [h]"));
    let n: i64 = args.get(2).map(|s| s.parse().unwrap()).unwrap_or(20);
    let w: u32 = args.get(3).map(|s| s.parse().unwrap()).unwrap_or(320);
    let h: u32 = args.get(4).map(|s| s.parse().unwrap()).unwrap_or(320);
    let mut s = sp4core::Sp4::open(dir, 90, 2, 64).unwrap();
    for k in 0..n {
        let l = sp4core::synthetic_rgba(w, h, k as u32);
        let r = sp4core::synthetic_rgba(w, h, 1000 + k as u32);
        assert_eq!(s.push_pair(1_791_367_700_000_000_000 + k * 100_000_000, &l, &r, w, h, 0), sp4core::OK);
    }
    let path = s.close().unwrap();
    println!("{}", path.display());
    println!("{}", s.stats_json());
}
