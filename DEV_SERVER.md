# 프론트 개발 서버 (`http://localhost:3000` 고정)

이 저장소는 Vite 개발·프리뷰 서버를 **항상 포트 3000**에만 띄웁니다. **`http://localhost:5173` 은 사용하지 않습니다.** (호스트의 `PORT` 나 `VITE_DEV_PORT` 로 개발 포트를 바꾸지 않습니다.)

## `ERR_CONNECTION_REFUSED` 가 나올 때

그 순간 **PC의 3000 포트에서 `npm run dev` 가 돌고 있지 않다**는 뜻입니다. 터미널을 켠 채로 두고, 브라우저는 **`http://localhost:3000`** 으로 접속하세요.

### 실행 방법

저장소 루트:

```bash
npm run dev
```

`frontend` 폴더:

```bash
cd frontend
npm run dev
```

### 하지 말 것

- **`frontend\apps`** 는 Python 예제용입니다. 프론트는 **`frontend`** 또는 루트 **`npm run dev`** 만 쓰세요.
- 백엔드만 켜 두고 프론트 터미널을 끈 뒤 브라우저만 열면 항상 거부됩니다. (API `8000`, UI `3000` — **둘 다** 필요.)

### 포트 3000 이 이미 사용 중일 때

`strictPort: true` 이라 3000이 다른 프로그램에 잡혀 있으면 `npm run dev` 가 **시작 단계에서 실패**합니다. 다른 터미널의 옛날 dev 서버를 끄거나, 3000을 쓰는 프로그램을 종료하세요.

### 백엔드(8000)와 같이 쓸 때

백엔드: `cd backend\apps` 후 `python main.py` (실제 앱은 `backend\main.py` — `apps\main.py` 가 경로를 맞춰 실행)

또는 `cd backend` 후 `python main.py`  
프론트: `npm run dev` — **서로 다른 터미널**에서 동시에 실행합니다.

### `localhost:8000` / `/docs` 가 `ERR_CONNECTION_REFUSED` 일 때

1. **백엔드 터미널이 꺼졌거나 크래시했을 때** 가장 흔합니다. `cd backend` 후 `python main.py` 를 다시 실행하고, **프롬프트가 돌아오지 않은 채 로그만 나오는 상태**를 유지하세요. (이 터미널에서 Ctrl+C 하면 8000 포트가 닫힙니다.)
2. **프론트만 켠 경우** (`npm run dev` 만 실행) 브라우저에서 API나 `/docs` 를 직접 열면 거부됩니다. API는 항상 **백엔드 프로세스**가 받습니다.
3. 백엔드가 `API 준비` 로그 직후 **바로 종료**되고 Windows 콘솔에 `libifcoremd.dll` 등 네이티브 스택이 보이면, Conda/Intel MKL 과 NumPy 조합 이슈일 수 있습니다. `backend\main.py` 에서 Windows 시 `OMP_NUM_THREADS` 등을 1로 제한하도록 이미 설정해 두었습니다. 그래도 반복되면 **가상환경을 새로 만들고** `pip install` 로 numpy 를 다시 설치해 보세요.

## Vercel v0 프리뷰에 대해

v0는 기본적으로 **5173** 을 기다리는 경우가 많습니다. 이 프로젝트는 **3000 고정**이라 **v0 인-브라우저 프리뷰와 맞지 않을 수 있습니다.** v0에서 미리보기가 필요하면 별도 브랜치에서 포트 정책을 조정하거나, Vercel **배포 미리보기**를 사용하는 편이 맞습니다.

## 폰·태블릿에서 접속

터미널에 나오는 **`Network` 주소**(예: `http://192.168.0.10:3000`)로 접속하세요.

**루프백만** 쓰려면 `frontend/.env` 에 `VITE_DEV_LOCALHOST=1` 을 넣을 수 있습니다. 이 경우 폰의 `Network` 주소로는 접속되지 않을 수 있습니다.

### 빌드된 앱·웹뷰가 API를 직접 호출하는 경우

`VITE_API_BASE=http://<PC_LAN_IP>:8000` 로 빌드하고, 필요 시 백엔드는 `API_HOST=0.0.0.0` (신뢰 네트워크에서만).
