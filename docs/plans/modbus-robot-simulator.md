# Modbus 시뮬레이터 연동 — cvpa 측 작업 플랜

> 본 문서는 **app.cvp.run** 저장소의 `docs/plans/modbus-robot-simulator.md` 를
> cvpa (Python) 측에서 실행하기 위한 작업 플랜이다.
> app.cvp.run 측 문서가 양 저장소의 **WS 메시지 스펙**과 **로봇 카탈로그 스키마**의
> single source of truth 이며, 본 문서는 그 스펙을 cvpa 저장소에서 구현하는
> 책임·구조·순서를 정의한다.
>
> 선행·참조:
>
> - `../app.cvp.run/docs/plans/modbus-robot-simulator.md`
> - `../app.cvp.run/docs/plans/agent-connection-state-machine.md` (envelope 프로토콜 원형)
> - `docs/ros2-integration-plan.md` (Envelope 디자인 원형)

---

## 0. 역할 분담 확인

| 관심사                          | 담당                                 |
| ------------------------------- | ------------------------------------ |
| UI 라우트/컴포넌트/3D 뷰어      | app.cvp.run                          |
| 로봇 카탈로그 (DH, mesh)        | app.cvp.run (`assets/robot-catalog`) |
| Worker/DO의 `modbus.*` fan-out  | app.cvp.run                          |
| **Modbus TCP server**           | **cvpa**                             |
| **`modbus.*` WS 핸들러**        | **cvpa**                             |
| **가상 6축 로봇팔 시뮬레이터**  | **cvpa**                             |
| **envelope 프로토콜·상태 머신** | **cvpa** (state-machine 플랜과 공용) |

cvpa가 Modbus 레지스터에 **각도 raw 값**을 채워 UI로 전달하면, 카탈로그·binding·DH 해석은 UI 책임이므로 cvpa는 카탈로그와 무관하다.

---

## 1. 현황 (As-Is)

| 구성요소                   | 상태                                            |
| -------------------------- | ----------------------------------------------- |
| `ws/client.py`             | `WebSocketClient` — backoff 재연결만 존재       |
| `ws/handler.py`            | `MessageDispatcher` — top-level `type` 기반 라우팅 |
| `apps/agent/client.py`     | `AgentClient` — `/connect` ticket → WS, `ServiceManager` |
| `service/` (manager/process/server) | gRPC over Unix socket 기반 `ProcessService` |
| envelope 프로토콜          | **없음** — raw JSON, `data` 필드 컨벤션 없음    |
| 상태 머신                  | **없음** — `agent.hello`/`heartbeat.*` 미구현   |
| Modbus                     | **없음**                                        |
| 가상 로봇 시뮬레이터       | **없음**                                        |

---

## 2. 선행 의존성 — envelope / state machine

`modbus.*` 메시지는 envelope(`{type, id, ts, data}`) 위에 정의되므로, `agent-connection-state-machine.md` **Phase 3 (cvpa 상태 머신)** 가 선행 또는 병행되어야 한다.

### 2.1 `src/cvpa/ws/protocol.py` (신규)

- Envelope dataclass (`type`, `id`, `ts`, `data`)
- Close code enum (1000/1001/1011/4001–4030)
- 프로토콜 상수 (`HEARTBEAT_INTERVAL_MS` 등; 서버 `server.hello` 값이 우선)

### 2.2 `src/cvpa/ws/state_machine.py` (신규)

- `AgentState` enum (`IDLE / CONNECTING / HANDSHAKING / ACTIVE / STOPPING / STOPPED / SUSPENDED / TERMINATED / BACKOFF`)
- 전이표: `agent-connection-state-machine.md §12.2`

### 2.3 `src/cvpa/ws/handler.py` 확장

- 현 구현은 raw top-level `type`만 보는데, envelope 수신 시 `data`를 핸들러로 건네도록 확장.
- 호환성: legacy top-level 핸들러도 전환기간 동안 유지.

### 2.4 `src/cvpa/client/ticket.py`

- 에러 응답 `{code, message}` 파싱 → 상태 머신 분기에 사용.

> 이 섹션은 본 플랜의 모든 Modbus 작업이 기대는 기반이다. 별 PR로 먼저 머지하는 것을 권장한다.

---

## 3. Modbus TCP 서버 모듈

### 3.1 레이아웃 (신규)

```
src/cvpa/modbus/
  __init__.py
  types.py           # Area enum, Subscription, ChangeRecord
  store.py           # 4영역 in-memory store + dirty tracking
  server.py          # Modbus TCP server (asyncio)
  sampler.py         # 구독자별 polling + diff + 다중구독 합성
```

### 3.2 `types.py`

