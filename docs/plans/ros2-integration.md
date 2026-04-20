# ROS2 Integration Plan for app.cvp.run Monitoring

## 1. Overview

CVPA(Computer Vision Player Agent)에 ROS2를 연동하여 app.cvp.run 웹 대시보드에서
로봇/CV 시스템을 실시간 모니터링하고 제어하는 기능을 구현한다.

### 1.1 현재 아키텍처

```
app.cvp.run (Web UI)
    | WebSocket (JSON, Bearer Token 인증)
    v
CVPA Agent (Python 3.14+, asyncio)
    |-- AgentClient: WebSocket 연결 + ServiceManager 관리
    |-- MessageDispatcher: type 필드 기반 메시지 라우팅
    |-- ServiceManager: 서비스 생명주기 관리
    |       |
    |       v
    |   ProcessService (gRPC over Unix Socket)
    |       |-- Channel(stream Envelope) -> stream Envelope  (양방향 스트리밍)
    |       |-- Heartbeat(Pit) -> Pat  (생존 확인)
    |       +-- Shutdown(Empty) -> Empty  (종료)
    |
    +-- Envelope { type, id, payload(bytes), metadata(map) }
```

### 1.2 목표 아키텍처

```
app.cvp.run (Web UI)
    | WebSocket
    v
CVPA Agent
    | gRPC (Envelope 양방향 스트림)
    v
ROS2 Bridge Service (신규 ProcessService)
    | rclpy (subscribe/publish/service call)
    v
ROS2 Nodes (camera, detector, robot, etc.)
```

ROS2 Bridge Service는 기존 `ProcessService`로 관리되며, `--grpc-socket` 인자를 받아
gRPC 서버를 시작하고 CVPA Agent와 `Envelope` 기반으로 통신한다.

---

## 2. 추천 기능 상세

### 2.1 시스템 인트로스펙션 (System Introspection)

웹 UI에서 ROS2 시스템의 전체 구조를 파악할 수 있는 기능.

#### 2.1.1 노드 탐색

| 항목 | 스펙 |
|------|------|
| rclpy API | `node.get_node_names_and_namespaces()` -> `List[Tuple[str, str]]` |
| 반환 데이터 | `[("camera_node", "/"), ("detector", "/cv"), ...]` |
| 폴링 주기 | 5초 |
| Envelope type | `ros2.introspection.nodes` |

#### 2.1.2 토픽 탐색

| 항목 | 스펙 |
|------|------|
| rclpy API | `node.get_topic_names_and_types()` -> `List[Tuple[str, List[str]]]` |
| 반환 데이터 | `[("/camera/image_raw", ["sensor_msgs/msg/Image"]), ...]` |
| 추가 정보 | 각 토픽의 publisher/subscriber 수 |
| Envelope type | `ros2.introspection.topics` |

#### 2.1.3 서비스 탐색

| 항목 | 스펙 |
|------|------|
| rclpy API | `node.get_service_names_and_types()` -> `List[Tuple[str, List[str]]]` |
| Envelope type | `ros2.introspection.services` |

#### 2.1.4 노드별 상세 정보

| 항목 | 스펙 |
|------|------|
| Publisher 목록 | `node.get_publisher_names_and_types_by_node(name, namespace)` |
| Subscriber 목록 | `node.get_subscriber_names_and_types_by_node(name, namespace)` |
| Service 목록 | `node.get_service_names_and_types_by_node(name, namespace)` |
| Client 목록 | `node.get_client_names_and_types_by_node(name, namespace)` |
| Envelope type | `ros2.introspection.node_detail` |

---

### 2.2 토픽 실시간 모니터링 (Topic Streaming)

선택한 토픽의 데이터를 실시간으로 웹에 스트리밍하는 핵심 기능.

#### 2.2.1 범용 토픽 구독

웹 UI에서 토픽을 선택하면 Bridge가 동적으로 subscription을 생성한다.

**요청 Envelope:**
```
type: "ros2.topic.subscribe"
payload: {
    "topic": "/odom",
    "msg_type": "nav_msgs/msg/Odometry",
    "throttle_ms": 100,       # 최소 전송 간격 (ms)
    "queue_size": 1            # 최신 메시지만 유지
}
```

