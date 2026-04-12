---
name: python-conventions
description: Python 코딩 규칙 레퍼런스. Python 코드를 작성, 수정, 리뷰할 때 이 프로젝트의 코딩 컨벤션을 적용한다. 새 파일 생성, 클래스 작성, 테스트 작성, 리팩토링 등 Python 코드 관련 작업 시 자동 참조.
user-invocable: false
---

# Python 코딩 컨벤션 (CVP 프로젝트 기반)

이 스킬은 Python 코드를 작성할 때 반드시 따라야 하는 코딩 규칙이다.
CVP(Computer Vision Player) 프로젝트의 실제 코드에서 추출한 패턴이다.

---

## 1. 파일 헤더

모든 `.py` 파일은 인코딩 선언으로 시작한다.

```python
# -*- coding: utf-8 -*-
```

---

## 2. Import 스타일

### 순서: stdlib → third-party → local (isort black 프로필)

```python
# -*- coding: utf-8 -*-

# 표준 라이브러리 (알파벳 순, from 형태)
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum, auto, unique
from os import PathLike
from os.path import expanduser, isfile, join
from re import Pattern
from re import compile as re_compile
from sys import exit as sys_exit
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
    Union,
)

# 서드파티
from yaml import dump, full_load

# 로컬
from cvp.config.config import Config
from cvp.logging.loggers import logger
from cvp.types.override import override
```

### 규칙
- `from module import Name` 형태 사용. `import module` 지양
- star import (`from x import *`) 절대 금지
- 충돌 시 별칭: `from sys import exit as sys_exit`
- 멀티라인은 괄호 `()` 사용, 백슬래시 `\` 금지

---

## 3. 상수 정의

`Final` 타입 어노테이션 필수. `UPPER_SNAKE_CASE` 네이밍.

```python
from typing import Final

# 스칼라
TIMEOUT_INFINITE: Final[float] = -1.0
DEFAULT_STRING_ENCODING: Final[str] = "utf-8"
LOCALHOST: Final[str] = "localhost"

# 컴포짓 (튜플)
CANVAS_ANCHOR_COLOR: Final[RGBA] = 1.0, 0.0, 0.0, 0.9
EMPTY_POINT: Final[Point] = 0.0, 0.0

# 불변 시퀀스
SEVERITIES: Final[Sequence[str]] = (
    SEVERITY_NAME_CRITICAL,
    SEVERITY_NAME_ERROR,
    SEVERITY_NAME_WARNING,
)

# 정규식
VERSION_REGEX: Final[Pattern[str]] = re_compile(r"(\d+\.\d+)(.*)")

# 불변 매핑
from types import MappingProxyType
LEVEL_TO_NAME: Final[MappingProxyType[int, str]] = MappingProxyType({
    logging.CRITICAL: "critical",
    logging.ERROR: "error",
})
```

---

## 4. 클래스 구조

### 원칙: 한 파일에 하나의 클래스

```python
# -*- coding: utf-8 -*-

from typing import Callable, Generic, Optional, TypeVar

_T = TypeVar("_T")


class DeltaValue(Generic[_T]):
    """
    A class designed for interoperability with `imgui`.

    Provides a value container that tracks changes and
    optionally triggers a callback when updated.
    """

    def __init__(
        self,
        value: _T,
        prev: _T,
        callback: Optional[Callable[[_T, _T], None]] = None,
    ):
        self.prev = prev
        self.value = value
        self._callback = callback

    @classmethod
    def from_single_value(
        cls,
        value: _T,
        on_change: Optional[Callable[[_T, _T], None]] = None,
    ):
        return cls(value, value, on_change)

    @property
    def changed(self) -> bool:
        return self.prev != self.value

    def update(self, value: _T, *, no_emit=False) -> bool:
        self.prev = self.value
        self.value = value
        changed = self.prev != self.value
        if not no_emit and changed and self._callback is not None:
            self._callback(self.value, self.prev)
        return changed
```

### 메서드 순서
1. `__init__`
2. `@classmethod` (팩토리)
3. `@staticmethod`
4. `@property` (getter/setter)
5. public 메서드
6. `_private` 메서드

### 속성 접근제어

```python
class Pin:
    def __init__(self, name: PinName, dtype: Union[None, type, Dtype]):
        self.__dtype = dtype if isinstance(dtype, Dtype) else Dtype(dtype)  # private (mangling)
        self.__name = name                                                  # private (mangling)
        self._hidden = False                                                # protected

    @property
    def name(self) -> PinName:
        return self.__name

    @property
    def dtype(self) -> Dtype:
        return self.__dtype
