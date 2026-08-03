# 이미지 S3 업로드 — 파이프라인과 배포 조건

`admin` 앱의 이미지 업로드. **코드에 없어서 새 환경에서 빠뜨리기 쉬운 것들**을 적는다
— 코드는 저장소를 읽으면 되지만, IAM 역할·nginx 상한·환경변수는 서버에만 있다.

플러터 화면 ---> `pmh_flutter/pmh_flutter_application_1/lib/image_upload_page.dart`
스타 토폴로지·계층 계약 ---> [`architecture-star-topology.md`](architecture-star-topology.md)

> 2026-08-03 구현·배포. 노트9 실기기와 터널 경유 curl로 종단 확인했다.
> 문서와 코드가 어긋나면 **코드가 정본**이다.

---

## 1. 계층 (포트/어댑터)

```
HTTP multipart
  → adapter/inbound/api/v1/s3_image_upload_router.py
  → app/ports/input/s3_image_upload_use_case.py
  → app/use_cases/s3_image_upload_interactor.py
  → app/ports/output/image_storage_port.py
  → adapter/outbound/client/s3_image_storage_client.py   ← boto3는 여기에만
```

지키는 규칙 세 가지. 어기면 `lint-imports`의 `domain ← app ← adapter` 계약이나
테스트 격리가 깨진다.

- **포트 이름에 S3가 없다.** `ImageStoragePort`는 `upload`/`generate_view_url`만 안다.
  덕분에 유스케이스 테스트가 가짜 포트만으로 돌아 AWS도 네트워크도 필요 없다.
- **botocore 예외가 라우터까지 올라가지 않는다.** 아웃바운드 어댑터가
  `NoCredentialsError`·`ClientError`를 `ImageStorageUnavailableError`로 바꿔 던진다.
- **허용 형식·크기는 domain에 있다**(`domain/entities/s3_image_entity.py`).
  라우터와 유스케이스가 같은 상수를 보므로 두 곳의 숫자가 어긋날 수 없다.
  검증은 **저장 전에** 한다 — 올린 뒤 거절하면 지워야 할 객체가 S3에 남는다.

### 엔드포인트

| Method | 경로 | 설명 |
|---|---|---|
| POST | `/api/admin/s3/images` | multipart `file` → 저장 후 presigned URL 반환 |
| GET | `/api/admin/s3/images/allowed-types` | 허용 형식·상한. 앱이 화면에 띄우는 데 쓴다 |

| 상태 | 조건 |
|---|---|
| 200 | `{ok, key, filename, content_type, size_bytes, url, uploaded_at}` |
| 413 | 10MB 초과 (**§3의 nginx 상한을 먼저 확인할 것**) |
| 422 | 허용하지 않는 형식·빈 파일 |
| 503 | 버킷 미설정, AWS 자격증명 없음, S3 장애 |

키 형식은 `admin/images/{uuid}-{원본파일명}`. UUID를 앞에 붙여 같은 이름끼리 덮어쓰지
않게 한다 — 키 생성은 저장소의 관심사라 어댑터에만 있다.

---

## 2. 필요한 것 — 저장소 밖 (새 환경에서 반드시)

### 2.1 버킷 이름 (`minho/.env`)

```
VISION_S3_BUCKET=pmh12-s3-bucket-070605553723-ap-northeast-2-an
```

- **ARN이 아니라 버킷 이름**이다. `arn:aws:s3:::` 접두사를 떼고 넣는다.
  ARN은 boto3의 `Bucket=`에 넣을 수 없고, IAM 정책의 `Resource`에 쓰는 값이다.
- 어댑터는 `ADMIN_S3_BUCKET` → 없으면 `VISION_S3_BUCKET` 순으로 읽는다. 후자는
  `ontology` 앱이 쓰던 이름인데 현재 같은 버킷을 공유해 폴백으로 받아들였다.
  버킷을 분리할 때 앞의 이름만 넣으면 된다.
- `AWS_REGION`은 넣지 않아도 된다 — 코드 기본값이 `ap-northeast-2`다.

### 2.2 AWS 자격증명 — **키를 넣지 않는다**

코드는 `boto3.client("s3", ...)`를 키 없이 호출한다. boto3 기본 탐색 순서
(환경변수 → `~/.aws/credentials` → **EC2 인스턴스 역할**)를 그대로 탄다.

운영은 **인스턴스 역할**을 쓴다. `.env`에 장기 키를 두지 않아도 되고, 회수도 역할
교체로 끝난다. 현재 `i-0d61cddf8061968f4`에 `pmh12-role`이 붙어 있다.