**응답 Envelope (스트림):**
```
type: "ros2.topic.data"
metadata: {"topic": "/odom"}
payload: <JSON-serialized message>
```

**구독 해제:**
```
type: "ros2.topic.unsubscribe"
payload: {"topic": "/odom"}
```

#### 2.2.2 주요 모니터링 대상 토픽 및 메시지 스펙

##### sensor_msgs/msg/Image

```
std_msgs/Header header       # stamp(sec, nanosec) + frame_id
uint32 height
uint32 width
string encoding              # rgb8, bgr8, mono8, 16UC1, 32FC1 등
uint8 is_bigendian
uint32 step                  # row 당 바이트 수
uint8[] data                 # size = step * height
```
- 토픽: `/camera/image_raw`
- QoS: BEST_EFFORT, VOLATILE, depth=1 (프레임 드롭 허용)
- 참고: 웹 전송 시 CompressedImage 사용 권장

##### sensor_msgs/msg/CompressedImage

```
std_msgs/Header header
string format                # "jpeg", "png", "rgb8; jpeg compressed bgr8" 등
uint8[] data                 # 압축된 이미지 바이트
```
- 토픽: `/camera/image_raw/compressed`
- QoS: BEST_EFFORT, VOLATILE, depth=1
- 웹 전송: payload를 binary Envelope로 직접 전달 (base64 불필요)
- 파라미터 조정:
  - `<topic>/compressed/format`: `"jpeg"` (기본) 또는 `"png"`
  - `<topic>/compressed/jpeg_quality`: 1-100 (기본 80, 웹용 60 권장)

##### sensor_msgs/msg/LaserScan

```
std_msgs/Header header
float32 angle_min            # 시작 각도 (rad)
float32 angle_max            # 종료 각도 (rad)
float32 angle_increment      # 측정 간 각도 (rad)
float32 time_increment       # 측정 간 시간 (sec)
float32 scan_time            # 스캔 간 시간 (sec)
float32 range_min            # 최소 유효 거리 (m)
float32 range_max            # 최대 유효 거리 (m)
float32[] ranges             # 거리 데이터
float32[] intensities        # 강도 데이터 (선택)
```
- 토픽: `/scan`
- QoS: BEST_EFFORT, VOLATILE, depth=5

##### sensor_msgs/msg/Imu

```
std_msgs/Header header
geometry_msgs/Quaternion orientation          # x, y, z, w
float64[9] orientation_covariance            # 3x3 행렬 (row-major)
geometry_msgs/Vector3 angular_velocity       # rad/sec
float64[9] angular_velocity_covariance
geometry_msgs/Vector3 linear_acceleration    # m/s^2
float64[9] linear_acceleration_covariance
```
- 토픽: `/imu/data`
- QoS: BEST_EFFORT, VOLATILE, depth=5

##### nav_msgs/msg/Odometry

```
std_msgs/Header header              # frame_id = odom
string child_frame_id               # base_link
geometry_msgs/PoseWithCovariance pose
    geometry_msgs/Pose pose
        Point position              # x, y, z (float64)
        Quaternion orientation      # x, y, z, w (float64)
    float64[36] covariance          # 6x6 행렬
geometry_msgs/TwistWithCovariance twist
    geometry_msgs/Twist twist
        Vector3 linear              # m/s
        Vector3 angular             # rad/s
    float64[36] covariance
```
- 토픽: `/odom`
- QoS: BEST_EFFORT, VOLATILE, depth=5

##### sensor_msgs/msg/JointState

```
std_msgs/Header header
string[] name                # 관절 이름
float64[] position           # rad (revolute) 또는 m (prismatic)
float64[] velocity           # rad/s 또는 m/s
float64[] effort             # N*m 또는 N
```
- 토픽: `/joint_states`
- QoS: RELIABLE, VOLATILE, depth=10

##### geometry_msgs/msg/Twist (제어 명령)

```
Vector3 linear               # x=전진, y=횡이동, z=수직 (m/s)
Vector3 angular              # x=roll, y=pitch, z=yaw (rad/s)
```
- 토픽: `/cmd_vel`
- QoS: RELIABLE, VOLATILE, depth=1