```

- **Public**: `self.value`
- **Protected**: `self._callback` (내부/서브클래스)
- **Private**: `self.__name` (name mangling, `@property`로 노출)

---

## 5. 타입 어노테이션

모든 public 함수는 파라미터와 리턴 타입을 명시한다.

### TypeVar와 Generic

```python
_T = TypeVar("_T")
ErrorT = TypeVar("ErrorT", bound=BaseException)

class Dtype(Generic[_T], Serializable):
    _type: Type[_T]
    _path: TypePath
```

### TypeAlias

```python
_X: TypeAlias = float
_Y: TypeAlias = float
Point: TypeAlias = Tuple[_X, _Y]
Size: TypeAlias = Tuple[_Width, _Height]
```

### NewType (의미 구분)

```python
TypePath = NewType("TypePath", str)
PinName = NewType("PinName", str)
MediaKey = NewType("MediaKey", str)
```

### Overload (다중 시그니처)

```python
@overload
def get(self, service: str, key: str) -> Optional[str]: ...
@overload
def get(self, service: str, key: str, default: str) -> str: ...

def get(
    self,
    service: str,
    key: str,
    default: Optional[str] = None,
) -> Optional[str]:
    cache_key = self.gen_cache_key(service, key)
    if cache_key in self._cache:
        return self._cache[cache_key]
    return default
```

### NamedTuple

```python
class ServiceKey(NamedTuple):
    service: str
    key: str

class MonthDay(NamedTuple):
    month: int  # 1-12
    day: int    # 1-31

    def __str__(self):
        return f"{self.month:02}/{self.day:02}"

    @classmethod
    def from_date(cls, d: date):
        return cls(d.month, d.day)
```

### Dataclass

```python
@dataclass
class MediaConfig:
    uuid: str = field(default_factory=lambda: str(uuid4()))
    name: str = field(default_factory=str)
    opened: bool = False
    frame_width: int = MEDIA_FRAME_WIDTH

    @property
    def frame_size(self) -> Tuple[int, int]:
        return self.frame_width, self.frame_height

    @frame_size.setter
    def frame_size(self, value: Tuple[int, int]) -> None:
        self.frame_width = value[0]
        self.frame_height = value[1]
```

---

## 6. Enum 패턴

`@unique` 데코레이터 필수. `auto()`로 값 할당.

### StrEnum

```python
@unique
class Action(StrEnum):
    exec = auto()
    """Execution pins are used to connect nodes together"""

    data = auto()
    """Data pins are used for taking data into a node"""
```

### IntEnum

```python
@unique
class PinKind(IntEnum):
    positional_only = Parameter.POSITIONAL_ONLY.value
    positional_or_keyword = Parameter.POSITIONAL_OR_KEYWORD.value
    return_only = auto()
    unknown = auto()
```

### match 문 (Python 3.10+)

```python
def create_action(value: AnyAction) -> Action:
    if isinstance(value, Action):
        return value
    elif isinstance(value, str):
        match value.lower():
            case "exec":
                return Action.exec
            case "data":
                return Action.data
            case _:
                raise ValueError(f"Unsupported action value: {value}")
    else:
        raise TypeError(f"Unsupported action type: {type(value).__name__}")
```

---

## 7. 추상 클래스와 @override

### 추상 메서드: 반드시 `raise NotImplementedError`

```python
from abc import ABC, abstractmethod

class ProxyValue(Generic[ValueT], ABC):
    @abstractmethod
    def get(self) -> ValueT:
        raise NotImplementedError

    @abstractmethod
    def set(self, value: ValueT) -> None:
        raise NotImplementedError
```

### @override: 부모 메서드 재정의 시 필수

```python
from cvp.types.override import override

class Dtype(Generic[_T], Serializable):
    @override
    def __serialize__(self) -> Any:
        return str(self._path)

    @override
    def __deserialize__(self, data: Any) -> None:
        if not isinstance(data, str):
            raise TypeError(f"Unexpected data type: {type(data).__name__}")
        self._type, self._path = load_with_path(data)
