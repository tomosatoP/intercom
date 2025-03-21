"""libpulse

マイク(source)とスピーカー(sink)の音量コントロール

これは、PulseAudionの共有ライブラリィlibpulseをPython言語から利用するためのモジュール。
libpulseAPIにPython言語のctypesモジュール経由でアクセスする。
"""

from typing import Literal, Any, Callable
from enum import IntEnum, IntFlag, auto
from ctypes.util import find_library
import ctypes as CPA
import logging as LPA

#### libpulseAPI Macros

PA_CHANNELS_MAX = 32  # 本来は、32U


#### libpulseAPI用のロギング
logger = LPA.getLogger(__name__)
logger.setLevel(LPA.INFO)


#### libpulseAPI用のエラーハンドラ
class PAError(Exception):
    """libpulseエラーハンドラー

    戻り値によるエラーチェックの結果、エラーとなった場合に例外を発生させる
    """

    def __init__(self, *args):
        super().__init__(*args)

        logger.error(f"PAError: {args}")


def _errcheck(result: Any, libpulseapi: Callable, args: tuple) -> Any:
    """戻り値によるエラーチェック

    libpulseAPIの戻り値の型(C言語)によるエラーチェック方法
        void型: このエラーチェックの対象外
        int型: 負数の場合にエラー発生
        pointer型: Nullポインター(None)の場合にエラー発生

    :param Any result: エラーチェック対象の関数の戻り値
    :param Callable libpulseapi: エラーチェック対象の関数オブジェクト
    :param tuple args: 関数呼び出しに最初に渡された引数
    """

    if ((type(result) is int) and (result < 0)) or (result == None):
        raise PAError((libpulseapi, args))

    return result


#### libpulseAPI
# libpulse
_libpulse = CPA.CDLL(name=find_library(name="pulse"), use_errno=True)


# 共有ライブラリィの提供するAPI関数プロトタイプ
def _prototype(restype: Any, name: str, *params: tuple) -> Any:
    """共有ライブラリィの提供するAPIを返す

    ctypes.CFUNCTYPE関数のラッパーで、読み易さ重視です。

    :param Any restype: APIの戻り値
    :param str name: APIの名前
    :param tuple params: APIの引数タプル(type, flag, name[, default])のタプル
    :return Any: 共有ライブラリィの提供するAPIを返す。
    """

    if hasattr(_libpulse, name):
        argtypes: list = list([])
        paramflags: list = list([])

        for param in params:
            argtypes.append(param[0])
            paramflags.append(param[1:])

        func_spec = (name, _libpulse)

        return CPA.CFUNCTYPE(restype, *argtypes, use_errno=True)(
            func_spec, tuple(paramflags)
        )

    else:
        return None


#### libpulseAPI Enumerations


# pa_context_state_t
class PA_CONTEXT_STATE(IntEnum):
    UNCONNECTED = 0
    CONNECTING = auto()
    AUTHORIZING = auto()
    SETTING_NAME = auto()
    READY = auto()
    FAILED = auto()
    TERMINATED = auto()


# pa_operation_state_t
class PA_OPERATION_STATE(IntEnum):
    RUNNING = 0
    DONE = auto()
    CANCELLED = auto()


# pa_subscription_event_type_t
class PA_SUBSCRIPTION_EVENT(IntFlag):
    SINK = 0x0000
    SOURCE = 0x0001
    SINK_INPUT = 0x0002
    SOURCE_OUTPUT = 0x0003
    MODULE = 0x0004
    CLIENT = 0x0005
    SAMPLE_CACHE = 0x0006
    SERVER = 0x0007
    AUTOLOAD = 0x0008
    CARD = 0x0009
    FACILITY_MASK = 0x000F
    NEW = 0x0000
    CHANGE = 0x0010
    REMOVE = 0x0020
    TYPE_MASK = 0x0030


# pa_subscription_mask_t
class PA_SUBSCRIPTION_MASK(IntFlag):
    NULL = 0x0000
    SINK = 0x0001
    SOURCE = 0x0002
    SINK_INPUT = 0x0004
    SOURCE_OUTPUT = 0x0008
    MODULE = 0x0010
    CLIENT = 0x0020
    SAMPLE_CACHE = 0x0040
    SERVER = 0x0080
    AUTOLOAD = 0x0100
    CARD = 0x0200
    ALL = 0x02FF


