---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# 실리콘밸리 캐스팅 — `apps/admin`의 명명 규약과 참조 슬라이스

`apps/admin`의 코드 대부분이 `piper_*` 접두를 달고 드라마 〈실리콘밸리〉의 등장인물 이름을
쓴다. 이 문서는 **그 캐스팅이 무엇을 뜻하는지**와 **새 코드가 따라야 할 규약**을 정한다.
002 이후 문서들이 전제하는 명명·구조의 출발점이다.

> **`admin`인데 왜 `silicon_valley`인가**
> 이 앱은 원래 `silicon_valley`라는 이름이었고 커밋 `15b0a4e`(`refactor: silicon_valley를
> admin으로 이동`)에서 디렉터리만 `admin`으로 바뀌었다. 그래서 **디렉터리는 `admin`, 라우터
> prefix·태그와 이 `_docs/`의 frontmatter는 여전히 `silicon_valley`** 다. 둘은 같은 것을
> 가리킨다 — 새 코드에서 혼동하지 않도록 여기 기록해 둔다.

---

## 1. 캐스팅 표

파이드 파이퍼(Pied Piper)의 다섯 인물이 각각 하나의 수직 슬라이스를 맡는다.

| 인물 | 배역(역할 접미사) | `route` | 파일 접두 | HTTP | MCP 마운트 |
|------|------------------|---------|-----------|------|-----------|
| Richard Hendricks / 리처드 헨드릭스 | CEO (`_ceo`) | `hendricks` | `piper_hendricks_ceo_` | `GET /api/v1/hendricks/myself` | `/mcp/hendricks` |
| Jared Dunn / 자레드 던 | COO (`_coo`) | `dunn` | `piper_dunn_coo_` | `GET /api/v1/dunn/myself` | `/mcp/dunn` |
| Bertram Gilfoyle / 버트럼 길포일 | 시스템 아키텍트 (`_system`) | `gilfoyle` | `piper_gilfoyle_system_` | `GET /api/v1/gilfoyle/myself` | `/mcp/gilfoyle` |
| Dinesh Chugtai / 디네시 추그타이 | 대시보드 (`_dash`) | `dinesh` | `piper_dinesh_dash_` | `GET /api/v1/dinesh/myself` | `/mcp/dinesh` |
| Nelson 'Big Head' Bighetti / 넬슨 '빅헤드' 비게티 | 인사(HR) (`_hr`) | `bighetti` | `piper_bighetti_hr_` | `GET /api/v1/bighetti/myself` | `/mcp/bighetti` |

- 목록 엔드포인트: `GET /api/v1/` — 다섯 캐릭터의 이름과 route를 반환한다
  (`adapter/inbound/api/__init__.py`의 `_CHARACTERS`).
- MCP 서버는 `main.py`에서 `streamable_http_app()`으로 **다섯 개 모두 마운트**된다.

---

## 2. 명명 규약

파일명은 **`piper_<인물>_<배역>_<계층>.py`** 형태로 고정한다.

```
piper_hendricks_ceo_router.py       ← 인물 hendricks, 배역 ceo, 계층 router
piper_hendricks_ceo_interactor.py
piper_hendricks_ceo_repository.py
```

- **인물**은 성(姓) 소문자 한 단어 — `hendricks`, `dunn`, `gilfoyle`, `dinesh`, `bighetti`.
  `route` 값과 항상 같다.
- **배역**은 역할 한 단어 — 위 표의 접미사를 그대로 쓴다. 새로 만들지 않는다.
- 클래스명은 `piper_` 없이 PascalCase로 인물+배역만 — `HendricksCeoRepository`,
  `GilfoyleSystemEntity`. (파일 접두 `piper_`는 디렉터리 안에서 묶어 보기 위한 것이고
  클래스명에는 반복하지 않는다.)
- 한글 이름·영문 이름은 데이터이지 식별자가 아니다 — 파일명·클래스명·라벨에 쓰지 않는다.

---

## 3. 참조 슬라이스 — 한 요청이 지나는 5단 경로

다섯 캐릭터 모두 동일한 헥사고날 수직 슬라이스로 구현돼 있다. **`apps/admin`에 새 기능을
추가할 때 따라야 할 참조 구현**이다(`pdf_loader`도 같은 구성).

