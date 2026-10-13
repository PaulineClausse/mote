from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PoseConvention(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    POSE_CONVENTION_UNSPECIFIED: _ClassVar[PoseConvention]
    UNITY: _ClassVar[PoseConvention]
    OPENXR: _ClassVar[PoseConvention]

class TimeDomain(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TIME_DOMAIN_UNSPECIFIED: _ClassVar[TimeDomain]
    MONOTONIC: _ClassVar[TimeDomain]
    BOOTTIME: _ClassVar[TimeDomain]
    XR_RUNTIME: _ClassVar[TimeDomain]
    UNKNOWN_DOMAIN: _ClassVar[TimeDomain]
    UNIX: _ClassVar[TimeDomain]

class ImageCodec(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IMAGE_CODEC_UNSPECIFIED: _ClassVar[ImageCodec]
    JPEG: _ClassVar[ImageCodec]
    RAW_RGBA: _ClassVar[ImageCodec]

class DistortionModel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DISTORTION_UNSPECIFIED: _ClassVar[DistortionModel]
    PINHOLE: _ClassVar[DistortionModel]
    OPENCV: _ClassVar[DistortionModel]

class DepthEncoding(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DEPTH_ENCODING_UNSPECIFIED: _ClassVar[DepthEncoding]
    F32_RAW: _ClassVar[DepthEncoding]
    U16_MM: _ClassVar[DepthEncoding]

class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_TYPE_UNSPECIFIED: _ClassVar[EventType]
    TRACKING_LOST: _ClassVar[EventType]
    TRACKING_RECOVERED: _ClassVar[EventType]
    RECENTER: _ClassVar[EventType]
    PAIR_DROPPED_BUSY: _ClassVar[EventType]
    PAIR_REJECTED_UNSYNC: _ClassVar[EventType]
    LIVE_DROPPED: _ClassVar[EventType]
    NET_DISCONNECTED: _ClassVar[EventType]
    NET_CONNECTED: _ClassVar[EventType]
POSE_CONVENTION_UNSPECIFIED: PoseConvention
UNITY: PoseConvention
OPENXR: PoseConvention
TIME_DOMAIN_UNSPECIFIED: TimeDomain
MONOTONIC: TimeDomain
BOOTTIME: TimeDomain
XR_RUNTIME: TimeDomain
UNKNOWN_DOMAIN: TimeDomain
UNIX: TimeDomain
IMAGE_CODEC_UNSPECIFIED: ImageCodec
JPEG: ImageCodec
RAW_RGBA: ImageCodec
DISTORTION_UNSPECIFIED: DistortionModel
PINHOLE: DistortionModel
OPENCV: DistortionModel
DEPTH_ENCODING_UNSPECIFIED: DepthEncoding
F32_RAW: DepthEncoding
U16_MM: DepthEncoding
EVENT_TYPE_UNSPECIFIED: EventType
TRACKING_LOST: EventType
TRACKING_RECOVERED: EventType
RECENTER: EventType
PAIR_DROPPED_BUSY: EventType
PAIR_REJECTED_UNSYNC: EventType
LIVE_DROPPED: EventType
NET_DISCONNECTED: EventType
NET_CONNECTED: EventType

class Pose3(_message.Message):
    __slots__ = ("px", "py", "pz", "qx", "qy", "qz", "qw")
    PX_FIELD_NUMBER: _ClassVar[int]
    PY_FIELD_NUMBER: _ClassVar[int]
    PZ_FIELD_NUMBER: _ClassVar[int]
    QX_FIELD_NUMBER: _ClassVar[int]
    QY_FIELD_NUMBER: _ClassVar[int]
    QZ_FIELD_NUMBER: _ClassVar[int]
    QW_FIELD_NUMBER: _ClassVar[int]
    px: float
    py: float
    pz: float
    qx: float
    qy: float
    qz: float
    qw: float
    def __init__(self, px: _Optional[float] = ..., py: _Optional[float] = ..., pz: _Optional[float] = ..., qx: _Optional[float] = ..., qy: _Optional[float] = ..., qz: _Optional[float] = ..., qw: _Optional[float] = ...) -> None: ...

class PoseSample(_message.Message):
    __slots__ = ("t_ns", "src_time_ns", "src_domain", "convention", "world_from_hmd", "predicted")
    T_NS_FIELD_NUMBER: _ClassVar[int]
    SRC_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    SRC_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    CONVENTION_FIELD_NUMBER: _ClassVar[int]
    WORLD_FROM_HMD_FIELD_NUMBER: _ClassVar[int]
    PREDICTED_FIELD_NUMBER: _ClassVar[int]
    t_ns: int
    src_time_ns: int
    src_domain: TimeDomain
    convention: PoseConvention
    world_from_hmd: Pose3
    predicted: bool
    def __init__(self, t_ns: _Optional[int] = ..., src_time_ns: _Optional[int] = ..., src_domain: _Optional[_Union[TimeDomain, str]] = ..., convention: _Optional[_Union[PoseConvention, str]] = ..., world_from_hmd: _Optional[_Union[Pose3, _Mapping]] = ..., predicted: _Optional[bool] = ...) -> None: ...

class ImageFrame(_message.Message):
    __slots__ = ("pair_id", "t_ns", "src_time_ns", "src_domain", "width", "height", "codec", "data", "convention", "world_from_camera", "exposure_ns", "iso", "blur_score")
    PAIR_ID_FIELD_NUMBER: _ClassVar[int]
    T_NS_FIELD_NUMBER: _ClassVar[int]
    SRC_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    SRC_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    CODEC_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CONVENTION_FIELD_NUMBER: _ClassVar[int]
    WORLD_FROM_CAMERA_FIELD_NUMBER: _ClassVar[int]
    EXPOSURE_NS_FIELD_NUMBER: _ClassVar[int]
    ISO_FIELD_NUMBER: _ClassVar[int]
    BLUR_SCORE_FIELD_NUMBER: _ClassVar[int]
    pair_id: int
    t_ns: int
    src_time_ns: int
    src_domain: TimeDomain
    width: int
    height: int
    codec: ImageCodec
    data: bytes
    convention: PoseConvention
    world_from_camera: Pose3
    exposure_ns: int
    iso: int
    blur_score: float
    def __init__(self, pair_id: _Optional[int] = ..., t_ns: _Optional[int] = ..., src_time_ns: _Optional[int] = ..., src_domain: _Optional[_Union[TimeDomain, str]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., codec: _Optional[_Union[ImageCodec, str]] = ..., data: _Optional[bytes] = ..., convention: _Optional[_Union[PoseConvention, str]] = ..., world_from_camera: _Optional[_Union[Pose3, _Mapping]] = ..., exposure_ns: _Optional[int] = ..., iso: _Optional[int] = ..., blur_score: _Optional[float] = ...) -> None: ...

class CameraIntrinsics(_message.Message):
    __slots__ = ("width", "height", "fx", "fy", "cx", "cy", "model", "dist", "convention", "hmd_from_camera")
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FX_FIELD_NUMBER: _ClassVar[int]
    FY_FIELD_NUMBER: _ClassVar[int]
    CX_FIELD_NUMBER: _ClassVar[int]
    CY_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    DIST_FIELD_NUMBER: _ClassVar[int]
    CONVENTION_FIELD_NUMBER: _ClassVar[int]
    HMD_FROM_CAMERA_FIELD_NUMBER: _ClassVar[int]
    width: int
    height: int
    fx: float
    fy: float
    cx: float
    cy: float
    model: DistortionModel
    dist: _containers.RepeatedScalarFieldContainer[float]
    convention: PoseConvention
    hmd_from_camera: Pose3
    def __init__(self, width: _Optional[int] = ..., height: _Optional[int] = ..., fx: _Optional[float] = ..., fy: _Optional[float] = ..., cx: _Optional[float] = ..., cy: _Optional[float] = ..., model: _Optional[_Union[DistortionModel, str]] = ..., dist: _Optional[_Iterable[float]] = ..., convention: _Optional[_Union[PoseConvention, str]] = ..., hmd_from_camera: _Optional[_Union[Pose3, _Mapping]] = ...) -> None: ...

class DepthFrame(_message.Message):
    __slots__ = ("t_ns", "src_time_ns", "src_domain", "width", "height", "encoding", "data", "convention", "world_from_depth", "fov_left_tan", "fov_right_tan", "fov_top_tan", "fov_down_tan", "near_z", "far_z", "min_depth", "max_depth", "src_predicted_display_time_ns")
    T_NS_FIELD_NUMBER: _ClassVar[int]
    SRC_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    SRC_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CONVENTION_FIELD_NUMBER: _ClassVar[int]
    WORLD_FROM_DEPTH_FIELD_NUMBER: _ClassVar[int]
    FOV_LEFT_TAN_FIELD_NUMBER: _ClassVar[int]
    FOV_RIGHT_TAN_FIELD_NUMBER: _ClassVar[int]
    FOV_TOP_TAN_FIELD_NUMBER: _ClassVar[int]
    FOV_DOWN_TAN_FIELD_NUMBER: _ClassVar[int]
    NEAR_Z_FIELD_NUMBER: _ClassVar[int]
    FAR_Z_FIELD_NUMBER: _ClassVar[int]
    MIN_DEPTH_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    SRC_PREDICTED_DISPLAY_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    t_ns: int
    src_time_ns: int
    src_domain: TimeDomain
    width: int
    height: int
    encoding: DepthEncoding
    data: bytes
    convention: PoseConvention
    world_from_depth: Pose3
    fov_left_tan: float
    fov_right_tan: float
    fov_top_tan: float
    fov_down_tan: float
    near_z: float
    far_z: float
    min_depth: float
    max_depth: float
    src_predicted_display_time_ns: int
    def __init__(self, t_ns: _Optional[int] = ..., src_time_ns: _Optional[int] = ..., src_domain: _Optional[_Union[TimeDomain, str]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., encoding: _Optional[_Union[DepthEncoding, str]] = ..., data: _Optional[bytes] = ..., convention: _Optional[_Union[PoseConvention, str]] = ..., world_from_depth: _Optional[_Union[Pose3, _Mapping]] = ..., fov_left_tan: _Optional[float] = ..., fov_right_tan: _Optional[float] = ..., fov_top_tan: _Optional[float] = ..., fov_down_tan: _Optional[float] = ..., near_z: _Optional[float] = ..., far_z: _Optional[float] = ..., min_depth: _Optional[float] = ..., max_depth: _Optional[float] = ..., src_predicted_display_time_ns: _Optional[int] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("t_ns", "type", "detail")
    T_NS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    t_ns: int
    type: EventType
    detail: str
    def __init__(self, t_ns: _Optional[int] = ..., type: _Optional[_Union[EventType, str]] = ..., detail: _Optional[str] = ...) -> None: ...

class Stats(_message.Message):
    __slots__ = ("t_ns", "pairs_pushed", "pairs_kept", "pairs_dropped", "bytes_written", "bytes_sent", "net_mbps", "encode_ms_avg", "live_queue_fill")
    T_NS_FIELD_NUMBER: _ClassVar[int]
    PAIRS_PUSHED_FIELD_NUMBER: _ClassVar[int]
    PAIRS_KEPT_FIELD_NUMBER: _ClassVar[int]
    PAIRS_DROPPED_FIELD_NUMBER: _ClassVar[int]
    BYTES_WRITTEN_FIELD_NUMBER: _ClassVar[int]
    BYTES_SENT_FIELD_NUMBER: _ClassVar[int]
    NET_MBPS_FIELD_NUMBER: _ClassVar[int]
    ENCODE_MS_AVG_FIELD_NUMBER: _ClassVar[int]
    LIVE_QUEUE_FILL_FIELD_NUMBER: _ClassVar[int]
    t_ns: int
    pairs_pushed: int
    pairs_kept: int
    pairs_dropped: int
    bytes_written: int
    bytes_sent: int
    net_mbps: float
    encode_ms_avg: float
    live_queue_fill: float
    def __init__(self, t_ns: _Optional[int] = ..., pairs_pushed: _Optional[int] = ..., pairs_kept: _Optional[int] = ..., pairs_dropped: _Optional[int] = ..., bytes_written: _Optional[int] = ..., bytes_sent: _Optional[int] = ..., net_mbps: _Optional[float] = ..., encode_ms_avg: _Optional[float] = ..., live_queue_fill: _Optional[float] = ...) -> None: ...

class SessionInfo(_message.Message):
    __slots__ = ("schema_version", "session_id", "start_unix_ns", "start_t_ns", "device_model", "os_build", "sdk_versions", "host_kind", "core_version", "tracking_space", "config_json")
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    START_UNIX_NS_FIELD_NUMBER: _ClassVar[int]
    START_T_NS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_MODEL_FIELD_NUMBER: _ClassVar[int]
    OS_BUILD_FIELD_NUMBER: _ClassVar[int]
    SDK_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    HOST_KIND_FIELD_NUMBER: _ClassVar[int]
    CORE_VERSION_FIELD_NUMBER: _ClassVar[int]
    TRACKING_SPACE_FIELD_NUMBER: _ClassVar[int]
    CONFIG_JSON_FIELD_NUMBER: _ClassVar[int]
    schema_version: int
    session_id: str
    start_unix_ns: int
    start_t_ns: int
    device_model: str
    os_build: str
    sdk_versions: str
    host_kind: str
    core_version: str
    tracking_space: str
    config_json: str
    def __init__(self, schema_version: _Optional[int] = ..., session_id: _Optional[str] = ..., start_unix_ns: _Optional[int] = ..., start_t_ns: _Optional[int] = ..., device_model: _Optional[str] = ..., os_build: _Optional[str] = ..., sdk_versions: _Optional[str] = ..., host_kind: _Optional[str] = ..., core_version: _Optional[str] = ..., tracking_space: _Optional[str] = ..., config_json: _Optional[str] = ...) -> None: ...

class ChannelEnd(_message.Message):
    __slots__ = ("channel", "last_seq")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    LAST_SEQ_FIELD_NUMBER: _ClassVar[int]
    channel: str
    last_seq: int
    def __init__(self, channel: _Optional[str] = ..., last_seq: _Optional[int] = ...) -> None: ...

class SessionEnd(_message.Message):
    __slots__ = ("channels",)
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    channels: _containers.RepeatedCompositeFieldContainer[ChannelEnd]
    def __init__(self, channels: _Optional[_Iterable[_Union[ChannelEnd, _Mapping]]] = ...) -> None: ...

class Hello(_message.Message):
    __slots__ = ("session_id", "auth_token", "schema_version")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    auth_token: str
    schema_version: int
    def __init__(self, session_id: _Optional[str] = ..., auth_token: _Optional[str] = ..., schema_version: _Optional[int] = ...) -> None: ...

class Envelope(_message.Message):
    __slots__ = ("channel", "seq", "hello", "session_info", "image", "intrinsics", "pose", "depth", "event", "stats", "session_end")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    HELLO_FIELD_NUMBER: _ClassVar[int]
    SESSION_INFO_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    INTRINSICS_FIELD_NUMBER: _ClassVar[int]
    POSE_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    SESSION_END_FIELD_NUMBER: _ClassVar[int]
    channel: str
    seq: int
    hello: Hello
    session_info: SessionInfo
    image: ImageFrame
    intrinsics: CameraIntrinsics
    pose: PoseSample
    depth: DepthFrame
    event: Event
    stats: Stats
    session_end: SessionEnd
    def __init__(self, channel: _Optional[str] = ..., seq: _Optional[int] = ..., hello: _Optional[_Union[Hello, _Mapping]] = ..., session_info: _Optional[_Union[SessionInfo, _Mapping]] = ..., image: _Optional[_Union[ImageFrame, _Mapping]] = ..., intrinsics: _Optional[_Union[CameraIntrinsics, _Mapping]] = ..., pose: _Optional[_Union[PoseSample, _Mapping]] = ..., depth: _Optional[_Union[DepthFrame, _Mapping]] = ..., event: _Optional[_Union[Event, _Mapping]] = ..., stats: _Optional[_Union[Stats, _Mapping]] = ..., session_end: _Optional[_Union[SessionEnd, _Mapping]] = ...) -> None: ...

class ResendRequest(_message.Message):
    __slots__ = ("channel", "first_seq", "last_seq")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    FIRST_SEQ_FIELD_NUMBER: _ClassVar[int]
    LAST_SEQ_FIELD_NUMBER: _ClassVar[int]
    channel: str
    first_seq: int
    last_seq: int
    def __init__(self, channel: _Optional[str] = ..., first_seq: _Optional[int] = ..., last_seq: _Optional[int] = ...) -> None: ...

class Control(_message.Message):
    __slots__ = ("resend",)
    RESEND_FIELD_NUMBER: _ClassVar[int]
    resend: ResendRequest
    def __init__(self, resend: _Optional[_Union[ResendRequest, _Mapping]] = ...) -> None: ...