##### tf2_msgs/msg/TFMessage

```
geometry_msgs/TransformStamped[] transforms
    std_msgs/Header header         # parent frame
    string child_frame_id
    geometry_msgs/Transform transform
        Vector3 translation        # x, y, z
        Quaternion rotation        # x, y, z, w
```
- 토픽: `/tf` (동적), `/tf_static` (정적)
- QoS (동적): RELIABLE, VOLATILE, depth=100
- QoS (정적): RELIABLE, TRANSIENT_LOCAL, depth=1

#### 2.2.3 토픽 주파수 모니터링

각 토픽의 실제 publish rate를 측정하여 기대치와 비교한다.

| 항목 | 설명 |
|------|------|
| 측정 방식 | 최근 N개 메시지의 timestamp 간격 평균 |
| 윈도우 크기 | 100 메시지 |
| 보고 주기 | 2초 |
| Envelope type | `ros2.topic.rate` |
| payload | `{"topic": "/scan", "rate_hz": 9.8, "expected_hz": 10.0}` |

---

### 2.3 진단 및 헬스체크 (Diagnostics & Health)

#### 2.3.1 /diagnostics 토픽 연동

##### diagnostic_msgs/msg/DiagnosticArray

```
std_msgs/Header header
DiagnosticStatus[] status
```

##### diagnostic_msgs/msg/DiagnosticStatus

```
byte OK=0, WARN=1, ERROR=2, STALE=3

byte level
string name              # 컴포넌트 이름 (예: "camera: Driver Status")
string message           # 상태 설명
string hardware_id       # 하드웨어 식별자
KeyValue[] values        # 상세 진단 데이터
    string key
    string value
```
- 토픽: `/diagnostics`
- QoS: RELIABLE, VOLATILE, depth=10
- Envelope type: `ros2.diagnostics`
- 웹 UI: 컴포넌트별 상태 표시 (OK=초록, WARN=노랑, ERROR=빨강, STALE=회색)

#### 2.3.2 노드 생존 확인

| 방식 | 설명 |
|------|------|
| 주기적 인트로스펙션 | `get_node_names()`로 노드 목록 갱신 (5초 주기) |
| 이전 목록과 비교 | 사라진 노드 = 다운, 새 노드 = 시작 |
| Envelope type | `ros2.health.nodes` |
| payload | `{"alive": [...], "died": [...], "new": [...]}` |

#### 2.3.3 Lifecycle 노드 상태 관리

ROS2 Lifecycle 노드는 상태 머신을 가진다:

```
         configure          activate
[Unconfigured] -------> [Inactive] -------> [Active]
       ^                    |                   |
       |     cleanup        |    deactivate     |
       +--------------------+<------------------+
       |                                        |
       +----------> [Finalized] <---------------+
                       shutdown
```

| 항목 | 스펙 |
|------|------|
| 상태 조회 서비스 | `/<node>/get_state` |
| 상태 전환 서비스 | `/<node>/change_state` |
| 이벤트 토픽 | `/<node>/transition_event` |
| 유효 전이 조회 | `/<node>/get_available_transitions` |
| Envelope type | `ros2.lifecycle.state` (조회), `ros2.lifecycle.transition` (전환 요청) |

---

### 2.4 카메라/영상 스트리밍 (Video Streaming)

CV 프로젝트의 핵심 기능. 웹 브라우저에서 카메라 영상과 CV 결과를 실시간으로 확인한다.

#### 2.4.1 압축 이미지 스트리밍

| 항목 | 스펙 |
|------|------|
| 소스 토픽 | `/camera/image_raw/compressed` (sensor_msgs/CompressedImage) |
| 전송 방식 | Binary Envelope (payload = JPEG 바이트) |
| metadata | `{"topic": "...", "format": "jpeg", "width": "640", "height": "480"}` |
| QoS | BEST_EFFORT, VOLATILE, depth=1 |
| 프레임 제한 | throttle_ms=33 (약 30fps), 웹 UI에서 조절 가능 |
| Envelope type | `ros2.image.compressed` |

