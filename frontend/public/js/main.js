// Radio Calico - Main JavaScript
// Handles audio playback, metadata fetching, and song ratings

// DOM Elements
const audio = document.getElementById('radioStream');
const playButton = document.getElementById('playButton');
const playIcon = document.getElementById('playIcon');
const volumeSlider = document.getElementById('volumeSlider');

// State
let isPlaying = false;
let currentSongData = {
    song_id: null,
    thumbs_up: 0,
    thumbs_down: 0
};

// ============================================================================
// Audio Player Functions
// ============================================================================

/**
 * Toggle play/pause for the audio stream
 */
function togglePlay() {
    if (isPlaying) {
        audio.pause();
        playIcon.textContent = '▶';
        isPlaying = false;
    } else {
        audio.play().then(() => {
            playIcon.textContent = '⏸';
            isPlaying = true;
        }).catch(error => {
            console.error('Playback failed:', error);
            alert('Unable to play stream. Please try again.');
        });
    }
}

/**
 * Set audio volume
 * @param {number} value - Volume level (0-100)
 */
function setVolume(value) {
    audio.volume = value / 100;
}

// ============================================================================
// User Identification
// ============================================================================

/**
 * Generate or retrieve anonymous user ID from localStorage
 * @returns {string} User identifier
 */
function getUserIdentifier() {
    let userId = localStorage.getItem('radiocalico_user_id');
    if (!userId) {
        // Generate a unique ID
        userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('radiocalico_user_id', userId);
    }
    return userId;
}

// ============================================================================
// Now Playing Functions
// ============================================================================

/**
 * Fetch and update the now playing information
 */
async function updateNowPlaying() {
    try {
        const response = await fetch('http://localhost:5000/api/nowplaying');
        if (response.ok) {
            const data = await response.json();

            // Store song data globally
            currentSongData = {
                song_id: data.song_id,
                thumbs_up: data.thumbs_up || 0,
                thumbs_down: data.thumbs_down || 0
            };

            // Update track information
            if (data.title) {
                document.getElementById('trackTitle').textContent = data.title;
            }
            if (data.artist) {
                document.getElementById('artistName').textContent = data.artist;
            }
            if (data.album) {
                document.getElementById('albumName').textContent = data.album;
            }

            // Update rating counts
            document.getElementById('nowPlayingUpCount').textContent = data.thumbs_up || 0;
            document.getElementById('nowPlayingDownCount').textContent = data.thumbs_down || 0;

            // Check if user has already rated this song
            if (data.song_id) {
                checkUserRating(data.song_id, 'now-playing');
            }

            // Update album art with smooth transition
            if (data.albumArt) {
                const albumArtImg = document.getElementById('albumArt');
                const newSrc = data.albumArt.startsWith('http') ?
                    data.albumArt :
                    data.albumArt;

                if (albumArtImg.src !== newSrc) {
                    albumArtImg.style.opacity = '0.5';
                    setTimeout(() => {
                        albumArtImg.src = newSrc;
                        albumArtImg.onload = () => {
                            albumArtImg.style.opacity = '1';
                        };
                    }, 300);
                }
            }
        }
    } catch (error) {
        console.error('Error fetching now playing data:', error);
    }
}

// ============================================================================
// Track History Functions
// ============================================================================

/**
 * Fetch and update the track history
 */
