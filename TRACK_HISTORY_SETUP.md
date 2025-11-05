# Track History Integration

## Overview

The Radio Calico website now displays recently played tracks automatically, fetching data from the streaming service and updating every 30 seconds.

## Backend API Endpoint

**Endpoint**: `GET /api/trackhistory`

The backend tries to fetch track history from potential streaming endpoints:
1. `https://d3d4yli4hf5bmh.cloudfront.net/hls/history.json`
2. `https://d3d4yli4hf5bmh.cloudfront.net/api/history`
3. `https://radiocalico.com/api/trackhistory.json`
4. `https://radiocalico.com/api/recent-tracks`

If none work, it returns sample data matching the style from the Radio Calico layout image.

## Response Format

The API expects JSON in this format:

```json
{
  "tracks": [
    {
      "title": "Song Title",
      "artist": "Artist Name",
      "album": "Album Name",
      "playedAt": "2024-11-04T18:30:00Z"
    }
  ]
}
```

Or as a simple array:

```json
[
  {
    "title": "Song Title",
    "artist": "Artist Name",
    "album": "Album Name",
    "playedAt": "2024-11-04T18:30:00Z"
  }
]
```

## Frontend Features

### Auto-Refresh
- Fetches track history when page loads
- Updates every 30 seconds
- Smooth UI updates without page reload

### Time Display
- Shows "X min ago" for tracks played in the last hour
- Shows time of day for older tracks
- Automatically updates as time passes

### Visual Design
- Each track has a teal left border accent
- Hover effect with shadow
- Artist name in teal color
- Album name in gray italic
- Timestamp on the right side

## Configuration

### Update the Actual Endpoint

Edit `backend/app.py` in the `/api/trackhistory` route:

```python
@app.route('/api/trackhistory', methods=['GET'])
def get_track_history():
    try:
        # Replace with actual Radio Calico history endpoint
        response = requests.get('https://actual-api-url.com/history', timeout=5)
        if response.status_code == 200:
            data = response.json()

            # Map the response to our format
            tracks = []
            for item in data:
                tracks.append({
                    'title': item.get('song_name'),
                    'artist': item.get('artist_name'),
                    'album': item.get('album_name'),
                    'playedAt': item.get('timestamp')
                })

            return jsonify({'tracks': tracks}), 200

        # Fallback
        return jsonify({'tracks': []}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Current Sample Data

The default sample data includes tracks from the Radio Calico layout image:
- Shandi Sinnamon - "He's A Dream (1983)"
- TLC - "Ain't 2 Proud 2 Beg"
- The Raconteurs - "Steady, As She Goes"
- Mick Jagger - "Just Another Night"
- Beyoncé - "Irreplaceable (Album Version)"

## Testing

### Test the API directly:

```bash
curl http://localhost:5000/api/trackhistory
```

### Check in browser:

1. Open http://localhost:3000
2. Scroll to "Previous Tracks" section
3. Open Developer Tools → Console
4. Look for fetch logs and any errors

## Customization

### Change refresh interval

Edit `frontend/views/index.ejs`:

```javascript
// Change from 30000ms (30 seconds) to desired interval
setInterval(updateTrackHistory, 60000); // 60 seconds
```

### Limit number of tracks displayed

Edit the backend response or add filtering in frontend:

```javascript
data.tracks.slice(0, 10).forEach(track => {
    // Only show first 10 tracks
});
```

### Add more track information

If your API provides additional data (genre, year, etc.):

```javascript
li.innerHTML = `
    <div class="track-details-row">
        <div>
            <strong>${track.title}</strong><br>
            <small>${track.artist}</small>
            ${track.album ? `<br><em>${track.album}</em>` : ''}
            ${track.year ? `<br><span class="track-year">${track.year}</span>` : ''}
        </div>
        ${timeInfo}
    </div>
`;
```

## Troubleshooting

### Tracks not showing
- Check browser console for errors
- Verify backend is running: `curl http://localhost:5000/api/trackhistory`
- Check CORS configuration

### Time display incorrect
- Verify `playedAt` timestamps are in ISO 8601 format
- Check browser timezone settings
- Ensure timestamps are in UTC

### Slow loading
- Reduce refresh interval
- Add caching on backend
- Limit number of tracks returned

## Integration with Actual Radio Calico Service

To integrate with the real Radio Calico metadata service:

1. **Find the track history API endpoint** - Contact the streaming provider or check their documentation
2. **Identify the response format** - Make a test request to see the JSON structure
3. **Update backend/app.py** - Add the actual endpoint URL and map the response fields
4. **Test** - Verify tracks display correctly
5. **Adjust refresh rate** - Based on how often tracks change

## Next Steps

- Add album art thumbnails to track history
- Implement "load more" for older tracks
- Add search/filter functionality
- Cache track history to reduce API calls
- Add click handlers to play previous tracks (if supported by stream)
