from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymysql
import os

app = FastAPI()


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB connection
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "mysql_db"),
        user=os.getenv("MYSQL_USER", "music_user"),
        password=os.getenv("MYSQL_PASSWORD", "music_pass"),
        database=os.getenv("MYSQL_DATABASE", "music_mood"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

# Pydantic model
class SongCreate(BaseModel):
    valence: float
    year: int
    acousticness: float
    artists: str
    danceability: float
    duration_ms: int
    energy: float
    explicit: int
    id: str
    instrumentalness: float
    key: int
    liveness: float
    loudness: float
    mode: int
    name: str
    popularity: int
    release_date: str
    speechiness: float
    tempo: float

# -------------------
# Mood calculation
# -------------------
def calculate_mood(valence, energy, acousticness, tempo):
    if valence > 0.6 and energy > 0.6:
        return "Happy"
    elif valence < 0.4 and energy < 0.4:
        return "Sad"
    elif energy > 0.7 and tempo > 120:
        return "Energetic"
    elif acousticness > 0.6 and energy < 0.5:
        return "Calm"
    else:
        return "Neutral"

# -------------------
# POST: Add song
# -------------------
@app.post("/api/songs")
def add_song(song: SongCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    mood = calculate_mood(song.valence, song.energy, song.acousticness, song.tempo)

    sql = """
    INSERT INTO songs (
        valence, year, acousticness, artists, danceability, duration_ms,
        energy, explicit, id, instrumentalness, `key`, liveness,
        loudness, mode, name, popularity, release_date,
        speechiness, tempo, mood
    ) VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s
    )
    """

    values = (
        song.valence, song.year, song.acousticness, song.artists, song.danceability,
        song.duration_ms, song.energy, song.explicit, song.id, song.instrumentalness,
        song.key, song.liveness, song.loudness, song.mode, song.name,
        song.popularity, song.release_date, song.speechiness, song.tempo, mood
    )

    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": f"Song '{song.name}' added successfully with mood '{mood}' 🎵"}

# -------------------
# GET: Search/filter songs
# -------------------
@app.get("/api/songs")
def get_songs(mood: str = None, year: int = None, search: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT name, artists, mood, energy, tempo, year FROM songs WHERE 1=1"
    params = []

    if mood:
        query += " AND mood = %s"
        params.append(mood)
    if year:
        query += " AND year = %s"
        params.append(year)
    if search:
        query += " AND (name LIKE %s OR artists LIKE %s)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# -------------------
# GET: All moods
# -------------------
@app.get("/api/moods")
def get_moods():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT mood, COUNT(*) AS count FROM songs GROUP BY mood")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