#### libpulseAPI Data Structure


# pa_sample_sepc
class PA_SAMPLE_SPEC(CPA.Structure):
    _fields_ = [
        ("format", CPA.c_int),  # c_int <- pa_sample_format_t
        ("rate", CPA.c_uint32),
        ("channels", CPA.c_uint8),
    ]


# pa_channel_map
PA_CHANNEL_POSITIONS = CPA.c_int * PA_CHANNELS_MAX  # c_int <- pa_channel_position_t


class PA_CHANNEL_MAP(CPA.Structure):
    _fields_ = [("channels", CPA.c_uint8), ("map", PA_CHANNEL_POSITIONS)]


# pa_server_info
class PA_SERVER_INFO(CPA.Structure):
    _fields_ = [
        ("user_name", CPA.c_char_p),
        ("host_name", CPA.c_char_p),
        ("server_version", CPA.c_char_p),
        ("server_name", CPA.c_char_p),
        ("sample_spec", PA_SAMPLE_SPEC),
        ("default_sink_name", CPA.c_char_p),
        ("default_source_name", CPA.c_char_p),
        ("cookie", CPA.c_uint32),
        ("channel_map", PA_CHANNEL_MAP),
    ]


# pa_volume_t
PA_VOLUME_T = CPA.c_uint32

# pa_cvolume
PA_VOLUME_TS = PA_VOLUME_T * PA_CHANNELS_MAX


class PA_CVOLUME(CPA.Structure):
    _fields_ = [("channels", CPA.c_uint8), ("values", PA_VOLUME_TS)]


# pa_sink_port_info
class PA_SINK_PORT_INFO(CPA.Structure):
    _fields_ = [
        ("name", CPA.c_char_p),
        ("description", CPA.c_char_p),
        ("priority", CPA.c_uint32),
        ("available", CPA.c_int),
        ("availablity_group", CPA.c_char_p),
        ("type", CPA.c_uint32),
    ]


# pa_source_port_info
class PA_SOURCE_PORT_INFO(CPA.Structure):
    _fields_ = [
        ("name", CPA.c_char_p),
        ("description", CPA.c_char_p),
        ("priority", CPA.c_uint32),
        ("available", CPA.c_int),
        ("availablity_group", CPA.c_char_p),
        ("type", CPA.c_uint32),
    ]


# pa_format_info
class PA_FORMAT_INFO(CPA.Structure):
    _fields_ = [
        ("encoding", CPA.c_int),  # c_int <- typedef enum pa_encoding_t
        ("plist", CPA.c_void_p),
    ]  # c_void_p <- pa_proplist*


# pa_sink_info
PA_USEC_T = CPA.c_uint64


class PA_SINK_INFO(CPA.Structure):
    _fields_ = [
        ("name", CPA.c_char_p),
        ("index", CPA.c_uint32),
        ("description", CPA.c_char_p),
        ("sample_spec", PA_SAMPLE_SPEC),
        ("channel_map", PA_CHANNEL_MAP),
        ("owner_module", CPA.c_uint32),
        ("volume", PA_CVOLUME),
        ("mute", CPA.c_int),
        ("monitor_source", CPA.c_uint32),
        ("monitor_source_name", CPA.c_char_p),
        ("latency", PA_USEC_T),
        ("driver", CPA.c_char_p),
        ("flags", CPA.c_int),  # c_int <- pa_sink_flags_t
        ("proplist", CPA.c_void_p),  # c_void_p <- pa_proplist*
        ("configure_latency", PA_USEC_T),
        ("base_volume", PA_VOLUME_T),
        ("state", CPA.c_int),  # c_int <- typedef enum pa_sink_state_t
        ("n_volume_steps", CPA.c_uint32),
        ("card", CPA.c_uint32),
        ("n_ports", CPA.c_uint32),
        ("ports", CPA.POINTER(CPA.POINTER(PA_SINK_PORT_INFO))),
        ("active_port", CPA.POINTER(PA_SINK_PORT_INFO)),
        ("n_formats", CPA.c_uint8),
        ("formats", CPA.POINTER(CPA.POINTER(PA_FORMAT_INFO))),
    ]


