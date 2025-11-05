#!/usr/bin/env python3
"""
Test script to verify Radio Calico metadata endpoint

Usage:
    python test_metadata.py <endpoint_url>

Example:
    python test_metadata.py https://radiocalico.com/api/nowplaying
"""

import sys
import requests
import json

def test_endpoint(url):
    """Test a metadata endpoint and display the response"""
    print(f"\n{'='*60}")
    print(f"Testing endpoint: {url}")
    print(f"{'='*60}\n")

    try:
        response = requests.get(url, timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"\n{'='*60}")
        print("Response:")
        print(f"{'='*60}\n")

        if response.status_code == 200:
            try:
                data = response.json()
                print(json.dumps(data, indent=2))

                print(f"\n{'='*60}")
                print("Analysis:")
                print(f"{'='*60}\n")

                # Try to identify track information
                def find_keys(obj, keys_to_find, path=""):
                    """Recursively find keys in nested dict"""
                    results = []
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            current_path = f"{path}.{key}" if path else key
                            if any(search_key.lower() in key.lower() for search_key in keys_to_find):
                                results.append((current_path, value))
                            if isinstance(value, (dict, list)):
                                results.extend(find_keys(value, keys_to_find, current_path))
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            results.extend(find_keys(item, keys_to_find, f"{path}[{i}]"))
                    return results

                # Look for common metadata fields
                track_info = {
                    'title': find_keys(data, ['title', 'song', 'track']),
                    'artist': find_keys(data, ['artist', 'performer']),
                    'album': find_keys(data, ['album']),
                    'art': find_keys(data, ['art', 'artwork', 'cover', 'image', 'img'])
                }

                for field, matches in track_info.items():
                    if matches:
                        print(f"\nFound {field.upper()}:")
                        for path, value in matches:
                            print(f"  {path}: {value}")

                if not any(track_info.values()):
                    print("⚠️  No obvious track metadata fields found.")
                    print("    Manual inspection of the response needed.")
                else:
                    print(f"\n{'='*60}")
                    print("✅ This looks like a valid metadata endpoint!")
                    print(f"{'='*60}")

            except json.JSONDecodeError:
                print("⚠️  Response is not valid JSON:")
                print(response.text[:500])
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(response.text[:500])

    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to endpoint")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_metadata.py <endpoint_url>")
        print("\nExample:")
        print("  python test_metadata.py https://radiocalico.com/api/nowplaying")
        sys.exit(1)

    endpoint_url = sys.argv[1]
    test_endpoint(endpoint_url)
