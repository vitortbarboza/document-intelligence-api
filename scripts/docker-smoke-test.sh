#!/usr/bin/env bash
# Start the Docker image against a fresh, temporary volume and verify that
# migrations run, the API becomes healthy and the database is writable.
# The container and the temporary volume are always removed on exit.
#
# Usage: scripts/docker-smoke-test.sh [image] [host-port]
set -euo pipefail

# Keep Git Bash on Windows from rewriting container paths such as /data.
export MSYS_NO_PATHCONV=1

IMAGE="${1:-document-intelligence-api:smoke-test}"
PORT="${2:-18000}"
SUFFIX="$(date +%s)-$$"
CONTAINER="document-intelligence-smoke-${SUFFIX}"
VOLUME="document-intelligence-smoke-${SUFFIX}"
BASE_URL="http://127.0.0.1:${PORT}"

cleanup() {
    docker rm --force "${CONTAINER}" >/dev/null 2>&1 || true
    docker volume rm "${VOLUME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

fail() {
    echo "FAIL: $1" >&2
    echo "--- container logs ---" >&2
    docker logs "${CONTAINER}" >&2 || true
    exit 1
}

docker volume create "${VOLUME}" >/dev/null
docker run --detach \
    --name "${CONTAINER}" \
    --publish "127.0.0.1:${PORT}:8000" \
    --mount "type=volume,source=${VOLUME},target=/data" \
    "${IMAGE}" >/dev/null

# Wait for the Docker health check, which polls /health inside the container.
status="starting"
for _ in $(seq 1 30); do
    status="$(docker inspect --format '{{.State.Health.Status}}' "${CONTAINER}")"
    [ "${status}" = "healthy" ] && break
    [ "$(docker inspect --format '{{.State.Running}}' "${CONTAINER}")" = "true" ] \
        || fail "container exited during startup"
    sleep 2
done
[ "${status}" = "healthy" ] || fail "container did not become healthy (${status})"
echo "OK: container is healthy"

# Output is captured before matching so an early grep exit cannot break a pipe.
logs="$(docker logs "${CONTAINER}" 2>&1)"
[[ "${logs}" == *"Running upgrade"* ]] \
    || fail "Alembic did not apply any migration to the empty database"
revision="$(docker exec "${CONTAINER}" alembic current 2>&1)"
[[ "${revision}" == *"(head)"* ]] \
    || fail "database is not at the latest migration"
echo "OK: migrations applied up to head"

health="$(curl --fail --silent --show-error "${BASE_URL}/health")" \
    || fail "/health did not respond successfully from the host"
[[ "${health}" == *'"status":"ok"'* ]] || fail "unexpected /health body: ${health}"
echo "OK: /health responded from the host"

# Writing a document proves the non-root user can write to the volume.
created_status="$(curl --silent --write-out '\n%{http_code}' \
    --header 'Content-Type: application/json' \
    --data '{"title": "Smoke test", "description": "Created by the smoke test"}' \
    "${BASE_URL}/documents" | tail -n 1)"
[ "${created_status}" = "201" ] \
    || fail "POST /documents returned ${created_status}, expected 201"
echo "OK: database volume is writable"

echo "Docker smoke test passed"
