# Quick Start Guide

## 🚀 Start Everything (Easiest Method)

Run this single command to start both backend and frontend:

```bash
./start.sh
```

This script will:
1. Create and seed the database if needed
2. Start the Python backend API (port 5000)
3. Start the Node.js frontend (port 3000)
4. Open logs for both servers

Then open your browser to: **http://localhost:3000**

Press `Ctrl+C` to stop both servers.

---

## 🔧 Manual Start (Two Terminals)

If you prefer to run servers manually in separate terminals:

### Terminal 1 - Backend

```bash
cd backend
source venv/bin/activate
flask seed-db  # Only needed first time
python app.py
```

Backend runs at: http://localhost:5000

### Terminal 2 - Frontend

```bash
cd frontend
npm start
```

Frontend runs at: http://localhost:3000

---

## 📋 What's Available

### Pages (http://localhost:3000)
- **/** - Home page with all posts
- **/users** - List all users
- **/user/add** - Add a new user
- **/post/add** - Create a new post

### API Endpoints (http://localhost:5000/api)
- `GET /api/health` - Health check
- `GET /api/users` - Get all users
- `GET /api/posts` - Get all posts
- `POST /api/users` - Create user
- `POST /api/posts` - Create post

---

## 🧪 Test the API

```bash
# Health check
curl http://localhost:5000/api/health

# Get all users
curl http://localhost:5000/api/users

# Get all posts
curl http://localhost:5000/api/posts
```

---

## 📁 Project Structure

```
radiocalico/
├── backend/           # Python Flask API
│   ├── app.py        # API routes & database models
│   └── venv/         # Python virtual environment
│
├── frontend/         # Node.js Express server
│   ├── server.js    # Express routes
│   ├── views/       # EJS templates
│   └── public/      # CSS, JS, images
│
└── start.sh         # Start both servers
```

---

## 🛠️ Common Tasks

### Reset Database

```bash
cd backend
source venv/bin/activate
flask seed-db
```

### View Database

```bash
cd backend
sqlite3 database.db
```

Then use SQL:
```sql
SELECT * FROM users;
SELECT * FROM posts;
.quit
```

### Check Logs

If using `start.sh`:
```bash
tail -f backend.log
tail -f frontend.log
```

---

## ❓ Troubleshooting

### Port Already in Use

Change ports in:
- Backend: `backend/app.py` (line with `app.run`)
- Frontend: `frontend/.env` (`PORT=3000`)

### Can't Connect to API

1. Check backend is running: `curl http://localhost:5000/api/health`
2. Check CORS settings in `backend/app.py`
3. Verify `frontend/.env` has `API_URL=http://localhost:5000/api`

### Missing Dependencies

**Backend:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

---

## 📚 Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the API endpoints
3. Customize the templates in `frontend/views/`
4. Add new routes in `backend/app.py` and `frontend/server.js`
5. Check out the architecture in [README.md](README.md#architecture)

---

**Happy Coding!** 🎉