```

---

## 8. 테스트 파일 구조

`unittest.TestCase` 사용. pytest 스타일 아님.

```python
# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvp.values.delta import DeltaValue


class DeltaTestCase(TestCase):
    def setUp(self):
        self._current = 0
        self._previous = 0

    def _on_change(self, value: int, prev: int):
        self._current = value
        self._previous = prev

    def test_default(self):
        watcher = DeltaValue(0, 0, self._on_change)
        self.assertFalse(watcher.update(0))
        self.assertEqual(0, self._current)
        self.assertFalse(watcher.changed)

    def test_update_triggers_callback(self):
        watcher = DeltaValue(0, 0, self._on_change)
        self.assertTrue(watcher.update(1))
        self.assertEqual(1, self._current)
        self.assertTrue(watcher.changed)


if __name__ == "__main__":
    main()
```

### 테스트 규칙
- 클래스명: `XxxTestCase` (TestCase 접미사)
- 메서드명: `test_` 접두사
- 미러링: `cvp/mod/foo.py` → `tester/mod/test_foo.py`
- 파일 끝: `if __name__ == "__main__": main()` 필수
- assertion 순서: `assertEqual(expected, actual)` — expected 먼저

---

## 9. 문자열 처리

f-string만 사용. `%` 포매팅과 `.format()` 금지.

```python
# 기본
raise TypeError(f"This is not a class type: '{path}'")

# 포맷 지정자
def __str__(self):
    return f"{self.month:02}/{self.day:02}"

# 멀티라인 (문자열 연결)
logger.warning(
    f"Please modify the value of '{self._config_section_path}'"
    f" to {self._update_value} of the"
    f" '{str(self._context.home.cvp_yml)}' file and try again."
)

# repr
def __repr__(self) -> str:
    return f"<{type(self).__name__} {self._path}>"
```

---

## 10. 비동기 패턴

```python
# sync + async 컨텍스트 매니저 (같은 클래스에서)
class ContextPropagator:
    def __enter__(self):
        self._stack.push(self._context)
        return self._context

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stack.pop()

    async def __aenter__(self):
        self._stack.push(self._context)
        return self._context

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._stack.pop()

# 비동기 예외 보호
async def shield_any(coro, logger: Logger):
    try:
        return await coro
    except BaseException as e:
        logger.exception(e)
```

---

## 11. 컨텍스트 매니저

```python
from contextlib import contextmanager

@contextmanager
def disable_logging(level=logging.CRITICAL):
    previous_level = logging.root.manager.disable
    logging.disable(level)
    try:
        yield
    finally:
        logging.disable(previous_level)
```

---

## 12. 로깅

`cvp.logging.loggers`의 `logger` 사용.

```python
from cvp.logging.loggers import logger

logger.info(f"Initialize config: '{logging_path}'")
logger.warning(f"Detect OpenGL config via subprocess ...")
logger.error(f"Failed to send message: {e}")
logger.debug(f"Message sent: {message}")
logger.exception(e)
```

---

## 13. 에러 처리

```python
# Generic 커스텀 예외
class AutoFixerError(Generic[ValueT], Exception):
    def __init__(self, path: str, value: ValueT):
        super().__init__(
            f"Due to AutoFixer, '{path}' was automatically corrected to {value}"
        )

# 선택적 의존성 패턴
try:
    from dotenv import load_dotenv
    load_dotenv(args.dotenv_path)
except ModuleNotFoundError:
    pass

