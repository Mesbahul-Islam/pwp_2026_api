#!/usr/bin/env bash

set -euo pipefail

SKIP_PULL=false
if [[ "${1:-}" == "--skip-pull" ]]; then
  SKIP_PULL=true
fi

BRANCH="${VM_GIT_BRANCH:-deployment}"
IMAGE="${VM_DOCKER_IMAGE:-eyesedge-api:latest}"
CONTAINER="${VM_CONTAINER_NAME:-eyesedge-api}"
BUILD_CONTEXT="${VM_DOCKER_BUILD_CONTEXT:-.}"
RUN_ARGS="${VM_DOCKER_RUN_ARGS:--d --restart unless-stopped -p 8000:8000}"
DOCKERFILE="${VM_DOCKERFILE:-}"

if [[ ! -d .git ]]; then
  echo "Current directory is not a git repository."
  exit 1
fi

if [[ "$SKIP_PULL" != "true" ]]; then
  git fetch origin "$BRANCH"
  git checkout "$BRANCH"
  git pull --ff-only origin "$BRANCH"
fi

DOCKERFILE_ARG=""
if [[ -n "$DOCKERFILE" ]]; then
  DOCKERFILE_ARG="-f $DOCKERFILE"
fi

echo "Building image $IMAGE"
docker build $DOCKERFILE_ARG -t "$IMAGE" "$BUILD_CONTEXT"

echo "Replacing container $CONTAINER"
docker rm -f "$CONTAINER" 2>/dev/null || true
docker run --name "$CONTAINER" $RUN_ARGS "$IMAGE"
