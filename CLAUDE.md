# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Radio Calico is a full-stack streaming radio web application with:
- **Frontend**: Node.js/Express.js serving EJS templates + HLS.js for audio streaming (Port 3000)
- **Backend**: Python Flask REST API with SQLAlchemy ORM (Port 5000)
- **Database**: SQLite (file-based at `backend/instance/database.db`)
- **Audio**: 48kHz FLAC/HLS lossless streaming from CloudFront CDN

## Running the Application

### Quick Start (One Command)
```bash
./start.sh
```
This starts both backend (port 5000) and frontend (port 3000) servers in the background.

### Manual Start (Two Terminals)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Access at: http://localhost:3000

### Database Commands

```bash
cd backend
source venv/bin/activate

# Recreate and seed database with sample data
flask seed-db

# Initialize empty database
flask init-db
```

## Architecture

### Key Architectural Patterns

1. **Song Auto-Creation on Metadata Fetch**: When `/api/nowplaying` or `/api/trackhistory` fetches track metadata from the streaming service, songs are automatically created in the database if they don't exist. This uses a unique constraint on `(title, artist)` to prevent duplicates.

2. **Anonymous User Identification**: The rating system uses browser localStorage to generate and store a unique anonymous user ID (`user_<timestamp>_<random>`). No authentication is required - users are tracked client-side only.

3. **Rating Edit Pattern**: Users can change their rating by clicking the opposite button (thumbs up ↔ thumbs down). The backend updates the existing rating record rather than creating a new one. Database constraint ensures one rating per user per song.

4. **Real-time Metadata Updates**:
   - Frontend polls `/api/nowplaying` every 10 seconds
   - Frontend polls `/api/trackhistory` every 30 seconds
   - Both update the UI and check user's existing ratings

### Data Flow for Rating Feature

```
User clicks rating button
  → Frontend: rateSong(context, ratingType)
  → POST /api/songs/{song_id}/rate with user_identifier from localStorage
  → Backend: Check existing rating for (song_id, user_identifier)
    → If exists && different type: Update rating, return updated: true
    → If exists && same type: Return unchanged, updated: false
    → If not exists: Create new rating
  → Frontend: Update button highlights and counts
  → Frontend: Check user's rating via GET /api/songs/{song_id}/user-rating/{user_id}
```

### Database Models

**Song Model** (`backend/app.py:66-89`):
- Unique constraint on `(title, artist)` prevents duplicate song entries
- `to_dict()` calculates thumbs_up/thumbs_down counts via Rating queries

**Rating Model** (`backend/app.py:91-112`):
- Unique constraint on `(song_id, user_identifier)` enforces one rating per user per song
- Stores anonymous user ID from browser localStorage

**User/Post Models**: Legacy community features, not used by main radio functionality

## Important Files

### Backend
- `backend/app.py` - All Flask routes, database models, and API endpoints in a single file
  - Lines 66-112: Song and Rating models
  - Lines 121-188: Now Playing and Track History endpoints (auto-create songs)
  - Lines 414-478: Rating endpoints (create/update ratings)

### Frontend
- `frontend/server.js` - Express routes and server configuration
- `frontend/views/index.ejs` - Main radio player UI with rating buttons
  - Lines 184-307: Rating JavaScript (getUserIdentifier, checkUserRating, rateSong)
  - Lines 350-456: Track history rendering with ratings
- `frontend/public/css/style.css:539-607` - Rating button styles

## API Endpoints

### Radio Streaming
- `GET /api/nowplaying` - Current track with song_id, thumbs_up, thumbs_down
- `GET /api/trackhistory` - Recent tracks with rating stats

### Ratings
- `POST /api/songs/{song_id}/rate` - Submit or update rating (body: `{user_identifier, rating_type: 'up'|'down'}`)
- `GET /api/songs/{song_id}/user-rating/{user_identifier}` - Check if user rated song
- `GET /api/songs/{song_id}/ratings` - Get rating statistics

### Legacy (User/Post management)
- `GET/POST /api/users`, `GET/POST/DELETE /api/posts`

## Development Notes

### Flask Auto-Reload
Backend runs in debug mode and auto-reloads on file changes. No need to restart when editing `backend/app.py`.

### Frontend Auto-Reload
Frontend uses nodemon and automatically restarts when `server.js` or view files change.

### Testing Ratings with curl
```bash
# Rate a song
curl -X POST http://localhost:5000/api/songs/1/rate \
  -H 'Content-Type: application/json' \
  -d '{"user_identifier": "test_user_123", "rating_type": "up"}'

# Change rating
curl -X POST http://localhost:5000/api/songs/1/rate \
  -H 'Content-Type: application/json' \
  -d '{"user_identifier": "test_user_123", "rating_type": "down"}'

# Check user's rating
curl http://localhost:5000/api/songs/1/user-rating/test_user_123

# Get rating stats
curl http://localhost:5000/api/nowplaying
```

### CSS Variable System
Uses CSS custom properties for theming (`style.css:3-11`):
- `--mint`, `--forest-green`, `--teal`, `--calico-orange`, `--charcoal`, `--cream`, `--white`

### HLS.js Audio Streaming
Audio playback uses HLS.js library loaded from CDN (`index.ejs:103-147`). Stream URL: `https://d3d4yli4hf5bmh.cloudfront.net/hls/live.m3u8`

## Common Patterns

### Adding a New API Endpoint

1. Add route in `backend/app.py`:
```python
@app.route('/api/endpoint', methods=['GET', 'POST'])
def endpoint_name():
    try:
        # Logic here
        return jsonify({...}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

2. Access from frontend via fetch:
```javascript
const response = await fetch('http://localhost:5000/api/endpoint');
const data = await response.json();
```

### Adding a New Database Model

1. Define model in `backend/app.py` with `to_dict()` method
2. Run `flask seed-db` to recreate database with new schema
3. Model relationships use SQLAlchemy's `db.relationship()` and `db.ForeignKey()`

### Frontend-Backend Communication

Frontend uses native `fetch()` API for all backend communication. No Axios dependency in the actual frontend code despite being in package.json.

## Known Limitations

- No user authentication (ratings use anonymous localStorage IDs only)
- SQLite database (not suitable for production/high concurrency)
- Single-file backend (`app.py` contains all routes and models)
- Metadata endpoints are external and may fail (fallback data provided)
- No pagination on track history or rating queries