async function updateTrackHistory() {
    try {
        const response = await fetch('http://localhost:5000/api/trackhistory');
        if (response.ok) {
            const data = await response.json();

            const trackHistoryList = document.getElementById('trackHistory');

            if (data.tracks && data.tracks.length > 0) {
                trackHistoryList.innerHTML = '';

                data.tracks.forEach((track, index) => {
                    const li = document.createElement('li');
                    li.className = 'track-item';
                    li.dataset.songId = track.song_id;

                    // Format the time if available
                    let timeInfo = '';
                    if (track.playedAt) {
                        const playedDate = new Date(track.playedAt);
                        const now = new Date();
                        const diffMinutes = Math.floor((now - playedDate) / 60000);

                        if (diffMinutes < 60) {
                            timeInfo = `<span class="track-time">${diffMinutes} min ago</span>`;
                        } else {
                            timeInfo = `<span class="track-time">${playedDate.toLocaleTimeString()}</span>`;
                        }
                    }

                    li.innerHTML = `
                        <div class="track-details-row">
                            <div>
                                <strong>${track.title || track.artist || 'Unknown Track'}</strong><br>
                                <small>${track.artist || ''}</small>
                                ${track.album ? `<br><em style="color: #666;">${track.album}</em>` : ''}
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <div class="song-rating" style="margin: 0;">
                                    <button class="rating-btn thumbs-up" onclick="rateSong('history-${index}', 'up')" title="Thumbs up">
                                        👍 <span id="historyUpCount-${index}">${track.thumbs_up || 0}</span>
                                    </button>
                                    <button class="rating-btn thumbs-down" onclick="rateSong('history-${index}', 'down')" title="Thumbs down">
                                        👎 <span id="historyDownCount-${index}">${track.thumbs_down || 0}</span>
                                    </button>
                                </div>
                                ${timeInfo}
                            </div>
                        </div>
                    `;

                    trackHistoryList.appendChild(li);

                    // Check if user has rated this song
                    if (track.song_id) {
                        checkUserRating(track.song_id, `history-${index}`);
                    }
                });
            } else {
                trackHistoryList.innerHTML = '<li class="track-item">No track history available</li>';
            }
        }
    } catch (error) {
        console.error('Error fetching track history:', error);
        const trackHistoryList = document.getElementById('trackHistory');
        trackHistoryList.innerHTML = '<li class="track-item">Unable to load track history</li>';
    }
}

// ============================================================================
// Rating Functions
// ============================================================================

/**
 * Check if user has already rated a song and highlight the button
 * @param {number} songId - The song ID
 * @param {string} context - The context ('now-playing' or 'history-{index}')
 */
