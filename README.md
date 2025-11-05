# Local Web Development Environment

A full-stack web application with Node.js frontend and Python Flask backend API, using SQLite database for local prototyping and development.

## Architecture

- **Frontend**: Node.js + Express + EJS templates (Port 3000)
- **Backend**: Python Flask REST API (Port 5000)
- **Database**: SQLite (file-based)
- **Communication**: RESTful API with CORS enabled

## Stack

### Backend (Python)
- **Framework**: Flask 3.0.0
- **Database ORM**: SQLAlchemy via Flask-SQLAlchemy
- **CORS**: Flask-CORS 4.0.0
- **Python Version**: 3.11.9

### Frontend (Node.js)
- **Framework**: Express.js
- **Template Engine**: EJS
- **HTTP Client**: Axios
- **Node Version**: 22.20.0

## Project Structure

```
radiocalico/
├── backend/                    # Python Flask API
│   ├── app.py                 # Main Flask application & API routes
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Backend environment variables
│   ├── database.db           # SQLite database (created on first run)
│   └── venv/                 # Python virtual environment
│
├── frontend/                   # Node.js frontend
│   ├── server.js             # Express server
│   ├── package.json          # Node dependencies
│   ├── .env                  # Frontend environment variables
│   ├── views/                # EJS templates
│   │   ├── index.ejs
│   │   ├── users.ejs
│   │   ├── add_user.ejs
│   │   └── add_post.ejs
│   ├── public/               # Static files
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   └── node_modules/         # Node packages
│
└── README.md                  # This file
```

## Setup Instructions

### Backend Setup (Python)

1. Navigate to backend directory:
```bash
cd backend
```

2. Activate virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies (already installed):
```bash
pip install -r requirements.txt
```

4. Initialize and seed the database:
```bash
flask seed-db
```

### Frontend Setup (Node.js)

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies (already installed):
```bash
npm install
```

## Running the Application

You need to run both the backend and frontend servers simultaneously.

### Terminal 1 - Start Backend API

```bash
cd backend
source venv/bin/activate
python app.py
```

Backend API will start at: **http://localhost:5000**

### Terminal 2 - Start Frontend Server

```bash
cd frontend
npm start
```

Frontend server will start at: **http://localhost:3000**

### Access the Application

Open your browser and visit: **http://localhost:3000**

## API Endpoints

### Health Check
- `GET /api/health` - API health check

### Users
- `GET /api/users` - Get all users
- `GET /api/users/:id` - Get user by ID
- `POST /api/users` - Create new user
  - Body: `{ "username": "string", "email": "string" }`
- `DELETE /api/users/:id` - Delete user

### Posts
- `GET /api/posts` - Get all posts
- `GET /api/posts/:id` - Get post by ID
- `POST /api/posts` - Create new post
  - Body: `{ "title": "string", "content": "string", "user_id": number }`
- `DELETE /api/posts/:id` - Delete post

## Frontend Routes

- `/` - Home page (displays all posts)
- `/users` - View all users
- `/user/add` - Add a new user
- `/post/add` - Create a new post

## Database Models

### User Model
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `created_at`: Timestamp of account creation
- `posts`: Relationship to user's posts

### Post Model
- `id`: Primary key
- `title`: Post title
- `content`: Post content
- `user_id`: Foreign key to User
- `author`: Username of post author
- `created_at`: Timestamp of post creation

## Environment Variables

### Backend ([backend/.env](backend/.env))
```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=sqlite:///database.db
SECRET_KEY=dev-secret-key-change-in-production
```

### Frontend ([frontend/.env](frontend/.env))
```env
PORT=3000
API_URL=http://localhost:5000/api
```

## Development Tips

### Accessing the Database Directly

```bash
cd backend
sqlite3 database.db
```

Common SQLite commands:
```sql
.tables                    -- List all tables
.schema users              -- Show table structure
SELECT * FROM users;       -- Query users
SELECT * FROM posts;       -- Query posts
.quit                      -- Exit SQLite
```

### Testing the API Directly

You can test the API using curl:

```bash
# Get all users
curl http://localhost:5000/api/users

# Get all posts
curl http://localhost:5000/api/posts

# Create a new user
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com"}'

# Create a new post
curl -X POST http://localhost:5000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Post","content":"This is a test","user_id":1}'
```

### Development Mode

For auto-reload during development:

**Frontend** (already configured):
```bash
npm run dev  # Uses nodemon for auto-reload
```

**Backend**:
```bash
flask run  # Flask debug mode auto-reloads
```

### Adding New Features

1. **Add Backend API Route**:
   - Edit [backend/app.py](backend/app.py)
   - Add new route with `@app.route('/api/endpoint')`
   - Return JSON responses with `jsonify()`

2. **Add Frontend Page**:
   - Create new EJS template in [frontend/views/](frontend/views/)
   - Add route in [frontend/server.js](frontend/server.js)
   - Use `apiCall()` helper to fetch data from backend

## Flask CLI Commands

```bash
cd backend
source venv/bin/activate

# Initialize database
flask init-db

# Seed database with sample data
flask seed-db
```

## Stopping the Servers

Press `Ctrl+C` in each terminal window running the servers.

## Next Steps

- Add user authentication (Flask-Login + JWT)
- Add form validation (Flask-WTF + client-side validation)
- Implement pagination for large datasets
- Add search functionality
- Add update (PUT/PATCH) endpoints
- Add client-side JavaScript for dynamic features
- Add error pages (404, 500)
- Deploy to a hosting service

## Troubleshooting

### Port Already in Use

**Backend:**
```bash
# Change port in backend/app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Frontend:**
```bash
# Change port in frontend/.env
PORT=3001
```

### CORS Errors

Make sure the backend is running and CORS is properly configured in [backend/app.py](backend/app.py):
```python
CORS(app, origins=['http://localhost:3000'])
```

### API Connection Failed

1. Verify backend is running on port 5000
2. Check [frontend/.env](frontend/.env) has correct `API_URL`
3. Check browser console for detailed error messages

### Database Locked Error

Close any database browser tools or other processes accessing the database file.

### Module Not Found (Python)

Make sure virtual environment is activated:
```bash
cd backend
source venv/bin/activate
```

### Module Not Found (Node.js)

Reinstall dependencies:
```bash
cd frontend
npm install
```

## Resources

### Backend
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-CORS Documentation](https://flask-cors.readthedocs.io/)

### Frontend
- [Express.js Documentation](https://expressjs.com/)
- [EJS Documentation](https://ejs.co/)
- [Axios Documentation](https://axios-http.com/)

## Quick Start Summary

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
flask seed-db
python app.py

# Terminal 2 - Frontend
cd frontend
npm start

# Open browser
# http://localhost:3000
```