# 예외 체이닝
raise AutoFixerError[ValueT](
    self._config_section_path, self._update_value
) from error
```

---

## 14. 네이밍 컨벤션

| 대상 | 스타일 | 예시 |
|------|--------|------|
| 모듈 | `lowercase` | `config.py`, `propagator.py` |
| 클래스 | `PascalCase` | `DragButton`, `ContextPropagator` |
| 함수/메서드 | `snake_case` | `get_default_arguments` |
| 상수 | `UPPER_SNAKE_CASE` | `TIMEOUT_INFINITE` |
| Private 속성 | `__double_underscore` | `self.__name` |
| Protected 속성 | `_single_underscore` | `self._callback` |
| TypeVar | `_T` 또는 `XxxT` | `_T`, `ErrorT`, `ValueT` |
| NewType | `PascalCase` | `TypePath`, `PinName` |
| TypeAlias | `PascalCase` | `Point`, `Size`, `RGBA` |

---

## 15. 파일/모듈 조직

- `__init__.py`는 비워둔다 (빈 파일 또는 인코딩 선언만)
- 한 파일에 하나의 클래스
- 코드 라인 폭: **88자** (black 기본값)
- 주석/독스트링도 88자 이내

---

## 16. Docstring

- 클래스에만 작성 (메서드는 복잡한 경우만)
- 삼중 따옴표 사용
- Enum 멤버에는 인라인 독스트링

```python
class IntervalUpdater(IntervalTimer, ABC):
    """
    A class designed for interoperability with `imgui`.

    This class is a generic abstract base class that provides automatic or manual
    data refresh functionality based on a time interval.
    """
```

---

## 17. 함수 시그니처 패턴

### Keyword-only 인자 (`*` 이후)

```python
def update(self, value: _T, *, no_emit=False) -> bool:
    pass
```

### @classmethod 팩토리

```python
@classmethod
def from_single_value(
    cls,
    value: _T,
    on_change: Optional[Callable[[_T, _T], None]] = None,
):
    return cls(value, value, on_change)
```

### @staticmethod

```python
@staticmethod
def gen_cache_key(service: str, key: str):
    return ServiceKey(service, key)