# pa_source_info
class PA_SOURCE_INFO(CPA.Structure):
    _fields_ = [
        ("name", CPA.c_char_p),
        ("index", CPA.c_uint32),
        ("description", CPA.c_char_p),
        ("sample_spec", PA_SAMPLE_SPEC),
        ("channel_map", PA_CHANNEL_MAP),
        ("owner_module", CPA.c_uint32),
        ("volume", PA_CVOLUME),
        ("mute", CPA.c_int),
        ("monitor_of_sink", CPA.c_uint32),
        ("monitor_of_sink_name", CPA.c_char_p),
        ("latency", PA_USEC_T),
        ("driver", CPA.c_char_p),
        ("flags", CPA.c_int),
        ("proplist", CPA.c_void_p),
        ("configured_latency", PA_USEC_T),
        ("base_volume", PA_VOLUME_T),
        ("state", CPA.c_int),
        ("n_volume_steps", CPA.c_uint32),
        ("card", CPA.c_uint32),
        ("n_ports", CPA.c_uint32),
        ("ports", CPA.POINTER(CPA.POINTER(PA_SOURCE_PORT_INFO))),
        ("active_port", CPA.POINTER(PA_SOURCE_PORT_INFO)),
        ("n_formats", CPA.c_uint8),
        ("formats", CPA.POINTER(CPA.POINTER(PA_FORMAT_INFO))),
    ]


#### libpulseAPI mainloop
# mainloop内でさまざまな非同期処理の通知を処理する。

# 新しいmainloopオブジェクトを割り当て
pa_mainloop_new = _prototype(CPA.c_void_p, "pa_mainloop_new")
pa_mainloop_new.errcheck = _errcheck

# mainloopオブジェクトを解放
pa_mainloop_free = _prototype(None, "pa_mainloop_free", (CPA.c_void_p, 1, "mainloop"))

# mainloopを1回反復
pa_mainloop_iterate = _prototype(
    CPA.c_int,
    "pa_mainloop_iterate",
    (CPA.c_void_p, 1, "mainloop"),
    (CPA.c_int, 1, "block"),
    (CPA.POINTER(CPA.c_int), 1, "retval"),
)
pa_mainloop_iterate.errcheck = _errcheck

#### libpulseAPI context
# context(PulseAudioサーバーと接続できる基本オブジェクト)を経由して非同期処理を実行する。

# mainloopの抽象化レイヤーのvtableを返す
pa_mainloop_get_api = _prototype(
    CPA.c_void_p, "pa_mainloop_get_api", (CPA.c_void_p, 1, "mainloop")
)
pa_mainloop_get_api.errcheck = _errcheck

# mainloop API と名前を持つcontextのインスタンスを生成
pa_context_new = _prototype(
    CPA.c_void_p,
    "pa_context_new",
    (CPA.c_void_p, 1, "mainloop"),
    (CPA.c_char_p, 1, "name"),
)
pa_context_new.errcheck = _errcheck

# contextの参照カウンタを1つ減らす
pa_context_unref = _prototype(None, "pa_context_unref", (CPA.c_void_p, 1, "context"))

# 指定したサーバにcontextを接続
pa_context_connect = _prototype(
    CPA.c_int,
    "pa_context_connect",
    (CPA.c_void_p, 1, "context"),
    (CPA.c_char_p, 1, "server"),
    (CPA.c_void_p, 1, "flags"),
    (CPA.c_void_p, 1, "api"),
)
pa_context_connect.errcheck = _errcheck

# contextとサーバとの接続を直ちに終了
pa_context_disconnect = _prototype(
    None, "pa_context_disconnect", (CPA.c_void_p, 1, "context")
)

# 汎用の通知callbackのプロトタイプ
PA_CONTEXT_NOTIFY_CB_T = CPA.CFUNCTYPE(None, CPA.c_void_p, CPA.c_void_p)
"""汎用の通知callbackのプロトタイプ

pa_context_set_state_callback関数での利用を想定

:param pa_context *context: 対象のcontext
:param void *userdata: ****
"""

