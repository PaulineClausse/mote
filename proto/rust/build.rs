// Génère les types Rust de mote.v1 dans OUT_DIR. protox remplace protoc : rien à installer en plus de cargo.
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let proto = "../mote/v1/mote.proto";
    println!("cargo:rerun-if-changed={proto}");
    let fds = protox::compile([proto], [".."])?;
    prost_build::Config::new().compile_fds(fds)?;
    Ok(())
}
