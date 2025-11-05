#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  RadioCalico Development Environment${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if database exists
if [ ! -f "backend/database.db" ]; then
    echo -e "${YELLOW}Database not found. Creating and seeding database...${NC}"
    cd backend
    source venv/bin/activate
    flask seed-db
    deactivate
    cd ..
    echo -e "${GREEN}✓ Database created and seeded${NC}\n"
fi

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✓ Servers stopped${NC}"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${BLUE}Starting Python Backend API...${NC}"
cd backend
source venv/bin/activate
python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
deactivate
cd ..

# Wait for backend to start
sleep 2

# Check if backend started successfully
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✓ Backend running on http://localhost:5000 (PID: $BACKEND_PID)${NC}\n"
else
    echo -e "${RED}✗ Backend failed to start. Check backend.log for errors.${NC}"
    exit 1
fi

# Start frontend
echo -e "${BLUE}Starting Node.js Frontend Server...${NC}"
cd frontend
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 3

# Check if frontend started successfully
if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✓ Frontend running on http://localhost:3000 (PID: $FRONTEND_PID)${NC}\n"
else
    echo -e "${RED}✗ Frontend failed to start. Check frontend.log for errors.${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🚀 Application is ready!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo -e "Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "Backend API: ${BLUE}http://localhost:5000${NC}\n"
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}\n"
echo -e "Logs:"
echo -e "  - Backend: ${BLUE}backend.log${NC}"
echo -e "  - Frontend: ${BLUE}frontend.log${NC}\n"

# Keep script running and show logs
tail -f backend.log frontend.log
