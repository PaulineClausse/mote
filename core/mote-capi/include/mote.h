#ifndef MOTE_H
#define MOTE_H

/* Généré par cbindgen depuis core/mote-capi (build.rs). Ne pas modifier : changer le Rust et reconstruire. */

#include <stdint.h>

// Version de l'ABI : `mote_config.abi_version` doit la porter.
#define MOTE_ABI_VERSION 1

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

// Horloge mote (CLOCK_MONOTONIC), utilisable avant mote_create.
int64_t mote_now_ns(void);

#ifdef __cplusplus
}  // extern "C"
#endif  // __cplusplus

#endif  /* MOTE_H */