```python
from dataclasses import dataclass
from enum import StrEnum

class Area(StrEnum):
    HOLDING  = "holding"
    INPUT    = "input"
    COIL     = "coil"
    DISCRETE = "discrete"

@dataclass(frozen=True)
class AreaSpec:
    kind: Area
    address: int
    length: int

@dataclass
class Subscription:
    subscription_id: str
    unit_id: int
    areas: list[AreaSpec]
    min_interval_ms: int
    # internal
    last_snapshot: dict[Area, list]  # 마지막 송신 상태
```

### 3.3 `store.py`

- 4영역(word × 65536, bit × 65536) in-memory store.
- write 시 dirty bitmap에 표시.
- `diff(area, address, length, last: list) -> list[ChangeRecord]` 로 변경분 계산.
- thread/async safety: 단일 event loop 가정, 락 없이 coroutine 경계 내에서만 접근.

### 3.4 `server.py`

- 의존성: **`pymodbus>=3.x` (비동기)**. `pyproject.toml` 에 추가.
- listen: `127.0.0.1:<port>` (agent별 격리, port는 CLI/env로 configurable).
- `StartAsyncTcpServer(context=..., address=...)` 기반.
- `context` 는 `store.py` 의 4영역을 wrap.

### 3.5 `sampler.py` — 구독 샘플링 + 합성

