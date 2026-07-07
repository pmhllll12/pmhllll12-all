#!/usr/bin/env bash
# main.py가 런타임에 구성하는 sys.path(backend root + apps + core)와 동일하게 맞춰야
# import-linter가 실제 import 경로(예: `from titanic...`, `from matrix...`)를 그대로 추적한다.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONPATH="$PWD:$PWD/apps:$PWD/core" lint-imports