#### 2.4.2 CV 결과 오버레이

| 항목 | 설명 |
|------|------|
| 소스 | CV 노드가 publish하는 결과 토픽 (커스텀 메시지) |
| 전송 데이터 | 바운딩 박스, 클래스 라벨, confidence score |
| Envelope type | `ros2.cv.detections` |
| 렌더링 | 웹 Canvas에서 이미지 위에 오버레이 |

예시 payload:
```json
{
  "header": {"stamp": {"sec": 1234567890, "nanosec": 0}, "frame_id": "camera"},
  "detections": [
    {
      "class": "person",
      "confidence": 0.95,
      "bbox": {"x": 100, "y": 50, "width": 200, "height": 300}
    }
  ]
}
```

#### 2.4.3 멀티 카메라 지원

- 여러 카메라 토픽을 동시 구독
- 웹 UI에서 그리드/탭 레이아웃으로 표시
- 각 카메라별 독립 throttle 설정

---

### 2.5 로그 스트리밍 (Log Streaming)

#### 2.5.1 /rosout 토픽

##### rcl_interfaces/msg/Log

```
byte DEBUG=10, INFO=20, WARN=30, ERROR=40, FATAL=50

builtin_interfaces/Time stamp
uint8 level
string name              # logger 이름 (보통 노드 이름)
string msg               # 로그 메시지
string file              # 소스 파일
string function          # 함수 이름
uint32 line              # 라인 번호
```
- 토픽: `/rosout`
- QoS: RELIABLE, TRANSIENT_LOCAL, depth=1000 (히스토리 보존)
- Envelope type: `ros2.log`

#### 2.5.2 웹 UI 기능

- 로그 레벨별 필터링 (DEBUG/INFO/WARN/ERROR/FATAL)
- 노드별 필터링
- 실시간 스트리밍 + 스크롤백
- 검색 기능

---

### 2.6 원격 제어 (Remote Control)

웹 UI에서 ROS2 시스템을 제어하는 양방향 기능.

#### 2.6.1 서비스 호출

**요청 Envelope:**
```
type: "ros2.service.call"
payload: {
    "service": "/trigger_calibration",
    "srv_type": "std_srvs/srv/Trigger",
    "request": {}
}
```

**응답 Envelope:**
```
type: "ros2.service.response"
metadata: {"service": "/trigger_calibration"}
payload: {"success": true, "message": "Calibration complete"}
```

| 항목 | 스펙 |
|------|------|
| rclpy API | `node.create_client(srv_type, srv_name)` |
| 타임아웃 | `client.wait_for_service(timeout_sec=5.0)` |
| 호출 | `client.call_async(request)` -> `Future` |

#### 2.6.2 파라미터 조정

| 항목 | 스펙 |
|------|------|
| rclpy API | `AsyncParameterClient(node, remote_node_name)` |
| 파라미터 조회 | `client.list_parameters()`, `client.get_parameters(names)` |
| 파라미터 설정 | `client.set_parameters(parameters)` |
| Envelope type (조회) | `ros2.param.list`, `ros2.param.get` |
| Envelope type (설정) | `ros2.param.set` |

**조회 요청:**
```
type: "ros2.param.get"
payload: {
    "node": "/detector",
    "names": ["confidence_threshold", "nms_threshold"]
}
```

**설정 요청:**
```
type: "ros2.param.set"
payload: {
    "node": "/detector",
    "parameters": [
        {"name": "confidence_threshold", "value": 0.7}
    ]
}
```

#### 2.6.3 토픽 Publish (제어 명령)

**요청 Envelope:**
```
type: "ros2.topic.publish"
payload: {
    "topic": "/cmd_vel",
    "msg_type": "geometry_msgs/msg/Twist",
    "message": {
        "linear": {"x": 0.5, "y": 0.0, "z": 0.0},
        "angular": {"x": 0.0, "y": 0.0, "z": 0.1}
    }
}
```

---

## 3. QoS 프로파일 가이드

모니터링 목적에 따른 권장 QoS 설정:

