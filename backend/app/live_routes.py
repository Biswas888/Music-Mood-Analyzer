import os
import time
import requests
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

load_dotenv()

live_router = APIRouter(prefix="/live", tags=["Live"])

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Spotify credentials not set.")

# -----------------------
# Mood categories
# -----------------------
MOOD_GENRES = [
    "pop", "hip hop", "sad", "chill", "party", "workout", "lofi", "romantic"
]

# -----------------------
# Seeded fallback tracks for ML mode
# -----------------------
MOOD_TO_SONGS = {
    "pop": [
        {"id": "seed1", "name": "Blinding Lights", "artist": "The Weeknd",
         "valence": 0.7, "energy": 0.8, "danceability": 0.75,
         "spotify_url": "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b",
         "preview_url": None},
        {"id": "seed2", "name": "Levitating", "artist": "Dua Lipa",
         "valence": 0.9, "energy": 0.7, "danceability": 0.8,
         "spotify_url": "https://open.spotify.com/track/463CkQjx2Zk1yXoBuierM9",
         "preview_url": None},
    ],
    "sad": [
        {"id": "seed3", "name": "Someone Like You", "artist": "Adele",
         "valence": 0.1, "energy": 0.2, "danceability": 0.3,
         "spotify_url": "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB",
         "preview_url": None},
        {"id": "seed4", "name": "When I Was Your Man", "artist": "Bruno Mars",
         "valence": 0.2, "energy": 0.25, "danceability": 0.35,
         "spotify_url": "https://open.spotify.com/track/7pKfPomDEeI4TPT6EOYjn9",
         "preview_url": None},
    ],
    "chill": [
        {"id": "seed5", "name": "Sunflower", "artist": "Post Malone",
         "valence": 0.6, "energy": 0.4, "danceability": 0.65,
         "spotify_url": "https://open.spotify.com/track/3KkXRkHbMCARz0aVfEt68P",
         "preview_url": None}
    ],
    # Add more moods as needed
}

# -----------------------
# Spotify Token Cache
# -----------------------
SPOTIFY_TOKEN = None
TOKEN_EXPIRES = 0

def get_spotify_token():
    global SPOTIFY_TOKEN, TOKEN_EXPIRES
    if SPOTIFY_TOKEN and time.time() < TOKEN_EXPIRES:
        return SPOTIFY_TOKEN

    url = "https://accounts.spotify.com/api/token"
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Spotify authentication failed")

    data = response.json()
    SPOTIFY_TOKEN = data["access_token"]
    TOKEN_EXPIRES = time.time() + data["expires_in"]
    return SPOTIFY_TOKEN

# -----------------------
# Fetch tracks from playlist
# -----------------------
def fetch_tracks_from_playlist(playlist_id):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return []

    data = res.json() or {}
    items = data.get("items", [])
    tracks = []
    for item in items:
        track = item.get("track")
        if track and track.get("id"):
            tracks.append(track)
    return tracks

# -----------------------
# Fetch batch audio features
# -----------------------
def get_audio_features_batch(track_ids):
    if not track_ids:
        return {}

    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/audio-features?ids={','.join(track_ids)}"

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return {}

    data = res.json() or {}
    features = data.get("audio_features", [])
    return {f["id"]: f for f in features if f}

# -----------------------
# Search tracks directly (fallback)
# -----------------------
def search_tracks_for_mood(mood, limit=10):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.spotify.com/v1/search"
    params = {"q": mood, "type": "track", "limit": limit}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        return []
    data = res.json()
    return data.get("tracks", {}).get("items", [])

# -----------------------
# Categories endpoint
# -----------------------
@live_router.get("/categories")
def get_categories():
    return MOOD_GENRES

# -----------------------
# Songs by mood endpoint (robust + ML-ready)
# -----------------------
@live_router.get("/songs_by_mood")
def songs_by_mood(mood: str):
    if mood not in MOOD_GENRES:
        raise HTTPException(status_code=404, detail="Mood not found")

    # Map mood to Spotify category IDs
    MOOD_TO_CATEGORY = {
        "pop": "pop",
        "hip hop": "hiphop",
        "sad": "mellow",
        "chill": "chill",
        "party": "party",
        "workout": "workout",
        "lofi": "lofi",
        "romantic": "romance"
    }

    category_id = MOOD_TO_CATEGORY.get(mood)

    # Fetch playlists from category
    playlists = []
    if category_id:
        token = get_spotify_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.spotify.com/v1/browse/categories/{category_id}/playlists"
        params = {"limit": 5}
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json()
            playlists = data.get("playlists", {}).get("items", [])

    # Fetch tracks from playlists
    all_tracks = []
    for pl in playlists:
        playlist_id = pl.get("id")
        if playlist_id:
            tracks = fetch_tracks_from_playlist(playlist_id)
            if tracks:
                all_tracks.extend(tracks)

    # Fallback to search if no playlists found
    if not all_tracks:
        all_tracks = search_tracks_for_mood(mood)

    # Fallback to seeded ML tracks
    if not all_tracks:
        all_tracks = MOOD_TO_SONGS.get(mood, [])

    if not all_tracks:
        return []

    # Fetch audio features for ML
    track_ids = [t["id"] for t in all_tracks if t.get("id")]
    audio_features = get_audio_features_batch(track_ids)

    # Prepare ML-ready songs
    songs = []
    for t in all_tracks:
        tid = t.get("id")
        f = audio_features.get(tid, {})
        artists = t.get("artists") or [{"name": t.get("artist", "Unknown")}]
        songs.append({
            "id": tid,
            "name": t.get("name"),
            "artist": artists[0]["name"],
            "spotify_url": t.get("external_urls", {}).get("spotify") or t.get("spotify_url"),
            "preview_url": t.get("preview_url"),
            "danceability": f.get("danceability"),
            "energy": f.get("energy"),
            "valence": f.get("valence"),
            "acousticness": f.get("acousticness"),
            "instrumentalness": f.get("instrumentalness"),
            "liveness": f.get("liveness"),
            "loudness": f.get("loudness"),
            "speechiness": f.get("speechiness"),
            "tempo": f.get("tempo"),
            "key": f.get("key"),
            "mode": f.get("mode"),
            "time_signature": f.get("time_signature"),
            "duration_ms": t.get("duration_ms"),
            "popularity": t.get("popularity"),
            "explicit": t.get("explicit")
        })

    # Deduplicate & limit top 10
    unique_songs = {s["id"]: s for s in songs}
    songs = list(unique_songs.values())[:10]

    # Cache for next request
    MOOD_TO_SONGS[mood] = songs

    return songs

# -----------------------
# Search endpoint
# -----------------------
@live_router.get("/search")
def search_song(song_name: str):
    if len(song_name) < 2:
        return []

    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.spotify.com/v1/search"
    params = {"q": song_name, "type": "track", "limit": 10}

    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        return []

    data = res.json() or {}
    items = data.get("tracks", {}).get("items", [])

    results = []
    for track in items:
        artists = track.get("artists") or []
        artist_name = artists[0]["name"] if artists else "Unknown"
        results.append({
            "id": track.get("id"),
            "name": track.get("name"),
            "artist": artist_name,
            "spotify_url": track.get("external_urls", {}).get("spotify"),
            "preview_url": track.get("preview_url")
        })

    return results
