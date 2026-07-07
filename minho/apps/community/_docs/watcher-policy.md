# [Specification] Multi-Agent System Test Harness Specification

## 1. System Overview & Architecture Context

본 시스템은 허브 앤 스포크(Hub-and-Spoke) 및 온톨로지 기반의 거대 비즈니스 ERP 멀티 에이전트 아키텍처이다.

- **최고 사령탑 (Hub / Brain)**: `apps/community/app/use_cases/watcher_interactor.py`
  초거대 AI 모델(EXAONE)이 상주하는 최고 권한의 오케스트레이터 에이전트 — 페이커(Faker) 에스컬레이션 스텝으로 시뮬레이션.
- **온톨로지 버스 (Ontology Hub)**: `apps/community/app/use_cases/watcher_interactor.py`
  전사 데이터 흐름, 엔티티 관계(Ontology) 및 전사 컨텍스트를 총괄하는 데이터 허브 버스 — StarCraft 경유 스텝으로 시뮬레이션.
- **커뮤니케이션 스포크 (Communication Spoke)**: `apps/community/`
  외부 채널(Email, Mail, Telegram, Discord 등)과의 소통 및 인바운드 이벤트를 전담하는 스포크.
- **기타 스포크 (Spokes)**: `apps/titanic/`, `apps/silicon_valley/` 등 (ERP의 개별 도메인 파트)

## 2. Agent Core Logic & Routing Criteria

외부 커뮤니케이션 채널을 통해 인입되는 이벤트는 비즈니스 중요도 및 의도(Intent)에 따라 다음과 같이 라우팅된다.

- **Case A (일반 업무)**: 중요 거래처가 아니거나 단순 문의인 경우
  ➔ `apps/community/app/use_cases/watcher_interactor.py` 내부의 홈즈(Holmes) 자체 처리 분기가 컨텍스트를 소화하여 처리 및 종결.
- **Case B (중요/에스컬레이션 업무)**: 중요 거래처이거나 자동 보고서 생성을 요청하는 경우
  ➔ 같은 인터랙터 안의 StarCraft 경유 분기를 거쳐 최고 에이전트인 **페이커(Faker / EXAONE)**에게 격상(Escalation)된 것으로 시뮬레이션. 페이커가 전사 ERP 데이터를 취합하여 최종 보고서를 생성하고 하향 전달.

## 3. Watson (Watcher Hub / Entry Point) 역할 정의

`apps/community/adapter/inbound/api/v1/watcher_router.py`에 위치한 **왓슨(Watson)**은 본 테스트 하네스의 핵심 검증 대상이자 인바운드 게이트웨이이다. 왓슨은 단순한 라우터가 아닌 **'Triage Nurse(초진 및 분류 관문)'** 역할을 수행한다.

### 왓슨의 핵심 메커니즘

1. **감시 및 후킹 (Watch & Hook)**: 경찰/조력자 레이어(`apps/community/adapter/inbound/api/v1/telegram_router.py`, `apps/community/adapter/inbound/api/v1/discord_router.py` 등)로부터 유저 메시지 및 이벤트를 낚아챔.
2. **1차 분류 및 조율 (Validation & Triage)**: 인입된 메시지의 발신자(중요 거래처 여부)와 본문(보고서 요청 등의 의도)을 가볍고 빠르게 분석.
3. **컨텍스트 스위칭 및 라우팅 (Routing Decision)**:
   - 일반 메일 ➔ `apps/community/app/use_cases/watcher_interactor.py` 내 홈즈(Holmes) 분기 호출.
   - 중요/보고서 메일 ➔ 같은 인터랙터 내 StarCraft 온톨로지 버스 경유 분기로 이벤트 발행(Publish) 시뮬레이션.

## 4. Test Harness Implementation Instructions (for Claude)

이 마크다운을 컨텍스트로 받는 LLM(클로드)은 위 설계를 검증하기 위한 테스트 하네스(Test Harness) 환경 코드를 다음 지시사항에 따라 생성하시오.

> **구현 현황**: 아래 지시사항은 `apps/community/` 안에서 자기완결 시뮬레이션으로 구현 완료됨 (star_craft·sherlock_homes 등 실제 허브/스포크 모듈은 아직 존재하지 않아 만들지 않고, 라우팅 저니를 인터랙터 하나에서 시뮬레이션함).

### [지시사항 1] 가상 이벤트 생성기 (Mock Event Generator) 구현

- `apps/community/adapter/inbound/api/v1/telegram_router.py`, `apps/community/adapter/inbound/api/v1/discord_router.py` 등 인바운드 라우터들이 외부에서 메일/메시지를 수신하는 상황을 모사하는 Mock 데이터 생성기를 작성할 것.
- 테스트 케이스 시나리오는 최소 2가지 이상을 포함해야 함 (`apps/community/tests/app/use_cases/test_watcher_interactor.py`에 구현됨):
  - **Scenario 1**: 일반 거래처의 단순 인사/일반 문의 메일 인입.
  - **Scenario 2**: VIP 거래처(`important_client: true`)의 "분기 실적 자동 보고서 발행 요망" 메시지 인입.

### [지시사항 2] 왓슨(Watson Watcher Hub)의 라우팅 인터셉터 구현

- 가상 이벤트 생성기에서 발생한 raw 데이터를 왓슨 인터페이스(`apps/community/adapter/inbound/api/v1/watcher_router.py`)가 가로채어 검증하는 라우팅 로직을 구현할 것.
- **홈즈 호출 트리거**: Scenario 1 감지 시, `apps/community/app/use_cases/watcher_interactor.py` 내의 홈즈 분기 함수를 호출하고 로그를 남길 것.
- **페이커 에스컬레이션 트리거**: Scenario 2 감지 시, 같은 인터랙터 안의 StarCraft 경유 분기를 거쳐 페이커(Faker)가 최종 활성화(Wake-up)되는 이벤트 버스 파이프라인(가상 MCP Notification 등)을 구현할 것.

### [지시사항 3] 하네스 대시보드 및 검증 로그 출력

- 이벤트 인입부터 최종 처리 완료(Watson ➔ Holmes 또는 Watson ➔ StarCraft ➔ Faker)까지의 전체 멀티 에이전트 저니(Journey)를 콘솔 내에 추적 서사 로그(Narrative Log) 형태로 일목요연하게 출력하는 모니터링 기능을 포함할 것 (`apps/community/app/use_cases/watcher_interactor.py`의 `logger.info("[Watson] ...")` + `GET /api/community/watcher/logs`로 구현됨).