# 操作完了の汎用callbackのプロトタイプ
PA_CONTEXT_SUCCESS_CB_T = CPA.CFUNCTYPE(None, CPA.c_void_p, CPA.c_int, CPA.c_void_p)
"""操作完了の汎用callbackのプロトタイプ

:param pa_context *context: 対象のcontext
:param int success: 1の時に正常終了、0なら異常終了
:param void *userdata: ****
"""

# 汎用の通知callback関数を登録し、contextの状態が変化するたびに呼び出す
pa_context_set_state_callback = _prototype(
    None,
    "pa_context_set_state_callback",
    (CPA.c_void_p, 1, "context"),
    (PA_CONTEXT_NOTIFY_CB_T, 1, "callback"),
    (CPA.c_void_p, 1, "userdata"),
)

# 現在のcontextの状態をPA_CONTEXT_STATEタイプで返す
pa_context_get_state = _prototype(
    CPA.c_int, "pa_context_get_state", (CPA.c_void_p, 1, "context")
)
pa_context_get_state.errcheck = _errcheck

#### libpulseAPI operation
# 操作。非同期処理なので終了まではmainloopを反復(pa_mainloop_iterate関数)

# operationの状態PA_OPERATION_STATEを返す
pa_operation_get_state = _prototype(
    PA_OPERATION_STATE, "pa_operation_get_state", (CPA.c_void_p, 1, "operation")
)
pa_operation_get_state.errcheck = _errcheck

# 参照カウントを1減らす
pa_operation_unref = _prototype(
    None, "pa_operation_unref", (CPA.c_void_p, 1, "operation")
)


#### libpulseAPI introspect
# daemon(pulseaudio server service)の内部処理

#### libpulseAPI instrospect - server
# server処理

# pa_context_get_server_info() のcallbackプロトタイプ
PA_SERVER_INFO_CB_T = CPA.CFUNCTYPE(None, CPA.c_void_p, CPA.c_void_p, CPA.c_void_p)
"""pa_context_get_server_info() のcallbackプロトタイプ

:param pa_context *context: 対象のcontext
:param const pa_server_info_t *info: サーバー情報
:param void *userdata: ****
"""

# サーバーに関する情報を取得
pa_context_get_server_info = _prototype(
    CPA.c_void_p,
    "pa_context_get_server_info",
    (CPA.c_void_p, 1, "context"),
    (PA_SERVER_INFO_CB_T, 1, "callback"),
    (CPA.c_void_p, 1, "userdata"),
)
pa_context_get_server_info.errcheck = _errcheck

#### libpulseAPI instrospect - sinks
# sink処理

# pa_context_get_sink_info_by_name()などのcallbackのプロトタイプ
PA_SINK_INFO_CB_T = CPA.CFUNCTYPE(
    None, CPA.c_void_p, CPA.c_void_p, CPA.c_int, CPA.c_void_p
)
"""pa_context_get_sink_info_by_name()などのcallbackのプロトタイプ

:param pa_context *context: 対象のcontext
:param pa_sink_info *info: sink情報
:param int eol: リスト終端判定値、0ならリスト内か単一のオブジェクトを取得
:param void *userdata: ****
"""

# 名前からsinkのpa_sink_infoを取得
pa_context_get_sink_info_by_name = _prototype(
    CPA.c_void_p,
    "pa_context_get_sink_info_by_name",
    (CPA.c_void_p, 1, "context"),
    (CPA.c_char_p, 1, "name"),
    (PA_SINK_INFO_CB_T, 1, "callback"),
    (CPA.c_void_p, 1, "userdata"),
)
pa_context_get_sink_info_by_name.errcheck = _errcheck

# 名前からsinkのvolumeを設定
pa_context_set_sink_volume_by_name = _prototype(
    CPA.c_void_p,
    "pa_context_set_sink_volume_by_name",
    (CPA.c_void_p, 1, "context"),
    (CPA.c_char_p, 1, "name"),
    (CPA.POINTER(PA_CVOLUME), 1, "volume"),
    (PA_CONTEXT_SUCCESS_CB_T, 1, "callback"),
    (CPA.c_void_p, 1, "userdata"),
)
pa_context_set_sink_volume_by_name.errcheck = _errcheck

#### libpulseAPI instrospect - sources
# source処理

