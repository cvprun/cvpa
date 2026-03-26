# -*- coding: utf-8 -*-

from typing import Final

TIMEOUT_INFINITE: Final[float] = -1.0
INFINITE: Final[int] = -1
UNKNOWN_ERROR_CODE: Final[int] = -1
NOT_FOUND_INDEX: Final[int] = -1
UNKNOWN_TOTAL_SIZE: Final[int] = -1
UNKNOWN_PID: Final[int] = -1
UNKNOWN_VERSION: Final[int] = -1
UNKNOWN_THREAD_IDENT: Final[int] = -1
INFINITY_HEIGHT_IN_ITEMS: Final[int] = -1
EPHEMERAL_PORT: Final[int] = -1
NULL_CODEPOINT: Final[int] = 0
BACKSPACE_CODEPOINT: Final[int] = ord("\b")
DELETE_CODEPOINT: Final[int] = 0x7F
NODOC: Final[str] = ""
COMMENT_PREFIX: Final[str] = "#"
HEXADECIMAL: Final[int] = 16
NEWLINE: Final[str] = "\n"
COMMA: Final[str] = ","

DEFAULT_STRING_ENCODING: Final[str] = "utf-8"
DEFAULT_STRING_ERRORS: Final[str] = "strict"
DEFAULT_STRING_NEWLINE: Final[str] = "\n"
DEFAULT_STRING_LINE_CONTINUATION_CHARACTER: Final[str] = "\\"

STDIN_FILE_HANDLE: Final[int] = 0
STDOUT_FILE_HANDLE: Final[int] = 1
STDERR_FILE_HANDLE: Final[int] = 2

STDIN_FILE_NAME: Final[str] = "stdin"
STDOUT_FILE_NAME: Final[str] = "stdout"
STDERR_FILE_NAME: Final[str] = "stderr"

LOCALHOST: Final[str] = "localhost"
ROOT_PATH: Final[str] = "/"

CVPA_TITLE: Final[str] = "CVPA"
CVPA_HOME_DIRNAME: Final[str] = ".cvpa"
CVPA_YML_FILENAME: Final[str] = "cvpa.yml"
CVPA_EXTENSION: Final[str] = ".cvpa"
CVPA_ROOT_INFO_FILENAME: Final[str] = "info.yml"
GUI_INI_FILENAME: Final[str] = "gui.ini"
LOGGING_JSON_FILENAME: Final[str] = "logging.json"

DOTENV_LOCAL_FILENAME: Final[str] = ".env.local"
DOTENV_TEST_FILENAME: Final[str] = ".env.test"

MODULE_PATH_SEPARATOR: Final[str] = "."
CONFIG_VALUE_SEPARATOR: Final[str] = ","
CHECKSUM_DELIMITER: Final[str] = ":"

UNICODE_SINGLE_BLOCK_SIZE: Final[int] = 0x100
CODEPOINT_RANGES_EXTENSION: Final[str] = ".ranges"
CODEPOINT_GLYPHS_EXTENSION: Final[str] = ".glyphs"
KEYRING_EXTENSION: Final[str] = ".cfg"

FONT_SIZE: Final[int] = 14
FONT_PREVIEW_SIZE: Final[int] = 48
FONT_SCALE: Final[float] = 1.0
FONT_DEFAULT_NAME: Final[str] = "Default"

THREAD_POOL_PREFIX: Final[str] = "cvpa.threadpool"
MAX_THREAD_WORKERS: Final[int] = 5
MAX_PROCESS_WORKERS: Final[int] = 5

PROCESS_LOGFILE_PREFIX: Final[str] = ""
PROCESS_LOGFILE_SUFFIX: Final[str] = ".log"
PROCESS_PIDFILE_SUFFIX: Final[str] = ".pid"

ASCII_RANGE: Final[int] = 127
MAX_IMGUI_KEYCODE: Final[int] = 512

MOUSE_WHEEL_OFFSET_SCALE: Final[float] = 0.5

LOGGING_STEP: Final[int] = 1000
SLOW_CALLBACK_DURATION: Final[float] = 0.05

SAFETY_FILE_SUFFIX_NEW: Final[str] = ".new.backup"
SAFETY_FILE_SUFFIX_OLD: Final[str] = ".old.backup"

FFMPEG_EXECUTABLE_FILENAME: Final[str] = "ffmpeg"
FFPROBE_EXECUTABLE_FILENAME: Final[str] = "ffprobe"

STREAM_LOGGING_MAXSIZE: Final[int] = 65536
STREAM_LOGGING_ENCODING: Final[str] = "utf-8"
STREAM_LOGGING_ERRORS: Final[str] = "strict"
STREAM_LOGGING_NEWLINE_SIZE: Final[int] = 88

WSD_INVALID_INSTANCE_ID: Final[int] = -1
WSD_INVALID_MESSAGE_NUMBER: Final[int] = -1
WSD_INVALID_METADATA_VERSION: Final[int] = -1
WSD_UNICAST_ADDRESS: Final[str] = "192.168.0.1"
WSD_IPV4_MULTICAST_ADDRESS: Final[str] = "239.255.255.250"
WSD_IPV6_MULTICAST_ADDRESS: Final[str] = "ff02::c"
WSD_PORT_NUMBER: Final[int] = 3702
WSD_TIMEOUT: Final[float] = 3.0
WSD_NAME_DEFAULT: Final[str] = "New Device"
WSD_ONVIF_SCOPE_PREFIX: Final[str] = "onvif://www.onvif.org/name/"
WSD_ONVIF_SCOPE_PREFIX_LEN: Final[int] = len(WSD_ONVIF_SCOPE_PREFIX)
WSD_UNICAST_UDP_REPEAT: Final[int] = 2
WSD_MULTICAST_UDP_REPEAT: Final[int] = 4
WSD_RELATES_TO: Final[bool] = True

SOCKMAP_ADDRESS_BEGIN: Final[str] = "192.168.0.1"
SOCKMAP_ADDRESS_END: Final[str] = "192.168.0.254"
SOCKMAP_PORT_RANGE: Final[str] = "80,443"
SOCKMAP_TIMEOUT: Final[float] = 3.0

ONVIF_NONAME: Final[str] = "New Device"
ONVIF_ADDRESS: Final[str] = "http://localhost/"

ZEEP_ELEMENT_SEPARATOR: Final[str] = "."