```

---

## 18. 코드 품질 도구 설정

| 도구 | 설정 |
|------|------|
| black | 88자 라인 폭 |
| flake8 | `E203`, `W503` 무시, 88자 |
| isort | `profile = black`, `py_version = 39` |
| mypy | `ignore_missing_imports = True` |
| pytest | `asyncio_mode = auto` |

---

## 19. 디렉토리 구조 및 모듈 그룹화

### 전체 구조: 기능별 그룹화 (Functional Grouping)

```
cvp/                          # 메인 패키지
├── __init__.py               # 버전만 포함 (__version__)
├── __main__.py               # CLI 진입점 (최소 코드)
├── entrypoint.py             # main() 함수
├── arguments.py              # CLI 인자 파싱
├── variables.py              # 환경 변수 정의
│
├── apps/                     # ── 애플리케이션 레이어 ──
│   ├── agent/                #   백그라운드 서비스
│   ├── cli/                  #   CLI 인터페이스
│   ├── player/               #   GUI 애플리케이션
│   │   └── modes/            #     33개 서브 모드 (각 기능별 디렉토리)
│   │       ├── canvas/       #       캔버스 모드
│   │       ├── flow/         #       플로우 그래프 모드
│   │       ├── medias/       #       미디어 플레이어 모드
│   │       └── ...           #       (binary, chat, games, ...)
│   └── tester/               #   테스트용 애플리케이션
│
├── flow/                     # ── 도메인 코어 ──
│   ├── graph.py              #   그래프 매니저
│   ├── node.py               #   노드 추상화
│   ├── pin.py                #   핀 타입
│   ├── wire.py               #   연결선
│   ├── runner.py             #   실행 엔진
│   └── manager.py            #   매니저
│
├── nodes/                    # ── 노드 시스템 (라이브러리별 그룹) ──
│   ├── node.py               #   베이스 노드
│   ├── defaults/             #   기본 노드 구현
│   │   ├── numpy/            #     NumPy 연산 노드
│   │   │   ├── array_creation/
│   │   │   ├── array_manipulation/
│   │   │   ├── mathematical/
│   │   │   └── linalg/
│   │   ├── pandas/           #     Pandas 연산 노드
│   │   │   ├── core/
│   │   │   ├── io/
│   │   │   └── manipulation/
│   │   ├── opencv/           #     OpenCV 연산 노드
│   │   │   ├── core/
│   │   │   ├── imgproc/
│   │   │   └── video/
│   │   ├── operators/        #     기본 연산자 노드
│   │   ├── casting/          #     타입 변환 노드
│   │   └── essential/        #     핵심 노드 (entrypoint 등)
│   └── registry/             #   노드 등록 시스템
│
├── pygame/                   # ── 그래픽스/렌더링 ──
│   ├── able/                 #   인터페이스 믹스인 (displayable, eventable, ...)
│   ├── constants/            #   pygame 상수 (keycode, event_type, ...)
│   ├── events/               #   이벤트 시스템
│   ├── surface/              #   서피스 추상화
│   └── transforms/           #   이미지 변환 (blur, rotate, scale, ...)
├── gl/                       #   OpenGL 유틸리티
│   ├── textures/             #     텍스처 관리
│   ├── fbo/                  #     프레임버퍼
│   └── objects/              #     3D 오브젝트
├── imgui/                    #   ImGui UI 바인딩
│   ├── widgets/              #     위젯 컴포넌트
│   ├── fonts/                #     폰트 관리
│   └── flow/                 #     플로우 시각화
├── renderer/                 #   렌더러 추상화
│   ├── base/                 #     베이스 인터페이스
│   ├── opengl/               #     OpenGL 렌더러
│   └── pygame/               #     PyGame 렌더러
├── canvas/                   #   캔버스 시스템
│
├── ffmpeg/                   # ── 미디어 처리 ──
│   ├── ffmpeg/               #   FFmpeg 빌더 패턴
│   ├── ffprobe/              #   미디어 정보 탐색
│   ├── m3u/                  #   M3U 플레이리스트
│   ├── capabilities/         #   코덱 탐지
│   └── h264/, hevc/, av1/    #   코덱별 모듈
│
├── network/                  # ── 네트워크/통신 ──
│   ├── uri/                  #   URI 파싱
│   └── ports/                #   포트 관리
├── ws/                       #   WebSocket
│   ├── asyncio/              #     비동기 클라이언트
│   ├── threading/            #     스레드 클라이언트
│   └── handlers/             #     메시지 핸들러
├── onvif/                    #   ONVIF 카메라 프로토콜
├── modbus/                   #   Modbus 프로토콜
├── wsdiscovery/              #   WS-Discovery
│
├── maths/                    # ── 수학 ──
│   ├── geometry/             #   기하학
│   │   ├── bbox/             #     바운딩 박스
│   │   ├── system/           #     좌표계 (cartesian, polar, ...)
│   │   └── transform/        #     변환
│   ├── equation/             #   방정식
│   │   └── linear/           #     선형 방정식
│   ├── bezier/               #   베지어 곡선
│   ├── trigonometry/         #   삼각함수
│   ├── statistics/           #   통계
│   └── numeral/              #   단위 변환
│
├── config/                   # ── 설정 ──
│   └── sections/             #   설정 섹션 (기능별 1:1 매핑)
│       ├── appearance.py     #     외관 설정
│       ├── developer.py      #     개발자 설정
│       ├── font.py           #     폰트 설정
│       └── ...               #     (각 기능 모듈당 하나)
│
├── types/                    # ── 타입 시스템 ──
│   ├── dataclass/            #   dataclass 유틸리티
│   ├── enum/                 #   enum 유틸리티
│   ├── matcher/              #   타입 매칭
│   └── override.py           #   @override 데코레이터
│
├── logging/                  # ── 로깅 ──
│   ├── formatters/           #   포매터
│   ├── handlers/             #   핸들러
│   └── records/              #   레코드
│
├── terminal/                 # ── 터미널/텍스트 ──
│   └── ansi/                 #   ANSI 이스케이프
│       └── sgr/              #     색상/스타일 코드
│
├── context/                  # ── 인프라 유틸리티 ──
├── containers/               #   컨테이너 타입
├── concurrency/              #   동시성 유틸리티
├── exceptions/               #   커스텀 예외
├── paths/                    #   경로 유틸리티
├── values/                   #   값 타입 (proxy, delta, ...)
└── ...                       #   (기타 유틸리티 모듈)