# pa_context_get_source_info_by_name() などのcallbackプロトタイプ
PA_SOURCE_INFO_CB_T = CPA.CFUNCTYPE(
    None, CPA.c_void_p, CPA.c_void_p, CPA.c_int, CPA.c_void_p
)
"""pa_context_get_source_info_by_name() などのcallbackプロトタイプ

:param pa_context *context: 対象のcontext
:param pa_source_info *info: ソース情報
:param int eol: リスト終端判定値、0ならリスト内か単一のオブジェクトを取得
:param void *userdata: ****
"""

# source nameからsourceの情報を取得
pa_context_get_source_info_by_name = _prototype(
    CPA.c_void_p,
    "pa_context_get_source_info_by_name",
    (CPA.c_void_p, 1, "context"),
    (CPA.c_char_p, 1, "name"),
    (PA_SOURCE_INFO_CB_T, 1, "callback"),
    (CPA.c_void_p, 1, "userdadta"),
)
pa_context_get_source_info_by_name.errcheck = _errcheck

# sourceのpa_cvolumeを設定
pa_context_set_source_volume_by_name = _prototype(
    CPA.c_void_p,
    "pa_context_set_source_volume_by_name",
    (CPA.c_void_p, 1, "context"),
    (CPA.c_char_p, 1, "name"),
    (CPA.POINTER(PA_CVOLUME), 1, "volume"),
    (PA_CONTEXT_SUCCESS_CB_T, 1, "callback"),
    (CPA.c_void_p, 1, "userdata"),
)
pa_context_get_source_info_by_name.errcheck = _errcheck

#### libpulseAPI volume
# 音量処理

# 全チャンネルの平均音量を返す
pa_cvolume_avg = _prototype(
    PA_VOLUME_T, "pa_cvolume_avg", (CPA.POINTER(PA_CVOLUME), 1, "cvolume")
)
pa_cvolume_avg.errcheck = _errcheck

# 指定されたチャンネル数の音量をボリュームvに設定
pa_cvolume_set = _prototype(
    CPA.POINTER(PA_CVOLUME),
    "pa_cvolume_set",
    (CPA.POINTER(PA_CVOLUME), 1, "cvolume"),
    (CPA.c_uint, 1, "channels"),
    (PA_VOLUME_T, 1, "value"),
)
pa_cvolume_set.errcheck = _errcheck

#### 汎用PulseAudioクラスなどで使うcallback関数
# contextはクラススコープなので、クラススコープのcallback関数


@PA_CONTEXT_NOTIFY_CB_T
def _connect_state(context, userdata):
    """callback関数

    PA_CONTEXT_STATE列挙型の値(contextのサーバー接続状態)をuserdataに渡す
    | pa_context_set_state_callback()

    :param pa_context *context: context
    :param void *userdata: PA_CONTEXT_STATEを収受
    """

    cast_userdata = CPA.cast(userdata, CPA.POINTER(CPA.c_int)).contents
    cast_userdata.value = pa_context_get_state(context)


# ローカルスコープで操作(operation)完了しないcallback関数


@PA_CONTEXT_SUCCESS_CB_T
def _success_state(context, success, userdata):
    """callback関数

    操作完了の成否を得る
    | pa_context_set_sink_volume_by_nam()
    | pa_context_set_source_volume_by_name()

    :param pa_context *context: 対象のcontext
    :param int success: 0 - 正常に操作完了、1 - 異常な操作完了
    :param void *userdata: ****
    """

    cast_userdata = CPA.cast(userdata, CPA.POINTER(CPA.c_int)).contents
    cast_userdata.value = success


#### 基本のPulseAudioクラス


