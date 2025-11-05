from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize CORS
CORS(app, origins=['http://localhost:3000'])

# Initialize database
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'post_count': len(self.posts)
        }

    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'author': self.user.username,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Post {self.title}>'

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200))
    # Composite unique constraint to ensure same song isn't added multiple times
    __table_args__ = (db.UniqueConstraint('title', 'artist', name='_title_artist_uc'),)

    def to_dict(self):
        # Calculate rating stats
        thumbs_up = Rating.query.filter_by(song_id=self.id, rating_type='up').count()
        thumbs_down = Rating.query.filter_by(song_id=self.id, rating_type='down').count()

        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'thumbs_up': thumbs_up,
            'thumbs_down': thumbs_down
        }

    def __repr__(self):
        return f'<Song {self.title} by {self.artist}>'

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    user_identifier = db.Column(db.String(100), nullable=False)  # Anonymous user ID from browser
    rating_type = db.Column(db.String(10), nullable=False)  # 'up' or 'down'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Ensure one rating per user per song
    __table_args__ = (db.UniqueConstraint('song_id', 'user_identifier', name='_song_user_uc'),)

    song = db.relationship('Song', backref=db.backref('ratings', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'song_id': self.song_id,
            'rating_type': self.rating_type,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Rating {self.rating_type} for Song {self.song_id}>'

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'API is running'}), 200

