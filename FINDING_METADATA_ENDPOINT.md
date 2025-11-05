# Finding the Radio Calico Metadata Endpoint

## Problem

The "Now Playing" album art and track information are not updating because we need to find the actual Radio Calico metadata API endpoint.

## How to Find the Metadata Endpoint

### Method 1: Using Browser Developer Tools (Easiest)

1. **Visit the Radio Calico website** where you see the now playing information
2. **Open Developer Tools**:
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Firefox: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Safari: Enable Developer Menu first, then press `Cmd+Option+I`

3. **Go to the Network tab**
4. **Filter by XHR/Fetch requests**
5. **Look for API calls** that contain:
   - "now playing"
   - "current track"
   - "metadata"
   - "track info"
   - JSON responses with track/artist/album data

6. **Click on the request** and examine:
   - Request URL (this is what we need!)
   - Response format (to understand the data structure)

### Method 2: Check the Radio Calico Website Source

1. Visit the Radio Calico streaming page
2. Right-click → "View Page Source"
3. Search for keywords:
   - `fetch(`
   - `XMLHttpRequest`
   - `api/`
   - `metadata`
   - `nowplaying`

### Method 3: Contact Radio Calico

If you can't find the endpoint:
- Check if Radio Calico has developer documentation
- Contact their support and ask for the metadata API endpoint
- Ask in their community forums or Discord

## Common Endpoint Patterns

Radio streaming services often use these patterns:

```
https://radiocalico.com/api/nowplaying
https://radiocalico.com/api/current-track
https://radiocalico.com/api/metadata
https://api.radiocalico.com/nowplaying
https://stream.radiocalico.com/metadata.json
https://[cloudfront-domain]/api/metadata
```

## What to Look For in the Response

The metadata should include:
- Track title
- Artist name
- Album name
- Album art URL
- Timestamp (when the track started)

Example response format:
```json
{
  "now_playing": {
    "song": {
      "title": "Song Title",
      "artist": "Artist Name",
      "album": "Album Name",
      "art": "https://example.com/album-art.jpg"
    }
  }
}
```

## Once You Find the Endpoint

1. **Test it with curl**:
   ```bash
   curl https://found-endpoint-url.com/api/nowplaying
   ```

2. **Copy the URL and response format**

3. **Update the backend** - I can help you configure it once you provide:
   - The endpoint URL
   - An example of the JSON response

## Temporary Solution

For now, the site is using placeholder data. To make it more dynamic, we can:

1. Use the Radio Calico website directly as a source
2. Scrape the information (if no API is available)
3. Use a third-party service that tracks Radio Calico's stream

Let me know what you find, and I'll help integrate it!
