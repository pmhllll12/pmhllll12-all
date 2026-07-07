작업하신 내역과 코드 수정 사항을 바탕으로, 프로젝트의 테스트 및 유지보수를 위한 **개발 하네스(Harness) 문서 형태의 마크다운(MD) 양식**으로 깔끔하게 정리해 드립니다.

`CLAUDE.md`나 프로젝트 내부 개발 가이드 문서에 바로 붙여넣어 사용하실 수 있도록 가독성을 높여 구성했습니다.

---

# 🚢 Titanic 도메인 개발 하네스 (Walter 데이터셋 가이드)

최근 수정된 `crew_walter_roaster` 포트 및 어댑터 구현체에 대한 명세와 데이터셋 호출 규칙입니다.

## 1. 아키텍처 및 인터페이스 명세

데이터베이스 I/O 작업이 포함되므로, 앞서 정의한 **async 규칙**에 따라 `async def` 인터페이스로 전환되었습니다. 훈련 데이터셋과 테스트 데이터셋은 `survived` 컬럼의 유무(Null 여부)를 기준으로 분기하여 조회합니다.

### 📐 포트 (Port) 인터페이스

* **파일 위치**: `minho/apps/titanic/app/ports/output/crew_walter_roaster_port.py`

```python
from abc import ABC, abstractmethod
import pandas as pd

class WalterRoasterPort(ABC):
    """월터의 승객 명단 관리 저장소 인터페이스."""

    @abstractmethod
    async def get_train_set(self) -> pd.DataFrame:
        """Survived 컬럼이 있는 데이터 전체를 데이터 프레임으로 반환하는 메소드"""
        pass

    @abstractmethod
    async def get_test_set(self) -> pd.DataFrame:
        """Survived 컬럼이 없는 데이터 전체를 데이터 프레임으로 반환하는 메소드"""
        pass

```

### 💾 어댑터 (Adapter) 구현체

* **파일 위치**: `minho/apps/titanic/adapter/outbound/repositories/crew_walter_roaster_repository.py`
* **주요 매핑 로직**: `passengers (JackTrainerOrm)` 테이블과 `bookings (RoseModelOrm)` 테이블을 `passenger_id` 기준으로 **Outer Join** 하여 ML 피처셋을 생성합니다.

| 데이터셋 유형 | DB 조건 (`survived`) | 반환 DataFrame 특징 |
| --- | --- | --- |
| **Train Set** | `JackTrainerOrm.survived.isnot(None)` | `survived` 컬럼 **포함** |
| **Test Set** | `JackTrainerOrm.survived.is_(None)` | `survived` 컬럼 **제외** |

---

## 2. 인터렉터(Interactor) 호출 규칙 (비동기 처리)

`WalterRoasterRepository`는 비동기(`AsyncSession`)로 작동하므로, 상위 비즈니스 로직(예: `crew_smith_captain_interactor.py`)에서 호출할 때는 반드시 **`await`** 키워드를 사용해야 합니다.

```python
# 인터렉터 내부 구현 예시
async def prepare_ml_pipeline(self):
    logger.info("ML 파이프라인 데이터 로드 시작")
    
    # 데이터셋 로드 시 await 필수 적용
    train_set = await self.walter.get_train_set()
    test_set  = await self.walter.get_test_set()
    
    logger.info(f"데이터 로드 완료: Train({len(train_set)}행), Test({len(test_set)}행)")
    return train_set, test_set

```

---

## 3. 컨테이너 재빌드 가이드

백엔드 `tailor.` 임포트 오류 수정 및 저장소 구현이 완료되었으므로, 변경 사항을 반영하기 위해 아래 명령어로 도커 컨테이너를 재빌드하십시오.

```bash
# 백그라운드 환경으로 깨끗하게 재빌드 및 실행
docker compose up --build -d

```