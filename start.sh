#!/bin/bash
# Exyra Technologies — Start All Services in Background

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}  ╔═══════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}  ║    Exyra Technologies v1.0.0      ║${NC}"
echo -e "${CYAN}${BOLD}  ║    Batch Management Platform      ║${NC}"
echo -e "${CYAN}${BOLD}  ╚═══════════════════════════════════╝${NC}"
echo ""

ROOT="$(cd "$(dirname "$0")" && pwd)"

# ─── 1. MySQL ─────────────────────────────────────────────────────────────────
echo -e "${YELLOW}▶ Starting MySQL...${NC}"
if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q "exyra_mysql"; then
  docker run -d \
    --name exyra_mysql \
    -e MYSQL_ROOT_PASSWORD=exyra_root_2024 \
    -e MYSQL_DATABASE=exyra_meet \
    -e MYSQL_USER=exyra \
    -e MYSQL_PASSWORD=exyra_pass_2024 \
    -p 3306:3306 \
    --restart unless-stopped \
    mysql:8.0 \
    --character-set-server=utf8mb4 \
    --collation-server=utf8mb4_unicode_ci > /dev/null 2>&1
  echo -e "  ${GREEN}✓ MySQL container started${NC}"
  printf "  Waiting for MySQL"
  for i in $(seq 1 30); do
    docker exec exyra_mysql mysqladmin ping -h localhost -u exyra -pexyra_pass_2024 --silent 2>/dev/null && break
    printf "."; sleep 2
  done
  echo ""
else
  echo -e "  ${GREEN}✓ MySQL already running${NC}"
fi

# ─── 2. Backend ───────────────────────────────────────────────────────────────
echo -e "${YELLOW}▶ Starting Backend (FastAPI on :8000)...${NC}"
lsof -ti :8000 | xargs kill -9 2>/dev/null; sleep 1

cd "$ROOT/backend"
if [ ! -d "venv" ]; then
  echo "  Installing Python dependencies..."
  python3.12 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt -q
else
  source venv/bin/activate
fi

nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/exyra_backend.log 2>&1 &
echo $! > /tmp/exyra_backend.pid

sleep 3
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
  echo -e "  ${GREEN}✓ Backend running${NC} (PID $(cat /tmp/exyra_backend.pid))"
else
  echo -e "  ${RED}✗ Backend failed — check: tail -f /tmp/exyra_backend.log${NC}"
fi

# ─── 3. Frontend ──────────────────────────────────────────────────────────────
echo -e "${YELLOW}▶ Starting Frontend (Next.js on :3000)...${NC}"
lsof -ti :3000 | xargs kill -9 2>/dev/null; sleep 1

cd "$ROOT/frontend"
if [ ! -d "node_modules" ]; then
  echo "  Installing npm packages..."
  npm install --legacy-peer-deps -q
fi

nohup npm run dev -- --port 3000 > /tmp/exyra_frontend.log 2>&1 &
echo $! > /tmp/exyra_frontend.pid

sleep 6
HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ --max-time 5)
if [ "$HTTP" = "200" ]; then
  echo -e "  ${GREEN}✓ Frontend running${NC} (PID $(cat /tmp/exyra_frontend.pid))"
else
  echo -e "  ${RED}✗ Frontend failed — check: tail -f /tmp/exyra_frontend.log${NC}"
fi

# ─── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}  ════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✅  Exyra Technologies is RUNNING!${NC}"
echo -e "${GREEN}${BOLD}  ════════════════════════════════════════${NC}"
echo ""
echo -e "  ${CYAN}App        →${NC}  http://localhost:3000"
echo -e "  ${CYAN}API        →${NC}  http://localhost:8000"
echo -e "  ${CYAN}API Docs   →${NC}  http://localhost:8000/api/docs"
echo -e "  ${CYAN}DB         →${NC}  127.0.0.1:3306 / exyra_meet"
echo ""
echo -e "  ${YELLOW}First time setup:${NC}"
echo -e "  • Integrations guide: ${CYAN}docs/SETUP_INTEGRATIONS.md${NC}"
echo -e "  • Google Meet auth:   ${CYAN}http://localhost:8000/api/setup/google-calendar${NC}"
echo -e "  • Check status:       ${CYAN}http://localhost:8000/api/setup/status${NC}"
echo ""
echo -e "  Logs: ${CYAN}tail -f /tmp/exyra_backend.log${NC}"
echo -e "  Stop: ${CYAN}./stop.sh${NC}"
echo ""