역할에 붙일 최소 정책:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AdminImageUpload",
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::pmh12-s3-bucket-070605553723-ap-northeast-2-an/*"
    }
  ]
}
```

- **끝의 `/*`가 필수다.** 객체 단위 작업은 버킷이 아니라 버킷 *안의 객체*가 대상이라,
  `/*` 없이 버킷 ARN만 쓰면 `AccessDenied`가 난다.
- `GetObject`가 필요한 이유는 presigned URL이 결국 **발급자의 권한으로** 동작하기 때문이다.
- `s3:ListBucket`은 넣지 않았다. 업로드·조회에 필요 없다. 운영 중 버킷 목록을 보려면
  **`/*` 없는** 버킷 ARN에 따로 추가한다(없으면 `aws s3 ls`가 `AccessDenied`).

`.env`에 `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`를 **빈 값이나 `CHANGE_ME`로
남겨 두지 말 것.** boto3가 그걸 진짜 키로 믿고 인스턴스 역할을 무시한다.

### 2.3 버킷은 비공개로 둔다

"퍼블릭 액세스 차단"을 켠 상태 그대로 쓴다. 조회는 presigned URL로만 연다.

- 어댑터는 `put_object`에 **`ACL`을 넘기지 않는다.** `ACL="public-read"`를 넣으면
  차단이 켜진 버킷에서 `AccessDenied`가 난다.
- URL 유효기간 기본 1시간. `ADMIN_S3_URL_EXPIRES_IN=초`로 바꾼다.

---

## 3. ⚠️ nginx 업로드 상한 — 가장 놓치기 쉬운 지점

`api.pmhllll12.cloud`의 경로는 **docker 게이트웨이를 거치지 않는다**:

```
클라이언트 → Cloudflare → 호스트 nginx(:443) → 백엔드 컨테이너(127.0.0.1:8000)
```

호스트에 별도로 설치된 nginx(`/etc/nginx/conf.d/api.conf`)가 앞단이고,
`docker/gateway.default.conf`(`client_max_body_size 100m`)는 **이 경로에 관여하지 않는다.**

`client_max_body_size`를 지정하지 않으면 nginx 기본값 **1MB**가 적용돼, 폰 사진
(보통 2~6MB)이 전부 413으로 막힌다. 2026-08-03에 실제로 이 문제를 겪었다.

```nginx
server {
    listen 443 ssl;
    server_name api.pmhllll12.cloud;

    client_max_body_size 12m;   # 앱 규칙 10MB + multipart 오버헤드
    ...
}
```

적용: `sudo nginx -t && sudo nginx -s reload` (무중단).

**증상으로 구분하는 법** — 413의 응답 본문을 보면 어디서 막혔는지 바로 안다.

| 응답 본문 | 막은 주체 | 조치 |
|---|---|---|
| `nginx/x.y.z` 가 적힌 **HTML** | nginx `client_max_body_size` | 위 설정 추가 |
| `{"detail":"이미지 크기는 10MB를…"}` **JSON** | 우리 애플리케이션 | 정상 동작 |

앱이 실패 사유를 서버의 `detail`로 표시하므로, nginx가 막으면 사용자에게는
구체적 사유 없이 "오류 413"만 보인다. 이 증상이 곧 nginx 쪽이라는 신호다.

`auth.pmhllll12.cloud` 블록에는 상한을 넣지 않았다 — 인증은 JSON 토큰만 오가서
1MB를 넘지 않는다. 파일을 다루는 엔드포인트가 생기면 그때 넣는다.

> **이 nginx 설정은 저장소 밖(서버 파일)이라 커밋되지 않는다.** 서버를 새로 만들면
> 반드시 다시 넣어야 한다. 이 문서가 그 기록이다.

---

## 4. 확인 절차

컨테이너 안에서 자격증명이 잡히는지:

```bash
docker exec pmhllll12-all-backend-1 python -c "
import boto3
c = boto3.Session().get_credentials()
print(c and c.method)
print(boto3.client('sts', region_name='ap-northeast-2').get_caller_identity()['Arn'])
"
```

`iam-role` 과 `arn:aws:sts::…:assumed-role/…` 이 나와야 한다.

터널 경유 실제 업로드:

```bash
curl -F "file=@사진.png;type=image/png" https://api.pmhllll12.cloud/api/admin/s3/images
```

- 200 이면 응답의 `url`을 그대로 `curl`해 원본과 바이트가 같은지 본다
- 같은 URL에서 쿼리스트링(서명)을 떼고 요청하면 **403**이어야 한다 — 버킷이
  비공개로 유지되고 있다는 뜻이다

테스트: `pytest apps/admin/tests` (유스케이스 5개, AWS 불필요),
`lint-imports --config pyproject.toml` (계층 계약).