| 데이터 유형 | Reliability | Durability | History | Depth | 이유 |
|-------------|-------------|------------|---------|-------|------|
| 카메라 이미지 | BEST_EFFORT | VOLATILE | KEEP_LAST | 1 | 프레임 드롭 > 지연 |
| LaserScan | BEST_EFFORT | VOLATILE | KEEP_LAST | 5 | 실시간 센서 |
| IMU | BEST_EFFORT | VOLATILE | KEEP_LAST | 5 | 고주파 센서 |
| Odometry | BEST_EFFORT | VOLATILE | KEEP_LAST | 5 | 빈번한 업데이트 |
| /tf | RELIABLE | VOLATILE | KEEP_LAST | 100 | 변환 누락 방지 |
| /tf_static | RELIABLE | TRANSIENT_LOCAL | KEEP_LAST | 1 | 늦은 구독자 지원 |
| /diagnostics | RELIABLE | VOLATILE | KEEP_LAST | 10 | 진단 누락 방지 |
| /rosout | RELIABLE | TRANSIENT_LOCAL | KEEP_LAST | 1000 | 로그 히스토리 |
| /joint_states | RELIABLE | VOLATILE | KEEP_LAST | 10 | 상태 정확성 |
| /cmd_vel | RELIABLE | VOLATILE | KEEP_LAST | 1 | 최신 명령만 유효 |

**호환성 주의사항:**

- Publisher=BEST_EFFORT + Subscriber=RELIABLE → 통신 불가
- Publisher=VOLATILE + Subscriber=TRANSIENT_LOCAL → 통신 불가
- Bridge의 QoS는 대상 토픽의 publisher QoS와 호환되어야 함
- 런타임에 `SubscriptionEventCallbacks.incompatible_qos`로 불일치 감지

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy

QOS_SENSOR = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=1
)

QOS_RELIABLE = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10
)

QOS_TF_STATIC = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
    history=HistoryPolicy.KEEP_LAST,
    depth=1
)
```

---

## 4. DDS Discovery 설정

### 4.1 Domain ID

| 항목 | 설명 |
|------|------|
| 환경변수 | `ROS_DOMAIN_ID` |
| 기본값 | 0 |
| 안전 범위 | 0-101 (크로스 플랫폼) |
| 프로그래밍 설정 | `rclpy.init(domain_id=42)` |
| 격리 | 같은 Domain ID의 노드만 서로 발견 |

### 4.2 Discovery 방식 선택

| 방식 | 장점 | 단점 | 적합한 경우 |
|------|------|------|------------|
| 멀티캐스트 (기본) | 설정 불필요 | O(N^2) 트래픽, 멀티캐스트 필요 | 소규모, 단일 네트워크 |
| Discovery Server | 낮은 트래픽, 멀티캐스트 불필요 | 서버 관리 필요 | 대규모, 복수 네트워크 |

**Discovery Server 설정 (필요시):**
```bash
# 서버 시작
ros2 run fastrtps_discovery_server discovery_server --port 11811 --id 0

# 클라이언트 설정
export ROS_DISCOVERY_SERVER="192.168.1.1:11811"
```

---

## 5. 개발 단계 (Phase)

### Phase 1: ROS2 Bridge Service 기반 구축

**목표:** gRPC 기반 ROS2 Bridge 프로세스를 만들어 CVPA Agent에서 관리한다.

**선행 조건:**
- ROS2 Jazzy 또는 Rolling 설치
- rclpy 사용 가능한 Python 환경
- CVPA의 `ServiceServer` 인터페이스 이해

**작업 항목:**

| # | 작업 | 검증 |
|---|------|------|
| 1-1 | Bridge 프로세스 스켈레톤 생성 | `--grpc-socket` 인자 받아 gRPC 서버 시작, Agent가 Heartbeat 성공 |
| 1-2 | rclpy 초기화 + asyncio 통합 | `rclpy.init()` + `MultiThreadedExecutor`가 gRPC와 공존 |
| 1-3 | Envelope 핸들러 등록 구조 | type별 핸들러 매핑, 알 수 없는 type 로깅 |
| 1-4 | Agent에 Bridge 서비스 등록 | `ServiceManager.add("ros2-bridge", cmd, on_message=...)` |
| 1-5 | 설정 파일 (YAML) 지원 | Domain ID, 기본 구독 토픽, QoS 등을 설정 파일로 관리 |

**asyncio + rclpy 통합 패턴:**
```python
import asyncio
import rclpy
from rclpy.executors import MultiThreadedExecutor