```
adapter/inbound/api/v1/piper_hendricks_ceo_router.py     ① 라우터   GET /myself
  └ dependencies/piper_hendricks_ceo_provider.py         ② provider  Depends 조립
      └ app/use_cases/piper_hendricks_ceo_interactor.py  ③ 인터랙터  입력 포트 구현
          └ app/ports/output/piper_hendricks_ceo_port.py ④ 출력 포트 (추상)
              └ adapter/outbound/repositories/
                    piper_hendricks_ceo_repository.py    ⑤ 어댑터    포트 구현

경계를 넘는 타입:
  adapter/inbound/schema/piper_hendricks_ceo_schema.py   Pydantic (HTTP 경계)
  app/dtos/piper_hendricks_ceo_dto.py                    Query / Response (내부)
  domain/entities/piper_hendricks_ceo_entity.py          순수 dataclass
  adapter/outbound/mapper/piper_hendricks_ceo_mapper.py  기본 엔티티 생성
```

계층 경계(`domain → app → adapter`)는 `minho/pyproject.toml`의 `[tool.importlinter]`가
빌드 타임에 강제한다 — 상세는
[`architecture-star-topology.md`](../../../_docs/architecture-star-topology.md).

테스트는 `apps/admin/tests/`에 있고 `pytest.ini`의 `testpaths`에 포함돼 실제로 실행된다.

---

## 4. 두 개의 인바운드 어댑터

같은 캐릭터가 **HTTP와 MCP 두 경로**로 노출된다. 둘은 성격이 다르다.

| | HTTP (`adapter/inbound/api/v1/`) | MCP (`adapter/inbound/mcp/`) |
|---|---|---|
| 진입 | `GET /api/v1/<route>/myself` | `/mcp/<route>` (streamable HTTP) |
| 계층 | §3의 5단을 전부 거친다 | **거치지 않는다** — 하드코딩 문자열 반환 |
| 정의 | `APIRouter` | `FastMCP` + `@mcp.tool(name="<Pascal>")` |

MCP 도구 이름은 PascalCase 인물명(`Hendricks`, `Gilfoyle` …)이다.

`piper_gilfoyle_system_tools.py`에만 `if __name__ == "__main__": mcp.run()` 진입점이 있다
(커밋 `c1d4f9a`). 이 진입점은 **stdio 서버로 직접 실행**하기 위한 것이고, 위 HTTP 마운트와는
별개 경로다 — 루트 `.mcp.json`이 이 파일 하나를 stdio로 띄워 쓴다. 나머지 넷은 HTTP로만
붙을 수 있다.

---

## 5. 알려진 격차

현재 구현은 **동작하는 스캐폴드**이지 완성된 기능이 아니다. 아래는 확인된 사실이며, 이
캐스팅 위에 실제 기능을 얹을 때 함께 정리한다.

### 5.1 캐릭터 메타데이터가 5곳에 중복돼 있다

같은 세 문자열(`route`, `english_name`, `korean_name`)이 아래에 각각 적혀 있다.

1. `domain/entities/piper_*_entity.py` — dataclass 기본값
2. `adapter/inbound/schema/piper_*_schema.py` — `Field` 기본값 **및** `json_schema_extra` 예시
3. `adapter/inbound/api/v1/piper_*_router.py` — 스키마 생성 시 리터럴로 다시 지정
4. `adapter/inbound/api/__init__.py` — `_CHARACTERS` 리스트
5. `adapter/inbound/mcp/piper_*_tools.py` — 반환 문자열에 한글 이름·역할 하드코딩

**이미 갈라졌다** — `dinesh`는 파일·route가 `dash`(대시보드)인데 MCP 문자열은 "엔지니어"라고
말한다. 다섯 중 이 하나만 배역 서술이 어긋난다. 새 캐릭터를 추가하면 5곳을 모두 고쳐야 하고,
하나만 빠뜨려도 조용히 어긋난다. **캐스팅 데이터의 정본을 한 곳으로 모으는 것**이 이 슬라이스에
대한 다음 개선이다.

### 5.2 리포지토리가 쓰지 않는 DB 세션을 주입받는다

`piper_*_repository.py`는 생성자로 `AsyncSession`을 받지만 `introduce_myself`는 세션을 전혀
쓰지 않고 입력을 그대로 되돌려 준다. provider가 `Depends(get_db)`로 세션을 열므로 **매 요청마다
쓰지 않을 DB 세션이 열린다.** 실제 조회가 생기기 전까지는 세션 주입을 걷어내는 편이 맞다.

