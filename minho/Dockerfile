# 1. 파이썬 기본 이미지 가져오기 (3.13)
FROM python:3.13-slim

# 2. 컨테이너 내부 작업 디렉토리 설정
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. LightGBM/OpenCV 의존 시스템 라이브러리 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# 4. 라이브러리 목록 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 나머지 소스 코드 전부 복사
COPY . .

# 5. Neon DB 마이그레이션(Alembic) 후 FastAPI (기본 8000, API_PORT 로 변경 가능)
EXPOSE 8000
CMD ["python", "docker_entrypoint.py"]