async def spin_ros2(executor: MultiThreadedExecutor):
    """rclpy executor를 asyncio에서 실행"""
    while rclpy.ok():
        executor.spin_once(timeout_sec=0)
        await asyncio.sleep(0.01)  # yield to event loop

async def main():
    rclpy.init()
    node = BridgeNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    grpc_task = asyncio.create_task(serve_grpc())
    ros2_task = asyncio.create_task(spin_ros2(executor))

    await asyncio.gather(grpc_task, ros2_task)
```

**산출물:**
- `src/cvpa_ros2_bridge/` 패키지
- `src/cvpa_ros2_bridge/main.py` (진입점)
- `src/cvpa_ros2_bridge/bridge_node.py` (ROS2 노드)
- `src/cvpa_ros2_bridge/envelope_handler.py` (Envelope 처리)

---

### Phase 2: 시스템 인트로스펙션

**목표:** 웹에서 ROS2 노드/토픽/서비스 구조를 탐색한다.

**선행 조건:** Phase 1 완료

**작업 항목:**

| # | 작업 | 검증 |
|---|------|------|
| 2-1 | 노드 목록 조회 핸들러 | `ros2.introspection.nodes` 요청 시 노드 목록 반환 |
| 2-2 | 토픽 목록 조회 핸들러 | `ros2.introspection.topics` 요청 시 토픽 + 타입 반환 |
| 2-3 | 서비스 목록 조회 핸들러 | `ros2.introspection.services` 요청 시 서비스 목록 반환 |
| 2-4 | 노드별 상세 조회 핸들러 | 특정 노드의 pub/sub/srv/client 정보 반환 |
| 2-5 | 주기적 자동 갱신 | 5초 주기로 시스템 상태를 자동 push |

**Envelope 프로토콜:**

```
# 요청 (Agent -> Bridge)
type: "ros2.introspection.nodes"
id: "req-001"
payload: {}

# 응답 (Bridge -> Agent)
type: "ros2.introspection.nodes"
id: "req-001"
payload: {
    "nodes": [
        {"name": "camera_node", "namespace": "/"},
        {"name": "detector", "namespace": "/cv"}
    ]
}
```

---

### Phase 3: 토픽 실시간 스트리밍

**목표:** 선택한 토픽의 데이터를 웹으로 실시간 전달한다.

**선행 조건:** Phase 2 완료

**작업 항목:**

| # | 작업 | 검증 |
|---|------|------|
| 3-1 | 동적 구독 관리자 | subscribe/unsubscribe 요청으로 구독 생성/제거 |
| 3-2 | 메시지 직렬화 | ROS2 메시지 -> JSON 변환 (message_to_ordereddict 등) |
| 3-3 | Throttle 구현 | 설정된 간격 이내 메시지 드롭 |
| 3-4 | QoS 자동 매칭 | 대상 토픽의 publisher QoS를 감지하여 호환 QoS 적용 |
| 3-5 | 토픽 주파수 측정 | 실제 Hz 계산 및 보고 |

**동적 QoS 매칭 구현:**
```python
from rclpy.qos import QoSProfile
from rclpy.qos_event import SubscriptionEventCallbacks

def match_qos(node, topic_name):
    """토픽의 publisher QoS를 감지하여 호환 프로파일 생성"""
    info_list = node.get_publishers_info_by_topic(topic_name)
    if not info_list:
        return QOS_SENSOR  # 기본값

    pub_qos = info_list[0].qos_profile
    return QoSProfile(
        reliability=pub_qos.reliability,
        durability=pub_qos.durability,
        history=HistoryPolicy.KEEP_LAST,
        depth=1
    )
