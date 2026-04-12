## EyesEdge API Deployment Guide (VM)

This document describes how to deploy and maintain the API on a Linux VM using Docker.

## 1. Components To Install

Install these components on the VM:

- Git
- Docker Engine
- Docker CLI plugin for Docker Compose (optional)
- Bash (already present on Ubuntu)
- OpenSSH server/client
- Certbot (for certificate creation and renewal)

Ubuntu installation example:

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin openssh-client certbot
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

After adding the user to the docker group, re-login once.

## 2. Start After SSH Into VM

SSH into the VM:

```bash
ssh ubuntu@86.50.20.115
```

Go to the repository root and API folder:

```bash
cd ~/pwp_2026/api
```

If repository is not present yet, clone it first:

```bash
cd ~
git clone https://github.com/Mesbahul-Islam/pwp_2026_api.git pwp_2026
cd ~/pwp_2026/api
git checkout deployment
```

## 3. Environment Setup

Create runtime environment file:

```bash
cp .env.example .env
```

Edit `.env` and set production values:

```env
SECRET_KEY=replace-with-strong-random-secret
DEBUG=False
ALLOWED_HOSTS=86.50.20.115
```

Notes:

- `DEBUG` must be `False` for production.
- `ALLOWED_HOSTS` must include the public VM IP or domain.
- `SECRET_KEY` must be unique and private.

## 4. Deploy The API

Deployment script:

- `scripts/deploy_vm.sh`

What it does:

- Pulls latest changes from `deployment` branch
- Builds Docker image
- Stops/replaces running API container
- Removes port-conflicting containers (by default)
- Starts the new container

Run deployment:

```bash
bash scripts/deploy_vm.sh
```

If docker permission is denied:

```bash
sudo bash scripts/deploy_vm.sh
```

Optional runtime overrides:

```bash
VM_GIT_BRANCH=deployment \
VM_DOCKER_IMAGE=eyesedge-api:latest \
VM_CONTAINER_NAME=eyesedge-api \
VM_DOCKER_RUN_ARGS="-d --restart unless-stopped -p 8000:8000 --env-file .env" \
bash scripts/deploy_vm.sh
```

## 5. Verify Deployment Is Working

Check running container:

```bash
docker ps --filter name=eyesedge-api
```

Check container logs:

```bash
docker logs --tail 100 eyesedge-api
```

Check endpoint response:

```bash
curl -I http://86.50.20.115:8000/api/schema/
curl -I http://86.50.20.115:8000/api/docs/
```

Expected result: HTTP 200 or redirect to docs page.

## 6. Run Tests To Validate Environment

### API behavior smoke checks from VM

```bash
curl -s http://127.0.0.1:8000/api/schema/ | head
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/api/docs/
```

### Optional project test suite

Run test suite from source environment (not inside runtime container):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py test -v 2
```

## 7. Troubleshooting

- Port already allocated: stop conflicting container or use another host port in `VM_DOCKER_RUN_ARGS`.
- Git pull blocked by local changes: `git stash -u`, deploy, then review stash.
- Container exits quickly: check `docker logs eyesedge-api`.
- Static files error: ensure `STATIC_ROOT` is configured (already set in project settings).


