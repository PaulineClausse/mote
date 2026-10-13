// Types mote.v1 et FileDescriptorSet (schéma des canaux MCAP), depuis proto/mote/v1/mote.proto, sans protoc.
use prost::Message;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let root = "../../../../proto";
    let proto = format!("{root}/mote/v1/mote.proto");
    println!("cargo:rerun-if-changed={proto}");
    let fds = protox::compile([&proto], [root])?;
    let out = std::path::PathBuf::from(std::env::var("OUT_DIR")?);
    std::fs::write(out.join("mote_v1.fds"), fds.encode_to_vec())?;
    prost_build::Config::new().compile_fds(fds)?;
    Ok(())
}
