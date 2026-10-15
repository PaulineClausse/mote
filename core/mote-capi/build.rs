// Génère include/mote.h depuis les fonctions extern "C" de la crate (cbindgen). Le header est versionné : la CI
// vérifie qu'il ne diffère pas de ce que produit le build.
fn main() {
    let dir = std::env::var("CARGO_MANIFEST_DIR").unwrap();
    println!("cargo:rerun-if-changed=src");
    println!("cargo:rerun-if-changed=cbindgen.toml");
    let cfg = cbindgen::Config::from_file(format!("{dir}/cbindgen.toml")).expect("cbindgen.toml");
    cbindgen::Builder::new()
        .with_crate(&dir)
        .with_config(cfg)
        .generate()
        .expect("génération de mote.h")
        .write_to_file(format!("{dir}/include/mote.h"));
}