### 5.3 엔티티·매퍼가 요청 경로에서 쓰이지 않는다

`domain/entities/piper_*_entity.py`와 `adapter/outbound/mapper/piper_*_mapper.py`의
`*_default_entity()`는 **테스트에서만 호출된다.** 실제 요청은 스키마 → DTO → DTO로 흐르고
엔티티를 거치지 않는다. 계층 구조를 보여 주는 예시로서의 가치는 있으나, 실제 도메인 로직이
생길 때 요청 경로에 편입하거나 정리한다.

### 5.4 MCP가 헥사고날을 우회한다

§4의 표대로, HTTP는 5단을 모두 지나는데 MCP 도구는 문자열을 즉시 반환한다. MCP에 실제 기능을
붙일 때는 HTTP 라우터와 마찬가지로 **provider를 통해 유스케이스를 호출**해야 한다 — 그러지
않으면 같은 기능이 두 벌로 갈라진다.

### 5.5 비어 있는 스텁

- `domain/piper_hendricks_ceo_topology.py` — `# 그래프 노드 정의` 주석 한 줄뿐
- `domain/notification_service.py` — 빈 파일
- `domain/document_vector.py` — 빈 파일 ([009](009-langgraph-strategy.md) §7에서 정리 대상)

빈 파일을 "이미 만들어 뒀으니 채운다"는 이유로 구현하지 않는다
([004](004-langgraph_harness.md) §2와 같은 원칙). 필요해질 때 채우거나, 지금 지운다.

---

## 6. 새로 추가할 때

**기존 캐릭터에 기능을 추가**하면 §3의 5단을 그대로 따르고, 파일명은 §2 규약을 지킨다.
`piper_<인물>_<배역>_` 접두를 유지하면 다섯 슬라이스가 디렉터리에서 나란히 정렬된다.

**새 캐릭터를 추가**할 때는 §5.1의 5곳을 모두 갱신해야 한다는 점을 먼저 확인한다. 셋 이상을
동시에 고쳐야 한다면, 캐릭터를 늘리기 전에 정본을 한 곳으로 모으는 작업을 먼저 하는 편이 싸다.

**캐릭터와 무관한 기능**(PDF 로더, LangChain 채팅, GraphRAG 등)은 `piper_` 접두를 쓰지 않는다.
이들은 별도 이름으로 같은 5단 구성을 따른다 — `pdf_loader_*`, `langchain_chat_*`,
[009](009-langgraph-strategy.md) §7의 `document_graph_*`.

---

## 7. 완료 기준 체크리스트

새 `piper_*` 코드를 추가·수정할 때 확인한다.

- [ ] 파일명이 `piper_<인물>_<배역>_<계층>.py` 규약을 따른다(§2).
- [ ] 배역 접미사가 §1 표에 있는 것이다(새로 만들지 않았다).
- [ ] 클래스명에 `piper_`를 반복하지 않았다.
- [ ] §3의 5단 경로를 지키고, 계층을 건너뛰지 않았다.
- [ ] `cd minho && lint-imports` 통과 — `domain → app → adapter` 경계 위반 없음.
- [ ] 캐릭터 메타데이터를 고쳤다면 §5.1의 **5곳을 모두** 확인했다.
- [ ] MCP 도구에 기능을 추가했다면 하드코딩이 아니라 provider를 거쳐 유스케이스를 호출한다(§5.4).
- [ ] DB를 실제로 쓰지 않는 리포지토리에 세션을 새로 주입하지 않았다(§5.2).
- [ ] `apps/admin/tests/`에 테스트를 추가했다.

---

## 8. 참고

- [`minho/_docs/architecture-star-topology.md`](../../../_docs/architecture-star-topology.md) — 허브/스포크·계층 경계
- [002-neo4j-harness.md](002-neo4j-harness.md) — 그래프 모델링 규칙
- [003-langchain_harness.md](003-langchain_harness.md) — LangChain 체인 배치 (§0에 `pdf_loader` 참조 구현)
- [008-neo4j-strategy.md](008-neo4j-strategy.md) — Neo4j 연결 기반
- [009-langgraph-strategy.md](009-langgraph-strategy.md) — GraphRAG 전략
