# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
│                   (http://localhost:3000)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP Requests
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Node.js Frontend Server                     │
│                     (Express + EJS)                          │
│                      Port 3000                               │
├─────────────────────────────────────────────────────────────┤
│  Routes:                                                     │
│  • GET  /           → Render home page                       │
│  • GET  /users      → Render users page                      │
│  • GET  /user/add   → Render add user form                   │
│  • POST /user/add   → Submit new user                        │
│  • GET  /post/add   → Render add post form                   │
│  • POST /post/add   → Submit new post                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Axios HTTP Requests
                            │ (RESTful API calls)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Python Backend API                          │
│                    (Flask + CORS)                            │
│                      Port 5000                               │
├─────────────────────────────────────────────────────────────┤
│  API Endpoints:                                              │
│  • GET    /api/health            → Health check              │
│  • GET    /api/users             → List all users            │
│  • GET    /api/users/:id         → Get single user           │
│  • POST   /api/users             → Create user               │
│  • DELETE /api/users/:id         → Delete user               │
│  • GET    /api/posts             → List all posts            │
│  • GET    /api/posts/:id         → Get single post           │
│  • POST   /api/posts             → Create post               │
│  • DELETE /api/posts/:id         → Delete post               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ SQLAlchemy ORM
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQLite Database                           │
│                    (database.db)                             │
├─────────────────────────────────────────────────────────────┤
│  Tables:                                                     │
│  • users (id, username, email, created_at)                   │
│  • posts (id, title, content, user_id, created_at)           │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend Layer
- **Runtime**: Node.js v22.20.0
- **Framework**: Express.js 4.18.2
- **Template Engine**: EJS 3.1.9
- **HTTP Client**: Axios 1.6.0
- **Purpose**: Server-side rendering, routing, API consumption

### Backend Layer
- **Runtime**: Python 3.11.9
- **Framework**: Flask 3.0.0
- **ORM**: SQLAlchemy (via Flask-SQLAlchemy 3.1.1)
- **CORS**: Flask-CORS 4.0.0
- **Purpose**: RESTful API, business logic, database operations

### Data Layer
- **Database**: SQLite (file-based)
- **Location**: `backend/database.db`
- **Purpose**: Persistent data storage

## Communication Flow

### Example: Adding a New Post

1. **User** fills out form at `http://localhost:3000/post/add`
2. **Frontend** receives POST request to `/post/add`
3. **Frontend** makes API call: `POST http://localhost:5000/api/posts`
   - Body: `{ title, content, user_id }`
4. **Backend** receives API request
5. **Backend** validates data
6. **Backend** creates Post object using SQLAlchemy
7. **Backend** commits to database
8. **Backend** returns JSON: `{ message, post: {...} }`
9. **Frontend** receives response
10. **Frontend** redirects user to home page
11. **User** sees new post displayed

## Security Features

- **CORS**: Configured to only accept requests from `http://localhost:3000`
- **Input Validation**: Server-side validation on all POST requests
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **Environment Variables**: Sensitive config stored in `.env` files
- **Secret Key**: Flask secret key for session management

## Scalability Considerations

### Current Setup (Development)
- SQLite database (single file)
- No authentication
- No caching
- Single server instances

### Production Recommendations
- Migrate to PostgreSQL or MySQL
- Add Redis for caching
- Implement JWT authentication
- Use Gunicorn/uWSGI for Python
- Use PM2 for Node.js
- Add rate limiting
- Implement proper logging
- Set up monitoring

## File Organization

```
Frontend Files:
frontend/
├── server.js          # Express app, routes, API calls
├── package.json       # Dependencies
├── .env              # Frontend config
├── views/            # EJS templates
│   ├── index.ejs     # Home page
│   ├── users.ejs     # Users list
│   ├── add_user.ejs  # Add user form
│   └── add_post.ejs  # Add post form
└── public/           # Static assets
    ├── css/
    │   └── style.css # Shared styles
    └── js/           # Client-side JS (future)

Backend Files:
backend/
├── app.py            # Flask app, API routes, models
├── requirements.txt  # Python dependencies
├── .env             # Backend config
├── venv/            # Virtual environment
└── database.db      # SQLite database (gitignored)
```

## Development Workflow

1. **Start Backend**: Activates venv, runs Flask on port 5000
2. **Start Frontend**: Runs Express on port 3000
3. **Make Changes**: 
   - Backend changes require server restart
   - Frontend can use nodemon for auto-reload
4. **Test API**: Use curl, Postman, or browser dev tools
5. **Test UI**: Access at http://localhost:3000

## API Response Format

### Success Response
```json
{
  "users": [...],
  "message": "Success"
}
```

### Error Response
```json
{
  "error": "Error message"
}
```

### Model Serialization
Models include `to_dict()` method for JSON conversion:

```python
class User(db.Model):
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
```

## Environment Configuration

### Backend (.env)
```
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=sqlite:///database.db
SECRET_KEY=dev-secret-key
```

### Frontend (.env)
```
PORT=3000
API_URL=http://localhost:5000/api
```

## Benefits of This Architecture

1. **Separation of Concerns**: Frontend handles presentation, backend handles data
2. **Technology Freedom**: Can swap frontend/backend independently
3. **API First**: Backend can be used by mobile apps, other frontends
4. **Scalability**: Can deploy frontend and backend separately
5. **Developer Experience**: Use best tools for each layer
6. **Testability**: Can test API and UI independently