tester/                       # 테스트 패키지 (cvp/ 미러링)
├── __init__.py
├── test_entrypoint.py        # cvp/entrypoint.py 테스트
├── liveness.py               # 공유 테스트 유틸리티
├── chrono/                   # cvp/chrono/ 테스트
├── chat/                     # cvp/chat/ 테스트
├── flow/                     # cvp/flow/ 테스트
├── maths/                    # cvp/maths/ 테스트
│   ├── bezier/
│   ├── equation/linear/
│   ├── geometry/
│   └── numeral/
└── ...                       # (cvp/ 구조와 동일)
```

### 그룹화 원칙

| 원칙 | 설명 | 예시 |
|------|------|------|
| **기능별 그룹** | 관련 기능을 하나의 디렉토리에 집중 | `ffmpeg/`, `maths/`, `ws/` |
| **라이브러리별 분류** | 외부 라이브러리 의존 코드를 분리 | `nodes/defaults/numpy/`, `nodes/defaults/opencv/` |
| **카테고리별 서브모듈** | 동일 도메인 내 기능 분류 | `numpy/array_creation/`, `numpy/mathematical/` |
| **인터페이스 믹스인** | `able/` 디렉토리에 인터페이스 집중 | `pygame/able/displayable.py` |
| **설정 미러링** | config 섹션이 기능 모듈과 1:1 대응 | `config/sections/font.py` ↔ `fonts/` |
| **테스트 미러링** | 소스와 동일 구조 유지 | `cvp/flow/node.py` → `tester/flow/test_node.py` |

### 최대 깊이: 3단계

```
cvp/nodes/defaults/numpy/array_creation/  # 최대 3단계
cvp/maths/geometry/bbox/                  # 최대 3단계
cvp/terminal/ansi/sgr/                    # 최대 3단계
```

3단계를 초과하지 않는다. 더 깊은 분류가 필요하면 파일명으로 구분한다.

### `__init__.py` 원칙

```python
# 대부분 비어 있음 (빈 파일 또는 인코딩만)
# -*- coding: utf-8 -*-
```

- `__init__.py`에 re-export 하지 않는다
- 임포트는 항상 전체 경로: `from cvp.flow.node import FlowNode`
- 예외: `cvp/__init__.py`에는 `__version__` 포함

### 특수 파일 역할

| 파일 | 위치 | 역할 |
|------|------|------|
| `__init__.py` | 모든 패키지 | 비어 있음 (패키지 표시용) |
| `__main__.py` | `cvp/` | CLI 진입점 (최소 코드) |
| `entrypoint.py` | `cvp/` | `main()` 함수 정의 |
| `arguments.py` | `cvp/` | argparse CLI 인자 파싱 |
| `variables.py` | `cvp/` | 환경 변수 및 전역 상수 |
| `liveness.py` | `tester/` | 테스트용 공유 유틸리티 |

---

## 20. 테스트 작성 패턴 가이드

### 20.1 기본 템플릿

모든 테스트 파일의 골격:

```python
# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvp.module.target import TargetClass


class TargetClassTestCase(TestCase):
    def test_기능_설명(self):
        # given
        target = TargetClass()

        # when
        result = target.some_method()

        # then
        self.assertEqual(expected, result)


if __name__ == "__main__":
    main()
```

### 20.2 setUp / tearDown — 리소스 관리

```python
from tempfile import TemporaryDirectory
from unittest import TestCase, main


class DatabaseTestCase(TestCase):
    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self._home = HomeDir(self._tmpdir.name)
        self._path = self._home.chat.get_database_path()
        self._chat = ChatDatabase(self._path, create_tables=True)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_insert_conversation(self):
        row_id = self._chat.insert_conversation("Test", datetime.now(UTC))
        self.assertEqual(1, row_id)
```

### 20.3 컨텍스트 매니저 중첩 — 임시 파일/디렉토리

```python
class BufferTestCase(TestCase):
    def test_lines_buffer(self):
        with TemporaryDirectory() as tmpdir:
            self.assertTrue(os.path.isdir(tmpdir))

            with NamedTemporaryFile("wt", dir=tmpdir) as f:
                with LinesBuffer(f.name, maxsize=10) as buffer:
                    self.assertEqual("", buffer.getvalue())
                    self.assertEqual(5, f.write("12345"))
                    f.flush()
                    buffer.update()
                    self.assertEqual("12345", buffer.getvalue())
```

### 20.4 예외 테스트 — assertRaises

```python
class StrEnumTestCase(TestCase):
    # 방법 1: 컨텍스트 매니저
    def test_unique_violation(self):
        with self.assertRaises(ValueError):
            @unique
            class _Test(_StrEnum):
                a = auto()
                b = "a"

    # 방법 2: 콜러블
    def test_type_error(self):
        argument = Argument(sig.parameters["arg0"])
        self.assertRaises(TypeError, lambda: argument.annotated_args)
