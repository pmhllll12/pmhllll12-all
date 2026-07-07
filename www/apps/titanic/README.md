# Titanic (레이어드)

`secom`과 같은 **controller → service → repository** 흐름으로 정리했습니다.

| 이전 파일(접미/역할) | 새 위치 |
|---------------------|---------|
| `james_controller` | `app/controllers/titanic_controller.py` |
| `jack_service` | `app/services/titanic_service.py` |
| `walter_reader` | `app/repositories/titanic_dataset_repository.py` |
| `rose_model` | `app/models/survival_classifier_model.py` |
| `caledon_validation` | `app/validators/titanic_passenger_validator.py` |
| (신규) 스키마·문제정의 | `schemas/titanic_schemas.py` |
| 데모 데이터 | `app/demo_data.py` (파일 I/O 없음) |

## API

- `GET /titanic/data` — 표본 1행(JSON)
- `GET /titanic/count` — 행 수
- `GET /titanic/tree` — 의사결정나무 분류기 사용 여부
- `GET /titanic/model` — 모델 메타데이터
- `GET /titanic/problem` — 문제 정의·컬럼 설명(JSON)