class BasePulseaudio:
    """基本のPulseAudioクラス

    コンストラクタ: mainloopの作成、contextのPulseAudioサーバーへの接続
    デストラクタ: contextのPulseAudioサーバーへの切断、mainloopの開放
    """

    def __init__(self, name: str):
        try:

            self._mainloop = pa_mainloop_new()

            self._context = pa_context_new(
                pa_mainloop_get_api(self._mainloop), name.encode("utf-8")
            )
            pa_context_connect(self._context, None, 0, None)

            connect = CPA.c_int(PA_CONTEXT_STATE.UNCONNECTED)
            pa_context_set_state_callback(
                self._context, _connect_state, CPA.pointer(connect)
            )

            # サーバー接続の準備完了まで待つ
            while connect.value in list(PA_CONTEXT_STATE):
                match connect.value:
                    # サーバー接続の準備中
                    case (
                        PA_CONTEXT_STATE.UNCONNECTED
                        | PA_CONTEXT_STATE.CONNECTING
                        | PA_CONTEXT_STATE.AUTHORIZING
                        | PA_CONTEXT_STATE.SETTING_NAME
                    ):
                        pass
                    # サーバー接続の準備OK
                    case PA_CONTEXT_STATE.READY:
                        break
                    # サーバー接続の失敗
                    case PA_CONTEXT_STATE.FAILED | PA_CONTEXT_STATE.TERMINATED:
                        raise
                pa_mainloop_iterate(self._mainloop, 1, None)

        except PAError as message:
            raise PAError(f"BasePulseaudio - constructor: {message}")

        else:
            logger.info("PulseAudio Server に接続")

    def __del__(self):
        pa_context_disconnect(self._context)
        pa_context_unref(self._context)

        pa_mainloop_free(self._mainloop)

        logger.info("PulseAudio Server 接続を解除")


#### Volumeのクラス