```

---

### Phase 4: 카메라 영상 스트리밍

**목표:** 압축 이미지를 웹 Canvas에 실시간 렌더링한다.

**선행 조건:** Phase 3 완료

**작업 항목:**

| # | 작업 | 검증 |
|---|------|------|
| 4-1 | CompressedImage 구독 | JPEG/PNG 데이터를 binary Envelope로 전달 |
| 4-2 | 프레임 레이트 제어 | 웹 성능에 맞춰 fps 조절 (기본 15fps) |
| 4-3 | Raw Image 변환 | Image 토픽만 있는 경우 Bridge에서 JPEG 압축 후 전달 |
| 4-4 | CV 결과 오버레이 데이터 | 탐지 결과를 별도 Envelope로 동기 전송 |
| 4-5 | 멀티 카메라 | 여러 카메라 동시 스트리밍 |

**Raw Image -> JPEG 변환 (numpy 활용):**
```python
import numpy as np
from io import BytesIO
# PIL 또는 cv2로 JPEG 인코딩
# numpy는 이미 프로젝트 의존성에 포함됨
```

**Binary Envelope 전송:**
```python
envelope = Envelope(
    type="ros2.image.compressed",
    id=str(uuid4()),
    payload=compressed_image_msg.data,  # bytes 직접 전달
    metadata={
        "topic": topic_name,
        "format": compressed_image_msg.format,
        "stamp_sec": str(header.stamp.sec),
        "stamp_nanosec": str(header.stamp.nanosec),
    }
)
```

---

### Phase 5: 진단 및 로그

**목표:** 시스템 건강 상태와 로그를 웹에서 모니터링한다.

**선행 조건:** Phase 3 완료 (Phase 4와 병렬 진행 가능)

**작업 항목:**

| # | 작업 | 검증 |
|---|------|------|
| 5-1 | /diagnostics 구독 | DiagnosticArray 메시지를 파싱하여 전달 |
| 5-2 | /rosout 구독 | 로그 메시지를 레벨/노드별로 전달 |
| 5-3 | 노드 생존 감시 | 5초 주기 인트로스펙션으로 노드 추가/제거 감지 |
| 5-4 | Lifecycle 상태 조회 | Lifecycle 노드의 현재 상태 조회 및 전환 이벤트 모니터링 |
| 5-5 | 알림 조건 설정 | ERROR 이상 진단, 노드 다운 시 즉시 push |

---

### Phase 6: 원격 제어

**목표:** 웹에서 ROS2 서비스 호출, 파라미터 조정, 토픽 publish를 수행한다.

**선행 조건:** Phase 3 완료

**작업 항목:**

| # | 작업 | 검증 |
|---|------|------|
| 6-1 | 서비스 호출 핸들러 | 웹 요청 -> ROS2 service call -> 응답 반환 |
| 6-2 | 파라미터 조회/설정 | AsyncParameterClient로 원격 노드 파라미터 관리 |
| 6-3 | 토픽 Publish | 웹에서 보낸 메시지를 ROS2 토픽으로 publish |
| 6-4 | Lifecycle 전환 | Lifecycle 노드의 상태 전환 (configure/activate/deactivate 등) |
| 6-5 | 권한/안전 체크 | 위험한 명령 (shutdown, emergency_stop 등) 확인 절차 |

**보안 고려사항:**
- 서비스 호출/토픽 publish는 인증된 사용자만 가능
- 화이트리스트 기반 허용 서비스/토픽 관리
- 위험 명령은 이중 확인 (웹 UI에서 confirm)

---

## 6. 의존성

### 6.1 Python 패키지 (추가 필요)

| 패키지 | 용도 | 비고 |
|--------|------|------|
| rclpy | ROS2 Python 클라이언트 | ROS2 설치 시 포함 |
| rosidl_runtime_py | 메시지 직렬화 유틸리티 | `message_to_ordereddict()` |
| cv_bridge | Image <-> numpy 변환 | 선택 (cv2 사용 시) |

### 6.2 시스템 요구사항

| 항목 | 요구사항 |
|------|----------|
| ROS2 | Jazzy Jalisco 또는 Rolling |
| DDS | Fast DDS (기본) 또는 Cyclone DDS |
| Python | 3.14+ (프로젝트 요구사항) |
| OS | Ubuntu 24.04 (Jazzy 공식 지원) |

### 6.3 ROS2 패키지 (추가 필요)

```bash
sudo apt install \
    ros-jazzy-compressed-image-transport \
    ros-jazzy-diagnostic-common-diagnostics \
    ros-jazzy-rqt-robot-monitor