```

### 20.5 비동기 테스트 — asyncio.run() 래핑

pytest fixture 미사용. `asyncio.run()`으로 직접 래핑한다.

```python
class TestWebSocketClient(TestCase):
    def test_client_connect_disconnect(self) -> None:
        async def run_test() -> None:
            async def echo_handler(websocket):
                async for message in websocket:
                    await websocket.send(f"Echo: {message}")

            server = await websockets.serve(echo_handler, "localhost", 18770)

            try:
                client = WebSocketClient("ws://localhost:18770")
                await client.connect()
                self.assertTrue(client.is_connected)
                await client.disconnect()
                self.assertFalse(client.is_connected)
            finally:
                server.close()
                await server.wait_closed()

        asyncio.run(run_test())
```

### 20.6 콜백 추적 — 리스트로 호출 기록

mock/patch 대신 리스트로 콜백 호출을 추적한다.

```python
class TestProtobufHandler(TestCase):
    def test_register_handler(self) -> None:
        handler = ProtobufHandler()
        called = []

        def msg_handler(data: bytes) -> Optional[bytes]:
            called.append(data)
            return b"response"

        handler.register(1, msg_handler)
        msg = ProtobufHandler.encode_message(1, b"test")
        response = handler.dispatch(msg)

        self.assertEqual([b"test"], called)
        self.assertEqual(b"response", response)
```

### 20.7 다중 TestCase 클래스 — 기능별 분리

한 파일에 여러 TestCase를 두어 관심사를 분리한다.

```python
class TestModbusTcpClientBasic(TestCase):
    def test_client_properties(self) -> None:
        client = ModbusTcpClient(host="127.0.0.1", port=15030)
        self.assertEqual(client.host, "127.0.0.1")
        self.assertFalse(client.is_connected)

    def test_client_connect_no_server(self) -> None:
        client = ModbusTcpClient(host="localhost", port=15031, timeout=1.0)
        result = client.connect()
        self.assertFalse(result)


class TestModbusTcpClientStartStop(TestCase):
    def test_start_stop_no_server(self) -> None:
        client = ModbusTcpClient(host="localhost", port=15033, timeout=1.0)
        client.start()
        self.assertTrue(client.is_running)
        client.stop()
        self.assertFalse(client.is_running)
```

### 20.8 @skipIf — 조건부 건너뛰기

외부 의존성(실행 파일, 서버 등)이 필요한 테스트:

```python
from shutil import which
from unittest import skipIf


class VersionTestCase(TestCase):
    @skipIf(not which("ffmpeg"), "Not found ffmpeg executable")
    def test_version(self):
        version = inspect_version()
        self.assertLessEqual(4, version.major)
```

### 20.9 데이터 주도 테스트 — 인라인 다중 검증

별도 파라미터화 라이브러리 없이, 한 테스트 메서드에서 여러 케이스를 검증:

```python
class CaseConverterTestCase(TestCase):
    def test_camel_case(self):
        expected = "helloWorld"
        self.assertEqual(expected, camel_case("hello_world"))
        self.assertEqual(expected, camel_case("HelloWorld"))
        self.assertEqual(expected, camel_case("hello-world"))
        self.assertEqual(expected, camel_case("hello world"))
        self.assertEqual(expected, camel_case("HELLO_WORLD"))
        self.assertEqual(expected, camel_case("helloWorld"))
```

### 20.10 직렬화 왕복 테스트 — roundtrip

```python
class DtypeTestCase(TestCase):
    def test_serialize_deserialize_int(self):
        dtype0 = Dtype(int)
        dtype1 = deserialize(serialize(dtype0), Dtype)
        self.assertEqual(dtype0, dtype1)
        self.assertEqual(dtype0.type, int)
        self.assertEqual("builtins.int", dtype0.path)

    def test_copy(self):
        dtype0 = Dtype(Path)
        self.assertEqual(copy(dtype0), dtype0)

    def test_deepcopy(self):
        dtype0 = Dtype(Path)
        self.assertEqual(deepcopy(dtype0), dtype0)