- 각 `Subscription` 에 대해 `asyncio.create_task` 로 루프를 띄움.
- 루프: `await asyncio.sleep(min_interval_ms / 1000)` → `store.diff(...)` → 변경 시 `modbus.delta` 송신.
- **다중 구독자 합성 (app.cvp.run 플랜 §12 미해결 #3)**: 동일 `(unit_id, area, address_range)` 에 대해 가장 짧은 `min_interval_ms` 로 단일 샘플링 후 fan-out. 1차 릴리스는 단순 구현(각 구독자 독립 루프) 도 허용하되, TODO로 명시.
- 첫 구독 시 1회 `modbus.snapshot` 즉시 송신.

---

## 4. `modbus.*` WS 핸들러

### 4.1 레이아웃

```
src/cvpa/apps/agent/
  modbus_handlers.py    # 신규 — 구독 레지스트리 + 메시지 처리
```

### 4.2 메시지 카탈로그 (app.cvp.run 플랜 §4.2)

| type                 | 방향   | 처리                                                            |
| -------------------- | ------ | --------------------------------------------------------------- |
| `modbus.subscribe`   | UI→cvpa | 신규 `Subscription` 등록 → sampler task 기동 → `modbus.snapshot` 1회 |
| `modbus.unsubscribe` | UI→cvpa | sampler task 취소 + 레지스트리 제거                             |
| `modbus.write`       | UI→cvpa | (Phase 8) store write → `modbus.write_ack`                      |
| `modbus.snapshot`    | cvpa→UI | 구독 시작 시 1회                                                |
| `modbus.delta`       | cvpa→UI | 변경분만                                                        |
| `modbus.error`       | cvpa→UI | `connection_lost` / `exception_code` / `timeout` 등             |

### 4.3 `AgentClient` 변경 (`src/cvpa/apps/agent/client.py`)

- `ModbusServer`, `SubscriptionRegistry` 를 소유.
- `start()` 시점에 Modbus 서버 기동, `stop()` 시 정리.
- `MessageDispatcher` 에 `modbus.*` 핸들러 등록.
- WS close 시 **모든 구독 cleanup** (sampler task 취소).

### 4.4 에러 응답 규약

- 입력 검증 실패 (addr overflow 등): `modbus.error {code: "invalid_request", message}`.
- Modbus 내부 예외: `modbus.error {code: "exception_code", data: {fn, exc}}`.
- Agent offline 은 Worker/DO 책임이므로 cvpa 는 발송하지 않음.

---

## 5. 가상 6축 로봇팔 시뮬레이터 프로세스

### 5.1 레이아웃

```
src/cvpa/apps/robot_sim/
  __init__.py
  __main__.py           # --grpc-socket=... 인자 받아 ProcessService로 기동
  simulator.py          # trajectory 생성 (idle / joint_sweep / target_pose)
  modbus_writer.py      # cvpa Modbus TCP server에 holding register write
```

### 5.2 기동 경로

- `AgentClient.services.add("robot_sim", [...], on_message=...)` 로 ProcessService 등록.
- ProcessService 의 `--grpc-socket` 인자 + 추가로 `--modbus-host`, `--modbus-port` 전달.
- 시뮬레이터는 **cvpa Modbus TCP server 에 client 로 접속**하여 holding register 에 joint 값을 write.

### 5.3 데이터 포맷 (UI 와의 암묵 계약)

- `holding[0..5]` = 6축 joint 각도, `int16` 스케일 0.001 rad/LSB (UI binding 기본값과 일치).
- 추가 워드 (status, cycle count) 은 선택.
- 실제 해석은 UI 측 `_BindingPanel` 에서 overridable. cvpa 는 기본 매핑만 제공하고 스펙은 문서화.

### 5.4 envelope 메시지 (시뮬레이터 ↔ cvpa)

`agent ↔ robot_sim` 은 기존 ROS2 플랜의 envelope 패턴을 재사용:

| type                     | 방향            | 설명                              |
| ------------------------ | --------------- | --------------------------------- |
| `robot_sim.set_mode`     | agent→sim       | `idle / joint_sweep / target_pose` |
| `robot_sim.status`       | sim→agent       | 주기적 상태 보고 (optional)       |

(UI→agent 의 제어 메시지 는 Phase 8 `modbus.write` 경로로 대체 가능하므로, 1차 릴리스에서는 sim 기본모드 `joint_sweep` 만 지원하고 set_mode 는 후속.)

---

## 6. 테스트

`tester/` 레이아웃을 그대로 따름.

```
tester/modbus/
  __init__.py
  test_store.py         # diff / snapshot / dirty tracking
  test_sampler.py       # min_interval_ms, 다중 구독 합성
  test_server.py        # pymodbus client 로 read/write 왕복
tester/apps/agent/
  test_modbus_handlers.py   # subscribe/unsubscribe/write 라우팅, error 코드
tester/apps/robot_sim/
  __init__.py
  test_simulator.py     # trajectory 함수 단위
  test_modbus_writer.py # 기동 후 register 값 검증
tester/ws/
  test_state_machine.py # (선행 Phase) envelope + state 전이
  test_protocol.py      # close code, envelope serialize
```

---

## 7. 의존성 변경 (`pyproject.toml`)

- 추가: `pymodbus>=3.6` (BSD-3, 호환 OK)
- 기존 활용: `asyncio`, `websockets`, `grpcio`, `numpy` (trajectory).

---

## 8. Phase 분할

본 플랜의 Phase 는 app.cvp.run 측 Phase 와 동기화된다.

### Phase C0 — 공용 스펙 미러 (선행)

- [ ] app.cvp.run `docs/plans/modbus-protocol.md` 를 본 저장소에서 참조 가능하게 한다
  - 방식 후보: submodule / 복사 스크립트 / 링크 문서. state-machine 플랜 §18 #6 결정과 동일 방식 채택.
- [ ] `docs/modbus-robot-simulator-plan.md` (본 문서) 유지·갱신

### Phase C1 — envelope / state machine (state-machine 플랜과 공용)

- [ ] `src/cvpa/ws/protocol.py` — envelope/close code/상수
- [ ] `src/cvpa/ws/state_machine.py` — 전이표 구현
- [ ] `src/cvpa/ws/client.py` — state machine 이 client 를 소유하도록 리팩터
- [ ] `src/cvpa/ws/handler.py` — envelope `data` dispatch
- [ ] `src/cvpa/client/ticket.py` — 에러 `code` 파싱
- [ ] `tester/ws/test_state_machine.py`, `test_protocol.py`
- [ ] **빌드 + 테스트 → commit (`feat(ws): Add envelope protocol and state machine`)**

### Phase C2 — Modbus TCP server (단독 검증)

- [ ] `pymodbus` 의존성 추가
- [ ] `src/cvpa/modbus/{types,store,server,sampler}.py`
- [ ] `tester/modbus/test_store.py`, `test_sampler.py`, `test_server.py`
- [ ] CLI/env 로 listen host/port configurable
- [ ] **빌드 + 테스트 → commit (`feat(modbus): Add modbus tcp server and sampler`)**

### Phase C3 — `modbus.*` WS 핸들러

- [ ] `src/cvpa/apps/agent/modbus_handlers.py`
- [ ] `AgentClient` 에 `ModbusServer` + 구독 레지스트리 연동
- [ ] WS close 시 구독 cleanup
- [ ] `tester/apps/agent/test_modbus_handlers.py`
- [ ] **빌드 + 테스트 → commit (`feat(agent): Route modbus.* messages over ws envelope`)**

### Phase C4 — 가상 6축 로봇팔 시뮬레이터

- [ ] `src/cvpa/apps/robot_sim/__main__.py` + `simulator.py` + `modbus_writer.py`
- [ ] `AgentClient` 에서 ProcessService 로 등록 (CLI 플래그 `--with-robot-sim`)
- [ ] 기본 trajectory `joint_sweep` 동작 확인
- [ ] `tester/apps/robot_sim/`
- [ ] **엔드투엔드 수동 검증 (cvpa ↔ UI mock) → commit (`feat(agent): Add virtual 6-dof arm simulator`)**

### Phase C5 — E2E 연동 (app.cvp.run Phase 6 와 정렬)

- [ ] app.cvp.run Phase 5 (Worker WS envelope + `/subscribe`) 완료 대기
- [ ] 로컬에서 Worker dev + cvpa 연결 → UI `modbus` 페이지에서 snapshot/delta 수신 확인
- [ ] UI `robot` 페이지에서 joint 각도가 3D 모델로 렌더되는지 확인
- [ ] 재연결 / 중복 구독 / 에러 경로 시나리오 점검

### Phase C6 — (옵션) 양방향 쓰기

- [ ] `modbus.write` 수신 → store write → `modbus.write_ack`
- [ ] 권한 모델: 기본 read-only, write 는 UI 측 토글 필요 (`JointSlider` write 모드)
- [ ] 에러 코드: `read_only`, `out_of_range`, `invalid_kind`

---

## 9. 의존성 그래프

```
C0 (선행, 가벼움)
 │
 ▼
C1 envelope / state machine
 │
 ├──► C2 Modbus server (독립 검증 가능)
 │     │
 │     ▼
 └──► C3 modbus.* 핸들러 (C1 + C2 필요)
        │
        ▼
       C4 시뮬레이터 (C2 필요; C3 와 병렬 가능)
        │
        ▼
       C5 E2E (app.cvp.run Phase 5 완료 후)
        │
        ▼
       C6 양방향 쓰기 (옵션)
```

---

## 10. 리스크 & 완화

| 리스크                                           | 완화                                                                                          |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| envelope 도입이 state-machine 플랜과 병행 충돌   | C1 을 **state-machine 플랜 Phase 3 PR 과 동일 브랜치**로 진행. 양 플랜 동기 유지              |
| pymodbus API 변경 (3.x 내 minor)                 | `pymodbus` pin (`>=3.6,<4`) + CI lock                                                         |
| 다중 UI 세션에서 같은 영역 중복 샘플링           | 1차는 구독별 독립 루프 허용, 합성은 측정 후 도입 (plan §12 미해결 #3)                          |
| agent 별 Modbus 포트 충돌                        | listen host 기본 `127.0.0.1`, port 기본 `5020`, `--modbus-port` 로 override                   |
| WS close 시 구독 leak                            | `AgentClient.stop()` + state machine `ACTIVE → BACKOFF` 전이 훅에서 모든 sampler task 취소    |
| Mock(UI)과 Real(cvpa) 데이터 포맷 미세 차이      | holding register 스케일(`0.001 rad/LSB`)·순서(base→tip) 를 본 문서 §5.3 에서 **계약으로 고정** |

---

## 11. 미해결 결정 (후속 합의 필요)

| #   | 질문                                                                  | 기본 제안                                    |
| --- | --------------------------------------------------------------------- | -------------------------------------------- |
| 1   | 공용 스펙 미러 방식 (submodule vs 복사 스크립트)                      | submodule (state-machine 플랜 결정과 동일)   |
| 2   | 다중 구독 sampler 합성 1차 구현 포함 여부                             | 1차는 구독별 독립 루프, 측정 후 합성         |
| 3   | Modbus 기본 port 및 listen host                                       | `127.0.0.1:5020` (agent 단독 격리 가정)      |
| 4   | 시뮬레이터 기본 모드 (`joint_sweep` vs `idle`)                        | `joint_sweep` — UI mock 없이도 변화 관측     |
| 5   | `robot_sim.set_mode` 메시지를 1차 릴리스에 포함할지                   | 제외 — `modbus.write` 경로(C6) 로 대체       |
| 6   | holding register 스케일 (rad × 1e3 vs 0.01°)                          | `int16, 1 LSB = 0.001 rad` — UI 기본값과 일치 |

> 결정 후 본 섹션 업데이트 + 영향 Phase 체크리스트 반영.

---

## 12. 참고

- `../app.cvp.run/docs/plans/modbus-robot-simulator.md` — UI/Worker/DB 측 플랜
- `../app.cvp.run/docs/plans/agent-connection-state-machine.md` — envelope 프로토콜 원형
- `docs/ros2-integration-plan.md` — Envelope 디자인 원형, ProcessService 사용 패턴
- `src/cvpa/ws/client.py`, `src/cvpa/ws/handler.py` — 현 WS 계층
- `src/cvpa/apps/agent/client.py`, `src/cvpa/service/manager.py` — 현 agent/service 계층
- pymodbus: https://github.com/pymodbus-dev/pymodbus
