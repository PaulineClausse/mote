# mote-codec

Encodage JPEG des images retenues par libjpeg-turbo (ADR-86d6), via la crate `turbojpeg` qui en compile les sources
avec CMake. Chrominance 4:2:0, qualité de `mote_config.jpeg_quality` (90 par défaut). Le core encode la gauche et
la droite d'une paire en parallèle (`JpegEncoder`, dans `mote-core`).

Le critère de WP-04 est testé de bout en bout dans `mote-capi/tests/jpeg.rs` : paire 1280x1280 poussée par l'API C,
JPEG relus dans le fichier de session, PSNR à q90 au-dessus de 35 dB ; `RAW_RGBA` restitue les octets de la source.