async function checkUserRating(songId, context) {
    const userId = getUserIdentifier();
    try {
        const response = await fetch(`http://localhost:5000/api/songs/${songId}/user-rating/${userId}`);
        if (response.ok) {
            const data = await response.json();
            if (data.has_rated) {
                // Highlight the button they chose (both buttons remain enabled for editing)
                if (context === 'now-playing') {
                    const upBtn = document.getElementById('nowPlayingThumbsUp');
                    const downBtn = document.getElementById('nowPlayingThumbsDown');
                    upBtn.classList.remove('rated');
                    downBtn.classList.remove('rated');
                    if (data.rating_type === 'up') {
                        upBtn.classList.add('rated');
                    } else {
                        downBtn.classList.add('rated');
                    }
                } else if (context.startsWith('history-')) {
                    const index = context.split('-')[1];
                    const trackItem = document.querySelector(`[data-song-id="${songId}"]`);
                    if (trackItem) {
                        const buttons = trackItem.querySelectorAll('.rating-btn');
                        buttons[0].classList.remove('rated');
                        buttons[1].classList.remove('rated');
                        if (data.rating_type === 'up') {
                            buttons[0].classList.add('rated');
                        } else {
                            buttons[1].classList.add('rated');
                        }
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error checking user rating:', error);
    }
}

/**
 * Rate a song with thumbs up or down
 * @param {string} context - The context ('now-playing' or 'history-{index}')
 * @param {string} ratingType - The rating type ('up' or 'down')
 */
async function rateSong(context, ratingType) {
    let songId;

    // Get song ID based on context
    if (context === 'now-playing') {
        songId = currentSongData.song_id;
    } else if (context.startsWith('history-')) {
        const index = context.split('-')[1];
        const trackItem = document.querySelectorAll('.track-item')[index];
        songId = trackItem ? trackItem.dataset.songId : null;
    }

    if (!songId) {
        alert('Unable to rate song. Please try again.');
        return;
    }

    const userId = getUserIdentifier();

    try {
        const response = await fetch(`http://localhost:5000/api/songs/${songId}/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_identifier: userId,
                rating_type: ratingType
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Update the rating counts
            if (context === 'now-playing') {
                document.getElementById('nowPlayingUpCount').textContent = data.song.thumbs_up;
                document.getElementById('nowPlayingDownCount').textContent = data.song.thumbs_down;

                // Remove rated class from both buttons and add to selected one
                const upBtn = document.getElementById('nowPlayingThumbsUp');
                const downBtn = document.getElementById('nowPlayingThumbsDown');
                upBtn.classList.remove('rated');
                downBtn.classList.remove('rated');

                if (ratingType === 'up') {
                    upBtn.classList.add('rated');
                } else {
                    downBtn.classList.add('rated');
                }
            } else if (context.startsWith('history-')) {
                const index = context.split('-')[1];
                document.getElementById(`historyUpCount-${index}`).textContent = data.song.thumbs_up;
                document.getElementById(`historyDownCount-${index}`).textContent = data.song.thumbs_down;

                // Remove rated class from both buttons and add to selected one
                const trackItem = document.querySelectorAll('.track-item')[index];
                const buttons = trackItem.querySelectorAll('.rating-btn');
                buttons[0].classList.remove('rated');
                buttons[1].classList.remove('rated');

                if (ratingType === 'up') {
                    buttons[0].classList.add('rated');
                } else {
                    buttons[1].classList.add('rated');
                }
            }

            // Show success message
            if (data.updated) {
                console.log('Rating updated successfully!');
            } else {
                console.log('Rating submitted successfully!');
            }
        } else {
            // Error occurred
            alert(data.error || 'Unable to submit rating');
        }
    } catch (error) {
        console.error('Error submitting rating:', error);
        alert('Unable to submit rating. Please try again.');
    }
}

// ============================================================================
// Initialization
// ============================================================================

/**
 * Initialize the application when DOM is ready
 */
function initializeApp() {
    // Initialize HLS.js for streaming
    if (Hls.isSupported()) {
        const hls = new Hls({
            enableWorker: true,
            lowLatencyMode: true,
            backBufferLength: 90
        });

        hls.loadSource('https://d3d4yli4hf5bmh.cloudfront.net/hls/live.m3u8');
        hls.attachMedia(audio);

        hls.on(Hls.Events.MANIFEST_PARSED, function() {
            console.log('HLS stream ready');
        });

        hls.on(Hls.Events.ERROR, function(event, data) {
            console.error('HLS error:', data);
            if (data.fatal) {
                switch(data.type) {
                    case Hls.ErrorTypes.NETWORK_ERROR:
                        console.log('Network error, trying to recover...');
                        hls.startLoad();
                        break;
                    case Hls.ErrorTypes.MEDIA_ERROR:
                        console.log('Media error, trying to recover...');
                        hls.recoverMediaError();
                        break;
                    default:
                        console.log('Fatal error, cannot recover');
                        break;
                }
            }
        });
    } else if (audio.canPlayType('application/vnd.apple.mpegurl')) {
        // Native HLS support (Safari)
        audio.src = 'https://d3d4yli4hf5bmh.cloudfront.net/hls/live.m3u8';
    }

    // Set initial volume
    audio.volume = 0.7;

    // Volume slider event listener
    volumeSlider.addEventListener('input', function() {
        setVolume(this.value);
    });

    // Handle audio errors
    audio.addEventListener('error', function(e) {
        console.error('Audio error:', e);
        playIcon.textContent = '▶';
        isPlaying = false;
    });

    // Start fetching metadata
    updateNowPlaying();
    setInterval(updateNowPlaying, 10000);  // Every 10 seconds

    updateTrackHistory();
    setInterval(updateTrackHistory, 30000);  // Every 30 seconds
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
