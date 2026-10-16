// Embarque le FileDescriptorSet de mote.proto : c'est le schéma MCAP de chaque canal (encodage « protobuf »), ce
// qui rend le fichier décodable par un lecteur qui n'a pas le code généré.
use prost::Message;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let proto = "../../proto/mote/v1/mote.proto";
    println!("cargo:rerun-if-changed={proto}");
    let mut fds = protox::compile(["mote/v1/mote.proto"], ["../../proto"])?;
    for f in &mut fds.file {
        f.source_code_info = None;
    }
    let out = std::path::PathBuf::from(std::env::var("OUT_DIR")?).join("mote.fds");
    std::fs::write(out, fds.encode_to_vec())?;
    Ok(())
}
