# Spotify Language Playlist Organizer

Automatically sorts your Spotify playlist into language-based playlists by detecting the language of each song’s lyrics using the Genius API and language detection.

## Features
- Fetches songs from a specified Spotify playlist
- Retrieves lyrics via Genius API
- Detects language of the lyrics or song title and artist name
- Creates or updates language-specific playlists on Spotify
- Optionally deletes old language playlists before sorting

## Requirements
- Python 3.6+
- Spotipy
- Requests
- BeautifulSoup4
- langdetect

## Setup

1. Clone the repo or download the script.
2. Install required packages:
   ```pip install spotipy requests beautifulsoup4 langdetect  ```  
3. Register your app on [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and get CLIENT_ID, CLIENT_SECRET.
4. Register your app on [Genius API](https://genius.com/api-clients) and get the API token.
5. Set your Spotify username, redirect URI, and API keys in the script.

## Usage

Run the script:
   ```python spotify.py```

Follow the prompts to delete old language playlists if desired. The script will process your playlist and organize songs by language.

---

Made with ❤️ by Samil 
