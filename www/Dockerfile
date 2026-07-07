# 1. Node.js 기본 이미지 가져오기 (v24.15.0)
FROM node:24.15.0-alpine

# 2. 컨테이너 내부 작업 디렉토리 설정
WORKDIR /app

# 3. 패키지 목록 복사 및 설치 (빌드에 devDependencies 필요)
COPY package*.json ./
RUN npm install

# 4. 나머지 소스 코드 전부 복사
COPY . .

# 5. 프로덕션 빌드: API 는 상대 경로(`/api/...`) — next.config.ts rewrites 가 백엔드로 프록시
RUN npm run build

ENV NODE_ENV=production
EXPOSE 3000
CMD ["npm", "run", "start"]