```

### 20.11 Property/Proxy 테스트 — 상태 동기화 검증

```python
class FFmpegTestCase(TestCase):
    def test_proxy(self):
        config = FFmpegConfig()
        proxy1 = config.create_ffmpeg_proxy()
        proxy2 = config.create_ffmpeg_proxy()

        self.assertEqual("ffmpeg", config.ffmpeg)
        self.assertEqual("ffmpeg", proxy1.get())
        self.assertEqual("ffmpeg", proxy2.get())

        config.ffmpeg = "0"
        self.assertEqual("0", proxy1.get())

        proxy1.set("1")
        self.assertEqual("1", config.ffmpeg)
        self.assertEqual("1", proxy2.get())
```

### 20.12 서버 테스트 — setUp/tearDown 패턴

```python
class TestModbusTcpServerConnection(TestCase):
    def setUp(self) -> None:
        self.datastore = ModbusDataStore()
        self.server = ModbusTcpServer(
            host="localhost",
            port=15024,
            datastore=self.datastore,
        )
        self.server.start()
        time.sleep(0.1)

    def tearDown(self) -> None:
        self.server.stop()

    def test_client_connection(self) -> None:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(("localhost", 15024))
            time.sleep(0.1)
            self.assertEqual(self.server.client_count, 1)
        finally:
            client.close()
```

### 20.13 헬퍼 메서드 — `_` 접두사 private 메서드

테스트 클래스 내 재사용 로직은 `_` 접두사 메서드로:

```python
class TestHubManager(TestCase):
    def _create_websocket_client(self, host: str, port: int) -> socket.socket:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        # ... WebSocket 핸드셰이크
        return client

    @staticmethod
    def _encode_binary_frame(data: bytes) -> bytes:
        # ... 프레임 인코딩 로직
        return bytes(frame)

    def test_hub_message(self) -> None:
        client = self._create_websocket_client("localhost", 19301)
        frame = self._encode_binary_frame(b"hello")
        # ... 테스트 로직
```

### 20.14 공유 테스트 유틸리티 — tester/liveness.py

```python
# -*- coding: utf-8 -*-

from functools import lru_cache
from pathlib import Path
from typing import Optional, TypeVar, Union, overload

from cvp.network.liveness import ServerLivenessProbe


@lru_cache
def get_project_root_path() -> Path:
    return Path(abspath(dirname(__file__))).parent


class TestServerLivenessProbe(ServerLivenessProbe):
    @classmethod
    def from_dotenv(cls, address_key: str, timeout_key: Optional[str] = None):
        address = get_project_root_dotenv_value(address_key)
        if address is None:
            return cls()
        return cls(address, timeout)

    def __bool__(self) -> bool:
        return self.is_alive()
```

### 20.15 자주 사용하는 Assertion 정리

| Assertion | 용도 | 예시 |
|-----------|------|------|
| `assertEqual(expected, actual)` | 값 동등 비교 | `self.assertEqual(30, result)` |
| `assertTrue(expr)` | 참 확인 | `self.assertTrue(client.is_connected)` |
| `assertFalse(expr)` | 거짓 확인 | `self.assertFalse(client.is_running)` |
| `assertIsInstance(obj, cls)` | 타입 확인 | `self.assertIsInstance(result, str)` |
| `assertIsNone(obj)` | None 확인 | `self.assertIsNone(response)` |
| `assertIsNotNone(obj)` | 비-None 확인 | `self.assertIsNotNone(session.origin)` |
| `assertIn(item, container)` | 포함 확인 | `self.assertIn("Echo", received)` |
| `assertRaises(exc, callable)` | 예외 발생 확인 | `self.assertRaises(TypeError, func)` |
| `assertLessEqual(a, b)` | 크기 비교 | `self.assertLessEqual(4, version.major)` |
| `assertGreater(a, b)` | 크기 비교 | `self.assertGreater(len(msgs), 0)` |
| `assertTupleEqual(a, b)` | 튜플 비교 | `self.assertTupleEqual((2, 1), btn.pivot)` |

### 20.16 테스트 작성 금지 사항

- **pytest fixture 미사용**: `conftest.py`, `@pytest.fixture` 사용 금지
- **mock/patch 최소화**: `unittest.mock` 대신 콜백 리스트 추적 패턴 사용
- **파라미터화 데코레이터 미사용**: `@parameterized` 등 미사용
- **테스트 데이터 외부 파일 미사용**: 인라인으로 테스트 데이터 정의