@app.route('/api/nowplaying', methods=['GET'])
def get_now_playing():
    """Get current track information from Radio Calico stream"""
    try:
        # Fetch metadata from Radio Calico CloudFront endpoint
        response = requests.get('https://d3d4yli4hf5bmh.cloudfront.net/metadata.json', timeout=5)

        if response.status_code == 200:
            data = response.json()

            # Extract track information
            title = data.get('title', 'Unknown Track')
            artist = data.get('artist', 'Unknown Artist')
            album = data.get('album', '')

            # Get album art from Radio Calico server
            album_art = 'https://d3d4yli4hf5bmh.cloudfront.net/cover.jpg'

            # Find or create song in database
            song = Song.query.filter_by(title=title, artist=artist).first()
            if not song:
                song = Song(title=title, artist=artist, album=album)
                db.session.add(song)
                db.session.commit()

            # Get rating stats
            song_data = song.to_dict()

            return jsonify({
                'song_id': song.id,
                'title': title,
                'artist': artist,
                'album': album,
                'albumArt': album_art,
                'live': True,
                'bit_depth': data.get('bit_depth'),
                'sample_rate': data.get('sample_rate'),
                'thumbs_up': song_data['thumbs_up'],
                'thumbs_down': song_data['thumbs_down']
            }), 200

        # Fallback if endpoint fails
        title = 'Radio Calico'
        artist = 'Live Stream'
        album = '24/7 Music'

        # Find or create fallback song
        song = Song.query.filter_by(title=title, artist=artist).first()
        if not song:
            song = Song(title=title, artist=artist, album=album)
            db.session.add(song)
            db.session.commit()

        song_data = song.to_dict()

        return jsonify({
            'song_id': song.id,
            'title': title,
            'artist': artist,
            'album': album,
            'albumArt': '/images/RadioCalicoLayout.png',
            'live': True,
            'thumbs_up': song_data['thumbs_up'],
            'thumbs_down': song_data['thumbs_down']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trackhistory', methods=['GET'])
def get_track_history():
    """Get recently played tracks from Radio Calico stream"""
    try:
        # Try to fetch track history from common streaming history endpoints
        history_urls = [
            'https://d3d4yli4hf5bmh.cloudfront.net/hls/history.json',
            'https://d3d4yli4hf5bmh.cloudfront.net/api/history',
            'https://radiocalico.com/api/trackhistory.json',
            'https://radiocalico.com/api/recent-tracks'
        ]

        tracks_data = None
        for url in history_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    # Normalize the response format
                    if isinstance(data, list):
                        tracks_data = data
                        break
                    elif 'tracks' in data:
                        tracks_data = data['tracks']
                        break
            except:
                continue

        # If no history endpoint works, use sample/default data
        if not tracks_data:
            tracks_data = [
                {
                    'title': 'He\'s A Dream (1983)',
                    'artist': 'Shandi Sinnamon',
                    'album': 'Flashdance (Original Motion Picture Soundtrack)',
                    'playedAt': '2024-11-04T18:30:00Z'
                },
                {
                    'title': 'Ain\'t 2 Proud 2 Beg',
                    'artist': 'TLC',
                    'album': 'Ooooooohhh... On the TLC Tip',
                    'playedAt': '2024-11-04T18:26:00Z'
                },
                {
                    'title': 'Steady, As She Goes',
                    'artist': 'The Raconteurs',
                    'album': 'Broken Boy Soldiers',
                    'playedAt': '2024-11-04T18:22:00Z'
                },
                {
                    'title': 'Just Another Night',
                    'artist': 'Mick Jagger',
                    'album': 'She\'s the Boss',
                    'playedAt': '2024-11-04T18:18:00Z'
                },
                {
                    'title': 'Irreplaceable (Album Version)',
                    'artist': 'Beyoncé',
                    'album': 'B\'Day',
                    'playedAt': '2024-11-04T18:14:00Z'
                }
            ]

        # Add song IDs and rating stats to each track
        enriched_tracks = []
        for track in tracks_data:
            title = track.get('title', 'Unknown Track')
            artist = track.get('artist', 'Unknown Artist')
            album = track.get('album', '')

            # Find or create song in database
            song = Song.query.filter_by(title=title, artist=artist).first()
            if not song:
                song = Song(title=title, artist=artist, album=album)
                db.session.add(song)
                db.session.commit()

            # Get rating stats
            song_data = song.to_dict()

            enriched_track = {
                'song_id': song.id,
                'title': title,
                'artist': artist,
                'album': album,
                'playedAt': track.get('playedAt'),
                'thumbs_up': song_data['thumbs_up'],
                'thumbs_down': song_data['thumbs_down']
            }
            enriched_tracks.append(enriched_track)

        return jsonify({'tracks': enriched_tracks}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User endpoints
@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify({'users': [user.to_dict() for user in users]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()

        if not data or not data.get('username') or not data.get('email'):
            return jsonify({'error': 'Username and email are required'}), 400

        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        new_user = User(
            username=data['username'],
            email=data['email']
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Post endpoints
@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get all posts"""
    try:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return jsonify({'posts': [post.to_dict() for post in posts]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get a specific post"""
    try:
        post = Post.query.get_or_404(post_id)
        return jsonify({'post': post.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/posts', methods=['POST'])
def create_post():
    """Create a new post"""
    try:
        data = request.get_json()

        if not data or not data.get('title') or not data.get('content') or not data.get('user_id'):
            return jsonify({'error': 'Title, content, and user_id are required'}), 400

        # Verify user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        new_post = Post(
            title=data['title'],
            content=data['content'],
            user_id=data['user_id']
        )

        db.session.add(new_post)
        db.session.commit()

        return jsonify({
            'message': 'Post created successfully',
            'post': new_post.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete a post"""
    try:
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Song rating endpoints
@app.route('/api/songs/<int:song_id>/rate', methods=['POST'])
def rate_song(song_id):
    """Rate a song with thumbs up or down, or update existing rating"""
    try:
        data = request.get_json()

        if not data or not data.get('user_identifier') or not data.get('rating_type'):
            return jsonify({'error': 'user_identifier and rating_type are required'}), 400

        if data['rating_type'] not in ['up', 'down']:
            return jsonify({'error': 'rating_type must be "up" or "down"'}), 400

        # Verify song exists
        song = Song.query.get(song_id)
        if not song:
            return jsonify({'error': 'Song not found'}), 404

        # Check if user already rated this song
        existing_rating = Rating.query.filter_by(
            song_id=song_id,
            user_identifier=data['user_identifier']
        ).first()

        if existing_rating:
            # User is changing their rating - update it
            if existing_rating.rating_type != data['rating_type']:
                existing_rating.rating_type = data['rating_type']
                existing_rating.created_at = datetime.utcnow()  # Update timestamp
                db.session.commit()

                return jsonify({
                    'message': 'Rating updated successfully',
                    'rating': existing_rating.to_dict(),
                    'song': song.to_dict(),
                    'updated': True
                }), 200
            else:
                # Same rating - no change needed
                return jsonify({
                    'message': 'Rating unchanged',
                    'rating': existing_rating.to_dict(),
                    'song': song.to_dict(),
                    'updated': False
                }), 200

        # Create new rating
        new_rating = Rating(
            song_id=song_id,
            user_identifier=data['user_identifier'],
            rating_type=data['rating_type']
        )

        db.session.add(new_rating)
        db.session.commit()

        return jsonify({
            'message': 'Rating submitted successfully',
            'rating': new_rating.to_dict(),
            'song': song.to_dict(),
            'updated': False
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/songs/<int:song_id>/ratings', methods=['GET'])
def get_song_ratings(song_id):
    """Get rating statistics for a song"""
    try:
        song = Song.query.get(song_id)
        if not song:
            return jsonify({'error': 'Song not found'}), 404

        return jsonify(song.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/songs/<int:song_id>/user-rating/<user_identifier>', methods=['GET'])
def get_user_rating(song_id, user_identifier):
    """Check if a user has already rated a song"""
    try:
        rating = Rating.query.filter_by(
            song_id=song_id,
            user_identifier=user_identifier
        ).first()

        if rating:
            return jsonify({
                'has_rated': True,
                'rating_type': rating.rating_type
            }), 200
        else:
            return jsonify({
                'has_rated': False
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/songs/find-or-create', methods=['POST'])
def find_or_create_song():
    """Find a song by title and artist, or create it if it doesn't exist"""
    try:
        data = request.get_json()

        if not data or not data.get('title') or not data.get('artist'):
            return jsonify({'error': 'title and artist are required'}), 400

        # Try to find existing song
        song = Song.query.filter_by(
            title=data['title'],
            artist=data['artist']
        ).first()

        if song:
            return jsonify({
                'song': song.to_dict(),
                'created': False
            }), 200

        # Create new song
        new_song = Song(
            title=data['title'],
            artist=data['artist'],
            album=data.get('album', '')
        )

        db.session.add(new_song)
        db.session.commit()

        return jsonify({
            'song': new_song.to_dict(),
            'created': True
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Database initialization commands
@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized!')

@app.cli.command()
def seed_db():
    """Seed the database with sample data."""
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Create sample users
    user1 = User(username='alice', email='alice@example.com')
    user2 = User(username='bob', email='bob@example.com')
    user3 = User(username='charlie', email='charlie@example.com')

    db.session.add_all([user1, user2, user3])
    db.session.commit()

    # Create sample posts
    post1 = Post(
        title='Welcome to the Blog',
        content='This is the first post on our blog! We are excited to share our thoughts and ideas with you.',
        user_id=user1.id
    )
    post2 = Post(
        title='Getting Started with Flask and Node.js',
        content='In this post, we explore how to build a modern web application with a Python backend and Node.js frontend.',
        user_id=user2.id
    )
    post3 = Post(
        title='The Future of Web Development',
        content='Web development is constantly evolving. Let\'s discuss the latest trends and technologies.',
        user_id=user3.id
    )

    db.session.add_all([post1, post2, post3])
    db.session.commit()

    print('Database seeded with sample data!')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
