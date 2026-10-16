#ifndef MOTE_H
#define MOTE_H

/* Généré par cbindgen depuis core/mote-capi (build.rs). Ne pas modifier : changer le Rust et reconstruire. */

#include <stdint.h>

// Version de l'ABI : `mote_config.abi_version` doit la porter.
#define MOTE_ABI_VERSION 1

// `mote_config.codec`.
#define MOTE_CODEC_JPEG 1

#define MOTE_CODEC_RAW_RGBA 2

// `mote_config.flags` : désactive la sélection.
#define MOTE_FLAG_RECORD_ALL (1 << 0)

typedef enum mote_status {
  MOTE_OK = 0,
  MOTE_ERR_INVALID_ARG = 1,
  // fichier local
  MOTE_ERR_IO = 2,
  // file d'encodage pleine, paire perdue
  MOTE_ERR_BUSY = 3,
  // appel hors séquence (ex. push avant start)
  MOTE_ERR_STATE = 4,
  MOTE_ERR_INTERNAL = 5,
} mote_status;

// Contexte d'une session, opaque pour l'hôte.
typedef struct mote_ctx mote_ctx;

typedef struct mote_config {
  uint32_t struct_size;
  // MOTE_ABI_VERSION
  uint32_t abi_version;
  // obligatoire (ADR-012)
  const char *local_dir;
  // "hôte:port", NULL = pas de flux live
  const char *server_addr;
  // jeton partagé, requis si server_addr
  const char *auth_token;
  // appareil, versions, espace de tracking
  const char *session_info_json;
  // MOTE_CODEC_*
  uint32_t codec;
  // 0 = défaut (90)
  uint32_t jpeg_quality;
  float kf_min_translation_m;
  float kf_min_rotation_rad;
  float kf_min_sharpness;
  // écart gauche/droite maximal accepté
  int64_t pair_max_dt_ns;
  // MOTE_FLAG_*
  uint32_t flags;
  // borne de la file live en octets ; 0 = 64 Mio
  uint64_t live_queue_bytes;
  // délai de connexion ; 0 = 3000 ms
  uint32_t connect_timeout_ms;
  // premier délai de reconnexion, doublé à chaque échec ; 0 = 500 ms
  uint32_t reconnect_min_ms;
  // délai de reconnexion maximal ; 0 = 5000 ms
  uint32_t reconnect_max_ms;
  // regroupement des demandes de rattrapage ; 0 = 500 ms
  uint32_t resend_batch_ms;
} mote_config;

// q = x,y,z,w
typedef struct mote_pose {
  double p[3];
  double q[4];
} mote_pose;

typedef struct mote_intrinsics {
  uint32_t struct_size;
  // 0 gauche, 1 droite
  uint32_t camera;
  uint32_t width;
  uint32_t height;
  double fx;
  double fy;
  double cx;
  double cy;
  // DistortionModel
  uint32_t model;
  const double *dist;
  uint32_t dist_len;
  uint32_t has_extrinsics;
  uint32_t convention;
  struct mote_pose hmd_from_camera;
} mote_intrinsics;

typedef struct mote_frame {
  uint32_t struct_size;
  // horloge mote
  int64_t t_ns;
  int64_t src_time_ns;
  // TimeDomain
  uint32_t src_domain;
  uint32_t width;
  uint32_t height;
  uint32_t stride;
  // RGBA8888
  const void *rgba;
  uint32_t has_pose;
  // PoseConvention
  uint32_t convention;
  struct mote_pose world_from_camera;
  uint32_t has_exposure;
  int64_t exposure_ns;
  uint32_t iso;
} mote_frame;

typedef struct mote_depth {
  uint32_t struct_size;
  // 0 gauche, 1 droite
  uint32_t eye;
  int64_t t_ns;
  int64_t src_time_ns;
  uint32_t src_domain;
  uint32_t width;
  uint32_t height;
  // DepthEncoding
  uint32_t encoding;
  const void *data;
  uint64_t data_len;
  uint32_t convention;
  struct mote_pose world_from_depth;
  // tangentes
  float fov_l;
  float fov_r;
  float fov_t;
  float fov_d;
  // far_z peut valoir +infini
  float near_z;
  float far_z;
  float min_depth;
  float max_depth;
} mote_depth;

typedef struct mote_stats {
  uint32_t struct_size;
  uint64_t pairs_pushed;
  uint64_t pairs_kept;
  uint64_t pairs_dropped;
  uint64_t bytes_written;
  uint64_t bytes_sent;
  float net_mbps;
  float encode_ms_avg;
  float live_queue_fill;
  uint32_t net_connected;
} mote_stats;

typedef struct mote_event {
  uint32_t struct_size;
  int64_t t_ns;
  // EventType
  uint32_t type;
  char detail[128];
} mote_event;

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

// Horloge mote (CLOCK_MONOTONIC), utilisable avant mote_create.
int64_t mote_now_ns(void);

enum mote_status mote_create(const struct mote_config *cfg, struct mote_ctx **out);

enum mote_status mote_start(struct mote_ctx *ctx);

// vide les files, écrit SessionEnd, ferme le fichier
enum mote_status mote_stop(struct mote_ctx *ctx);

// Arrête la session si elle tourne et libère le contexte. NULL est accepté.
void mote_destroy(struct mote_ctx *ctx);

enum mote_status mote_set_intrinsics(struct mote_ctx *ctx, const struct mote_intrinsics *intr);

enum mote_status mote_push_pair(struct mote_ctx *ctx,
                                const struct mote_frame *left,
                                const struct mote_frame *right,
                                uint32_t *out_kept);

enum mote_status mote_push_hmd_pose(struct mote_ctx *ctx,
                                    int64_t t_ns,
                                    int64_t src_time_ns,
                                    uint32_t src_domain,
                                    uint32_t convention,
                                    const struct mote_pose *world_from_hmd,
                                    uint32_t predicted);

enum mote_status mote_push_depth(struct mote_ctx *ctx, const struct mote_depth *depth);

enum mote_status mote_push_event(struct mote_ctx *ctx, uint32_t type, const char *detail);

enum mote_status mote_get_stats(struct mote_ctx *ctx, struct mote_stats *out);

// Prochain événement émis par le core ; `*out_has_event` vaut 0 si la file est vide.
enum mote_status mote_poll_event(struct mote_ctx *ctx,
                                 struct mote_event *out,
                                 uint32_t *out_has_event);

#ifdef __cplusplus
}  // extern "C"
#endif  // __cplusplus

#endif  /* MOTE_H */
