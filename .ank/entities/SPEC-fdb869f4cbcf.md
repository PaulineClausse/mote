---
id: SPEC-fdb869f4cbcf
type: spec
slug: api-c-du-core-mote-h
title: API C du core (mote.h)
created: 2026-10-05T08:20:40Z
author: seanl@sean-laptop
status: proposed
scope:
  - core/mote-capi/**
  - hosts/unity/**
references: [ADR-7a169c5d5e26]
schema: 4
version: 1
---

Principes : handles opaques ; structures plates commençant par `struct_size` ; aucune structure C++ à la frontière ; aucun callback vers l'hôte ; état et événements récupérés par polling ; les buffers passés aux fonctions `mote_push_*` ne sont lus que pendant l'appel (le core copie ce qu'il conserve) ; toutes les fonctions sont appelables depuis n'importe quel thread.

```c
#include <stdint.h>

#define MOTE_ABI_VERSION 1

typedef struct mote_ctx mote_ctx;

typedef enum {
  MOTE_OK = 0,
  MOTE_ERR_INVALID_ARG = 1,
  MOTE_ERR_IO = 2,          // fichier local
  MOTE_ERR_BUSY = 3,        // file d'encodage pleine, paire perdue
  MOTE_ERR_STATE = 4,       // appel hors séquence (ex. push avant start)
  MOTE_ERR_INTERNAL = 5
} mote_status;

enum { MOTE_CODEC_JPEG = 1, MOTE_CODEC_RAW_RGBA = 2 };
enum { MOTE_FLAG_RECORD_ALL = 1u << 0 };   // désactive la sélection

typedef struct {
  uint32_t struct_size;
  uint32_t abi_version;          // MOTE_ABI_VERSION
  const char* local_dir;         // obligatoire (ADR-012)
  const char* server_addr;       // "hôte:port", NULL = pas de flux live
  const char* auth_token;        // jeton partagé, requis si server_addr
  const char* session_info_json; // appareil, versions, espace de tracking
  uint32_t codec;                // MOTE_CODEC_*
  uint32_t jpeg_quality;         // 0 = défaut (90)
  float kf_min_translation_m;
  float kf_min_rotation_rad;
  float kf_min_sharpness;
  int64_t pair_max_dt_ns;        // écart gauche/droite maximal accepté
  uint32_t flags;                // MOTE_FLAG_*
} mote_config;

typedef struct { double p[3]; double q[4]; } mote_pose;   // q = x,y,z,w

typedef struct {
  uint32_t struct_size;
  int64_t t_ns;                  // horloge mote
  int64_t src_time_ns;
  uint32_t src_domain;           // TimeDomain
  uint32_t width, height, stride;
  const void* rgba;              // RGBA8888
  uint32_t has_pose;
  uint32_t convention;           // PoseConvention
  mote_pose world_from_camera;
  uint32_t has_exposure;
  int64_t exposure_ns;
  uint32_t iso;
} mote_frame;

typedef struct {
  uint32_t struct_size;
  uint32_t camera;               // 0 gauche, 1 droite
  uint32_t width, height;
  double fx, fy, cx, cy;
  uint32_t model;                // DistortionModel
  const double* dist; uint32_t dist_len;
  uint32_t has_extrinsics;
  uint32_t convention;
  mote_pose hmd_from_camera;
} mote_intrinsics;

typedef struct {
  uint32_t struct_size;
  uint32_t eye;                  // 0 gauche, 1 droite
  int64_t t_ns;
  int64_t src_time_ns;
  uint32_t src_domain;
  uint32_t width, height;
  uint32_t encoding;             // DepthEncoding
  const void* data; uint64_t data_len;
  uint32_t convention;
  mote_pose world_from_depth;
  float fov_l, fov_r, fov_t, fov_d;   // tangentes
  float near_z, far_z;                // far_z peut valoir +infini
  float min_depth, max_depth;
} mote_depth;

typedef struct {
  uint32_t struct_size;
  uint64_t pairs_pushed, pairs_kept, pairs_dropped;
  uint64_t bytes_written, bytes_sent;
  float net_mbps, encode_ms_avg, live_queue_fill;
  uint32_t net_connected;
} mote_stats;

typedef struct {
  uint32_t struct_size;
  int64_t t_ns;
  uint32_t type;                 // EventType
  char detail[128];
} mote_event;

// Horloge mote (CLOCK_MONOTONIC), utilisable avant mote_create.
int64_t     mote_now_ns(void);

mote_status mote_create(const mote_config* cfg, mote_ctx** out);
mote_status mote_start(mote_ctx*);
mote_status mote_stop(mote_ctx*);     // vide les files, écrit SessionEnd, ferme le fichier
void        mote_destroy(mote_ctx*);

// L'hôte pousse tout ce qu'il acquiert.
mote_status mote_set_intrinsics(mote_ctx*, const mote_intrinsics*);
mote_status mote_push_pair(mote_ctx*, const mote_frame* left,
                           const mote_frame* right, uint32_t* out_kept);
mote_status mote_push_hmd_pose(mote_ctx*, int64_t t_ns, int64_t src_time_ns,
                               uint32_t src_domain, uint32_t convention,
                               const mote_pose* world_from_hmd, uint32_t predicted);
mote_status mote_push_depth(mote_ctx*, const mote_depth*);
mote_status mote_push_event(mote_ctx*, uint32_t type, const char* detail);

// Supervision par polling.
mote_status mote_get_stats(mote_ctx*, mote_stats* out);
mote_status mote_poll_event(mote_ctx*, mote_event* out, uint32_t* out_has_event);
```

Règles complémentaires :
- `mote_push_pair` calcule la sélection de façon synchrone sur une version sous-échantillonnée (coût faible), puis copie la paire dans la file d'encodage uniquement si elle est retenue. `out_kept` permet à l'hôte de n'associer la profondeur et la couverture qu'aux paires retenues.
- L'appariement gauche/droite est fait par l'hôte (timestamp le plus proche, comme SRC-1 `[SOURCE]`). Le core rejette une paire dont l'écart dépasse `pair_max_dt_ns` et émet `PAIR_REJECTED_UNSYNC`.
- Le wrapper Unity appelle `mote_push_pair` et `mote_push_depth` hors du thread principal quand les données le permettent, pour ne pas allonger la frame de rendu.
- ABI : `abi_version` et `struct_size` ; ajout de champs en fin de structure uniquement.
