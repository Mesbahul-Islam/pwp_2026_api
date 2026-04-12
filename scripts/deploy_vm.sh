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
REMOVE_PORT_CONFLICTS="${VM_REMOVE_PORT_CONFLICTS:-true}"

declare -a HOST_PORTS=()

add_host_port() {
  local port="$1"
  if [[ ! "$port" =~ ^[0-9]+$ ]]; then
    return
  fi
  local existing
  for existing in "${HOST_PORTS[@]:-}"; do
    if [[ "$existing" == "$port" ]]; then
      return
    fi
  done
  HOST_PORTS+=("$port")
}

extract_host_port() {
  local spec="$1"
  spec="${spec%%/*}"
  IFS=':' read -r -a parts <<< "$spec"
  local n="${#parts[@]}"
  local host_port=""
  if [[ "$n" -eq 2 ]]; then
    host_port="${parts[0]}"
  elif [[ "$n" -ge 3 ]]; then
    host_port="${parts[$((n - 2))]}"
  fi
  add_host_port "$host_port"
}

parse_published_ports() {
  read -r -a arg_tokens <<< "$RUN_ARGS"
  local i token next
  for ((i = 0; i < ${#arg_tokens[@]}; i++)); do
    token="${arg_tokens[$i]}"
    case "$token" in
      -p|--publish)
        if ((i + 1 < ${#arg_tokens[@]})); then
          next="${arg_tokens[$((i + 1))]}"
          extract_host_port "$next"
        fi
        ;;
      -p=*|--publish=*)
        extract_host_port "${token#*=}"
        ;;
    esac
  done
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Current directory is not inside a git repository."
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

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

if [[ "$REMOVE_PORT_CONFLICTS" == "true" ]]; then
  parse_published_ports
  for port in "${HOST_PORTS[@]:-}"; do
    mapfile -t conflict_ids < <(docker ps -q --filter "publish=${port}")
    for id in "${conflict_ids[@]:-}"; do
      name="$(docker inspect --format '{{.Name}}' "$id" | sed 's#^/##')"
      if [[ "$name" != "$CONTAINER" ]]; then
        echo "Removing conflicting container $name on host port $port"
        docker rm -f "$id" >/dev/null || true
      fi
    done
  done
fi

echo "Replacing container $CONTAINER"
docker rm -f "$CONTAINER" 2>/dev/null || true
docker run --name "$CONTAINER" $RUN_ARGS "$IMAGE"
