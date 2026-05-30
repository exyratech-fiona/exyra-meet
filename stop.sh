#!/bin/bash
echo "Stopping Exyra Technologies services..."

# Kill by PID file if available
if [ -f /tmp/exyra_backend.pid ]; then
  kill $(cat /tmp/exyra_backend.pid) 2>/dev/null && echo "  ✓ Backend stopped"
  rm /tmp/exyra_backend.pid
else
  lsof -ti :8000 | xargs kill -9 2>/dev/null && echo "  ✓ Backend stopped"
fi

if [ -f /tmp/exyra_frontend.pid ]; then
  kill $(cat /tmp/exyra_frontend.pid) 2>/dev/null && echo "  ✓ Frontend stopped"
  rm /tmp/exyra_frontend.pid
else
  lsof -ti :3000 | xargs kill -9 2>/dev/null && echo "  ✓ Frontend stopped"
fi

echo "  MySQL container left running (use: docker stop exyra_mysql)"
echo ""
echo "Done. Restart with: ./start.sh"
