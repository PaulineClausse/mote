/* Critère de WP-03 (TASK-85d8) vu d'un hôte C : mote.h expose chaque fonction et chaque champ de SPEC-fdb8 (les
 * initialiseurs nommés ne compilent pas s'il en manque un), et la séquence complète d'une session réussit.
 * Lancé par la CI après le build hôte. Usage : api <répertoire de session> */
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "mote.h"

#define CHECK(expr, want)                                                              \
    do {                                                                               \
        mote_status got_ = (expr);                                                     \
        if (got_ != (want)) {                                                          \
            fprintf(stderr, "api: %s a renvoyé %d, attendu %d\n", #expr, got_, want);  \
            return 1;                                                                  \
        }                                                                              \
    } while (0)

enum { W = 8, H = 4 };

int main(int argc, char** argv) {
    const char* dir = argc > 1 ? argv[1] : "mote-api-c";
    mote_config cfg = {
        .struct_size = sizeof(mote_config),
        .abi_version = MOTE_ABI_VERSION,
        .local_dir = dir,
        .server_addr = NULL,
        .auth_token = NULL,
        .session_info_json = "{}",
        .codec = MOTE_CODEC_JPEG,
        .jpeg_quality = 0,
        .kf_min_translation_m = 0.05f,
        .kf_min_rotation_rad = 0.1f,
        .kf_min_sharpness = 0.0f,
        .pair_max_dt_ns = 5000000,
        .flags = MOTE_FLAG_RECORD_ALL,
    };
    mote_ctx* ctx = NULL;

    cfg.local_dir = NULL;
    CHECK(mote_create(&cfg, &ctx), MOTE_ERR_INVALID_ARG);
    cfg.local_dir = dir;
    CHECK(mote_create(&cfg, &ctx), MOTE_OK);

    mote_pose pose = {.p = {0.0, 1.6, 0.0}, .q = {0.0, 0.0, 0.0, 1.0}};
    static uint8_t px[W * H * 4];
    int64_t t = mote_now_ns();
    mote_frame left = {
        .struct_size = sizeof(mote_frame),
        .t_ns = t,
        .src_time_ns = t / 1000,
        .src_domain = 5,
        .width = W,
        .height = H,
        .stride = W * 4,
        .rgba = px,
        .has_pose = 1,
        .convention = 1,
        .world_from_camera = pose,
        .has_exposure = 1,
        .exposure_ns = 8000000,
        .iso = 400,
    };
    mote_frame right = left;
    right.t_ns = t + 1000000;
    uint32_t kept = 7;

    CHECK(mote_push_pair(ctx, &left, &right, &kept), MOTE_ERR_STATE);
    CHECK(mote_start(ctx), MOTE_OK);

    double dist[4] = {0.1, -0.05, 0.0, 0.0};
    mote_intrinsics intr = {
        .struct_size = sizeof(mote_intrinsics),
        .camera = 0,
        .width = W,
        .height = H,
        .fx = 5.0,
        .fy = 5.0,
        .cx = 4.0,
        .cy = 2.0,
        .model = 2,
        .dist = dist,
        .dist_len = 4,
        .has_extrinsics = 1,
        .convention = 1,
        .hmd_from_camera = pose,
    };
    CHECK(mote_set_intrinsics(ctx, &intr), MOTE_OK);
    CHECK(mote_push_pair(ctx, &left, &right, &kept), MOTE_OK);
    if (kept != 1) {
        fprintf(stderr, "api: paire non retenue\n");
        return 1;
    }
    CHECK(mote_push_hmd_pose(ctx, t, t / 1000, 5, 1, &pose, 0), MOTE_OK);

    static float depth_px[4 * 4];
    mote_depth depth = {
        .struct_size = sizeof(mote_depth),
        .eye = 0,
        .t_ns = t,
        .src_time_ns = t,
        .src_domain = 3,
        .width = 4,
        .height = 4,
        .encoding = 1,
        .data = depth_px,
        .data_len = sizeof(depth_px),
        .convention = 2,
        .world_from_depth = pose,
        .fov_l = 1.0f,
        .fov_r = 1.0f,
        .fov_t = 1.0f,
        .fov_d = 1.0f,
        .near_z = 0.1f,
        .far_z = INFINITY,
        .min_depth = 0.0f,
        .max_depth = 1.0f,
    };
    CHECK(mote_push_depth(ctx, &depth), MOTE_OK);
    CHECK(mote_push_event(ctx, 1, "perte de tracking"), MOTE_OK);

    /* Paire désynchronisée : rejetée sans erreur, signalée par un événement. */
    right.t_ns = t + 50000000;
    CHECK(mote_push_pair(ctx, &left, &right, &kept), MOTE_OK);
    mote_event ev = {.struct_size = sizeof(mote_event)};
    uint32_t has = 0;
    CHECK(mote_poll_event(ctx, &ev, &has), MOTE_OK);
    if (kept != 0 || has != 1 || ev.type != 5 || ev.t_ns <= 0 || strlen(ev.detail) == 0) {
        fprintf(stderr, "api: rejet de paire désynchronisée non signalé (kept=%u has=%u type=%u)\n", kept, has,
                ev.type);
        return 1;
    }

    CHECK(mote_stop(ctx), MOTE_OK);
    CHECK(mote_stop(ctx), MOTE_ERR_STATE);
    mote_stats st = {.struct_size = sizeof(mote_stats)};
    CHECK(mote_get_stats(ctx, &st), MOTE_OK);
    if (st.pairs_pushed != 2 || st.pairs_kept != 1 || st.pairs_dropped != 0) {
        fprintf(stderr, "api: stats inattendues (pushed=%llu kept=%llu dropped=%llu)\n",
                (unsigned long long)st.pairs_pushed, (unsigned long long)st.pairs_kept,
                (unsigned long long)st.pairs_dropped);
        return 1;
    }
    printf("api: ok (bytes_written=%llu bytes_sent=%llu net=%u %.1f Mb/s encode=%.2f ms live=%.2f)\n",
           (unsigned long long)st.bytes_written, (unsigned long long)st.bytes_sent, st.net_connected, st.net_mbps,
           st.encode_ms_avg, st.live_queue_fill);
    mote_destroy(ctx);
    mote_destroy(NULL);
    (void)MOTE_CODEC_RAW_RGBA;
    (void)MOTE_ERR_IO;
    (void)MOTE_ERR_BUSY;
    (void)MOTE_ERR_INTERNAL;
    return 0;
}
