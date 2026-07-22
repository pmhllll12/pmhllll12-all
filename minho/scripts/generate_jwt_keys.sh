#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

openssl genrsa -out jwt_private.pem 2048
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem

echo
echo "jwt_private.pem -> .env.auth 의 JWT_PRIVATE_KEY 로 (auth 컨테이너 전용)"
echo "jwt_public.pem  -> .env.backend 의 JWT_PUBLIC_KEY 로 (백엔드 등 검증부 공용)"
echo
echo "멀티라인 PEM을 env var로 그대로 넣기 번거로우면 base64 한 줄로 인코딩해서 써도 된다"
echo "(core/security.py가 PEM/base64 둘 다 받아들인다):"
echo "  JWT_PRIVATE_KEY=\$(base64 -w0 jwt_private.pem)"
echo "  JWT_PUBLIC_KEY=\$(base64 -w0 jwt_public.pem)"
