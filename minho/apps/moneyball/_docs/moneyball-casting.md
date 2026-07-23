# moneyball — casting (라인업 캐스팅)

`GET /api/moneyball/casting/{team_id}?formation=4-4-2`

팀 ID와 포메이션 문자열(`DF-MF-FW`, 예: `4-4-2`)을 받아 그 팀 로스터에서 포지션별로
선발(starters) 슬롯을 채운다. GK 1명은 포메이션 문자열과 무관하게 항상 슬롯에 포함된다.

## 1단계 범위 — 포지션 기반 로스터 배치만

`moneyball_players`에는 골/어시스트/평점 같은 경기 성과 지표가 없다(로스터 정보만:
이름/포지션/등번호/신체정보/국적/생년월일). 그래서 지금은 진짜 머니볼식(저평가 선수
데이터 기반 발굴)이 아니라, 포지션이 맞는 선수를 순서대로 슬롯에 채우는 것까지만 한다.
포지션 안에서의 정렬은 `back_no`(등번호) 오름차순 → `player_id` — **성과 지표가 없는
동안 쓰는 결정적 임시 기준**이다. 실제 스탯이나(`moneyball_players.embedding` 컬럼처럼)
임베딩 기반 랭킹이 생기면 `app/use_cases/casting_interactor.py`의 `_sort_key`만 교체하면 된다.

## 슬롯을 못 채우는 경우

로스터에 해당 포지션 선수가 없거나 부족하면 에러를 내지 않고 `unfilled_positions`에
그 포지션 이름을 담아 반환한다(예: `["GK"]`). 실제 시드 데이터(`resources/soccer_seed_data.sql`)에는
GK 포지션 선수가 아예 없고, 팀별 보유 인원도 크게 다르다(K06=30명, K04=5명 등) —
이 API를 그대로 시드 데이터에 돌리면 거의 항상 `unfilled_positions`에 `"GK"`가 포함된다.

## 응답 구조

`CastingResponse(team_id, formation, starters, unfilled_positions, bench)` —
선발되지 않은 로스터 전원은 `bench`로 반환된다.

## 다음 단계(범위 밖)

- 경기 성과 지표(골/어시스트/평점 등) 수집·스키마 반영 후 정렬 기준을 스탯 기반으로 교체.
- `moneyball_players.embedding`(pgvector, 아직 미사용)을 활용한 유사 선수 추천/스카우팅.