```

---

## 7. Envelope Type 요약

전체 Envelope type 네이밍 컨벤션: `ros2.<category>.<action>`

| Type | 방향 | 설명 |
|------|------|------|
| `ros2.introspection.nodes` | 양방향 | 노드 목록 조회 |
| `ros2.introspection.topics` | 양방향 | 토픽 목록 조회 |
| `ros2.introspection.services` | 양방향 | 서비스 목록 조회 |
| `ros2.introspection.node_detail` | 양방향 | 노드 상세 정보 |
| `ros2.topic.subscribe` | Agent->Bridge | 토픽 구독 요청 |
| `ros2.topic.unsubscribe` | Agent->Bridge | 구독 해제 |
| `ros2.topic.data` | Bridge->Agent | 토픽 데이터 스트림 |
| `ros2.topic.publish` | Agent->Bridge | 토픽에 메시지 publish |
| `ros2.topic.rate` | Bridge->Agent | 토픽 주파수 보고 |
| `ros2.image.compressed` | Bridge->Agent | 압축 이미지 (binary) |
| `ros2.cv.detections` | Bridge->Agent | CV 탐지 결과 |
| `ros2.diagnostics` | Bridge->Agent | 진단 데이터 |
| `ros2.health.nodes` | Bridge->Agent | 노드 생존 상태 |
| `ros2.log` | Bridge->Agent | /rosout 로그 |
| `ros2.service.call` | Agent->Bridge | 서비스 호출 요청 |
| `ros2.service.response` | Bridge->Agent | 서비스 호출 응답 |
| `ros2.param.list` | 양방향 | 파라미터 목록 |
| `ros2.param.get` | 양방향 | 파라미터 조회 |
| `ros2.param.set` | Agent->Bridge | 파라미터 설정 |
| `ros2.lifecycle.state` | 양방향 | Lifecycle 상태 조회 |
| `ros2.lifecycle.transition` | Agent->Bridge | Lifecycle 전환 요청 |

---

## 8. 대안 검토: rosbridge_suite vs 직접 구현

### 8.1 rosbridge_suite 사용

| 장점 | 단점 |
|------|------|
| 즉시 사용 가능 | 별도 WebSocket 서버 (포트 9090) |
| roslibjs 클라이언트 라이브러리 | CVPA Agent 우회 (인증/라우팅 분리) |
| 검증된 프로토콜 | 대용량 메시지 성능 이슈 |
| Action 지원 | 커스터마이즈 제한 |

### 8.2 직접 구현 (권장)

| 장점 | 단점 |
|------|------|
| 기존 CVPA 아키텍처 활용 | 개발 시간 |
| 단일 WebSocket 경로 (인증 통합) | 프로토콜 직접 설계 |
| Envelope 기반 통합 메시지 체계 | 테스트 필요 |
| 필요한 기능만 구현 | |
| gRPC 바이너리 전송 (이미지 효율) | |

**결론:** CVPA의 기존 아키텍처(ProcessService + gRPC + WebSocket)가 이미 Bridge 패턴에
적합하므로, 직접 구현이 아키텍처 일관성과 보안 측면에서 유리하다. rosbridge_suite의
프로토콜 설계(throttle, fragmentation, compression 등)는 참고할 가치가 있다.

---

## 9. 개발 일정 예상 로드맵

```
Phase 1: Bridge 기반 구축         ████████░░░░░░░░░░░░░░░░░░░░
Phase 2: 인트로스펙션             ░░░░░░░░████░░░░░░░░░░░░░░░░
Phase 3: 토픽 스트리밍            ░░░░░░░░░░░░████████░░░░░░░░
Phase 4: 카메라 스트리밍          ░░░░░░░░░░░░░░░░░░░░████░░░░
Phase 5: 진단/로그 (4와 병렬)     ░░░░░░░░░░░░░░░░░░░░████░░░░
Phase 6: 원격 제어               ░░░░░░░░░░░░░░░░░░░░░░░░████
```
