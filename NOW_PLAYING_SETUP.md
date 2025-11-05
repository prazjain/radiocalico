# Now Playing Integration Setup

## Overview

The Radio Calico website now includes automatic "Now Playing" metadata fetching that updates the track information and album art in real-time.

## How It Works

### Backend API Endpoint

**Endpoint**: `GET /api/nowplaying`

The backend tries to fetch metadata from potential streaming metadata endpoints:
1. `https://d3d4yli4hf5bmh.cloudfront.net/hls/metadata.json`
2. `https://d3d4yli4hf5bmh.cloudfront.net/api/nowplaying`
3. `https://radiocalico.com/api/nowplaying.json`

If none of these work, it returns default placeholders.

### Frontend Polling

The frontend automatically:
- Fetches now playing data when the page loads
- Polls the backend API every 10 seconds for updates
- Updates the UI with smooth transitions when track changes

## Response Format

The API expects JSON in this format:

```json
{
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "albumArt": "https://example.com/album-art.jpg",
  "live": true
}
```

## Configuring the Actual Metadata Source

To configure the real Radio Calico metadata endpoint:

1. **Find the metadata endpoint** - Check with the streaming service provider
2. **Update backend/app.py** - Modify the `metadata_urls` list in the `/api/nowplaying` route
3. **Adjust response parsing** - Update the data extraction based on the actual API response format

### Example Configuration

If Radio Calico provides metadata at `https://api.radiocalico.com/current-track`:

```python
@app.route('/api/nowplaying', methods=['GET'])
def get_now_playing():
    try:
        response = requests.get('https://api.radiocalico.com/current-track', timeout=5)
        if response.status_code == 200:
            data = response.json()

            # Map the actual API response to our format
            return jsonify({
                'title': data.get('track_name'),
                'artist': data.get('artist_name'),
                'album': data.get('album_name'),
                'albumArt': data.get('artwork_url'),
                'live': True
            }), 200

        # Fallback
        return jsonify({
            'title': 'Radio Calico',
            'artist': 'Live Stream',
            'album': '24/7 Music',
            'albumArt': '/images/RadioCalicoLayout.png',
            'live': True
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Features

### Smooth Album Art Transitions
- Fade out/fade in effect when album art changes
- Prevents jarring visual updates
- Fallback to logo if image fails to load

### Error Handling
- Gracefully handles API failures
- Continues showing last known data if fetch fails
- Logs errors to browser console for debugging

### Performance
- 10-second polling interval balances freshness with server load
- Timeout on metadata requests prevents hanging
- Client-side caching prevents unnecessary updates

## Testing

### Test the API endpoint directly:

```bash
curl http://localhost:5000/api/nowplaying
```

### Check browser console:
Open Developer Tools and look for:
- "Now Playing:" logs showing successful updates
- Error messages if metadata fetch fails

## Customization

### Change polling interval

Edit `frontend/views/index.ejs`:
```javascript
// Change from 10000ms (10 seconds) to desired interval
setInterval(updateNowPlaying, 5000); // 5 seconds
```

### Add more metadata fields

1. Update the backend response
2. Add HTML elements for the new data
3. Update the frontend JavaScript to populate them

Example - adding genre:

```html
<p class="track-genre" id="trackGenre">Genre</p>
```

```javascript
if (data.genre) {
    document.getElementById('trackGenre').textContent = data.genre;
}
```

## Troubleshooting

### Album art not updating
- Check browser console for CORS errors
- Verify album art URL is accessible
- Check network tab in Developer Tools

### Metadata not refreshing
- Verify backend server is running
- Check backend API endpoint returns valid JSON
- Verify frontend polling is active (check console logs)

### CORS Issues
If fetching from external metadata source, ensure CORS is properly configured in the backend.

## Next Steps

1. **Identify actual metadata endpoint** from Radio Calico streaming service
2. **Update backend configuration** with the real endpoint
3. **Test with live data** to ensure format matches
4. **Add caching** if needed to reduce API calls
5. **Consider WebSocket** for real-time updates instead of polling