class VolumePulseaudio(BasePulseaudio):
    """Volume - Pulseaudio

    sink あるいは source の音量コントロールクラス

    property
    facility_name(取得のみ): Facilityの名前
    facility_type(取得のみ): Facilityのタイプ ["SINK", "SOURCE"]
    value: 音量値
    """

    def __init__(self, type: Literal["SINK", "SOURCE"], name: str = "VPA"):
        super().__init__(name)

        try:
            self._type = type
            self._default_name = self._get_default_name()

            self._cvolume = PA_CVOLUME()
            self._get_cvolume()

        except KeyError as message:
            # typeに"SINK"か"SOURCE"以外を指定した際の例外処理(KeyError)を想定
            raise KeyError

        except PAError as message:
            raise PAError(f"VolumePulseaudio - contructor : {message}")

        else:
            logger.info(f"{self._type} {self._default_name} 音量コントールを開始")

    @property
    def facility_name(self) -> str:
        """名前を得る

        :return str: facilityの名前
        """

        return self._default_name

    @property
    def facility_type(self) -> str:
        """タイプを得る

        :return str: facilityのタイプ
        """

        return self._type

    @property
    def value(self) -> int:
        """音量値を得る

        PulseAudioの生の音量値( 0 - 65535)を返す
        多チャンネルでも単一の音量値に纏める

        :retrun int: 音量値(0 - 65535)
        """

        self._get_cvolume()

        return pa_cvolume_avg(CPA.pointer(self._cvolume))

    @value.setter
    def value(self, value: int) -> None:
        """音量値を設定する

        PulseAudioの生の音量値(0 - 65536)を設定する
        多チャンネルの場合、すべてのチャンネルに設定する

        :param int value: 音量値(0 - 65535)
        """

        self._set_cvolume(value)

    def _get_cvolume(self) -> None:
        """現在のPA_CVOLUME構造体オブジェクトを得る

        まずsink情報/source情報構造体オブジェクトを得た後、
        PA_CVOLUME構造体オブジェクトを抽出しコピーする
        """

        @PA_SINK_INFO_CB_T
        def sink_info(context, info, eol, userdata) -> None:
            """callback関数

            sink情報から現在のPA_CVOLUME構造体オブジェクトを得る
            | pa_context_get_sink_info_by_name()

            :param pa_context *context: 対象のcontext
            :param pa_sink_info *info: sink情報
            :param int eol: リスト終端判定値、0ならリスト内か単一のオブジェクトを取得
            :param void *userdata: ****
            """

            if eol == 0:
                cast_info = CPA.cast(info, CPA.POINTER(PA_SINK_INFO)).contents
                cast_userdata = CPA.cast(userdata, CPA.POINTER(PA_CVOLUME)).contents

                cast_userdata.channels = cast_info.volume.channels
                for ci in range(cast_info.volume.channels):
                    cast_userdata.values[ci] = cast_info.volume.values[ci]

        @PA_SOURCE_INFO_CB_T
        def source_info(context, info, eol, userdata) -> None:
            """callback関数

            source情報から現在のPA_CVOLUME構造体オブジェクトを得る
            | pa_context_get_source_info_by_name()

            :param pa_context *context: 対象のcontext
            :param pa_source_info *info: source情報
            :param int eol: リスト終端判定値、0ならリスト内か単一のオブジェクトを取得
            :param void *userdata: ****
            """

            if eol == 0:
                cast_info = CPA.cast(info, CPA.POINTER(PA_SOURCE_INFO)).contents
                cast_userdata = CPA.cast(userdata, CPA.POINTER(PA_CVOLUME)).contents

                cast_userdata.channels = cast_info.volume.channels
                for ci in range(cast_info.volume.channels):
                    cast_userdata.values[ci] = cast_info.volume.values[ci]

        try:
            func = {
                "SINK": pa_context_get_sink_info_by_name,
                "SOURCE": pa_context_get_source_info_by_name,
            }
            callback = {"SINK": sink_info, "SOURCE": source_info}

            operation = func[self._type](
                self._context,
                self._default_name,
                callback[self._type],
                CPA.pointer(self._cvolume),
            )

            while pa_operation_get_state(operation) != PA_OPERATION_STATE.DONE:
                pa_mainloop_iterate(self._mainloop, 1, None)

            pa_operation_unref(operation)

        except PAError as message:
            raise PAError(f"_get_cvolume: {message}")

    def _set_cvolume(self, value: int) -> None:
        """現在のPA_CVOLUME構造体オブジェクトを設定する"""

        try:
            func = {
                "SINK": pa_context_set_sink_volume_by_name,
                "SOURCE": pa_context_set_source_volume_by_name,
            }
            success = CPA.c_int(-1)

            operation = func[self._type](
                self._context,
                self._default_name,
                pa_cvolume_set(
                    CPA.pointer(self._cvolume),
                    self._cvolume.channels,
                    PA_VOLUME_T(value),
                ),
                _success_state,
                CPA.pointer(success),
            )
            while pa_operation_get_state(operation) != PA_OPERATION_STATE.DONE:
                pa_mainloop_iterate(self._mainloop, 1, None)

            pa_operation_unref(operation)

        except PAError as message:
            raise PAError(f"_set_cvolume: {message}")

    def _get_default_name(self) -> str:
        """default_nameを得る

        server情報からsinkあるいはsourceのデフォルトの名前を得る

        :return str: "SINK": default_sink_name, "SOURCE": default_source_name
        """

        @PA_SERVER_INFO_CB_T
        def server_info(context, info, userdata) -> None:
            """callback関数

            pa_context_get_server_info()で登録
            PA_SERVER_INFO構造体オブジェクト(server情報)からdefault_sinke_nameをuserdataに渡す

            :param pa_context *context: 対象のcontext
            :param pa_server_info *info: server情報
            :param void *userdata: ****
            """
            cast_info = CPA.cast(info, CPA.POINTER(PA_SERVER_INFO)).contents
            cast_userdata = CPA.cast(userdata, CPA.c_char_p)

            type = cast_userdata.value
            match type:
                case b"sink":
                    CPA.memmove(
                        cast_userdata,
                        cast_info.default_sink_name,
                        len(cast_info.default_sink_name),
                    )
                case b"source":
                    CPA.memmove(
                        cast_userdata,
                        cast_info.default_source_name,
                        len(cast_info.default_source_name),
                    )

        try:
            default_name_type = {"SINK": b"sink", "SOURCE": b"source"}

            # サイズ不明の文字列データは、余裕を持った大きめのバッファを確保
            default_name = CPA.create_string_buffer(default_name_type[self._type], 512)

            operation = pa_context_get_server_info(
                self._context, server_info, default_name
            )

            while pa_operation_get_state(operation) != PA_OPERATION_STATE.DONE:
                pa_mainloop_iterate(self._mainloop, 1, None)

            pa_operation_unref(operation)

            return default_name.value

        except PAError as message:
            raise PAError(f"_get_default_name: {message}")


if __name__ == "__main__":
    print(__file__)
