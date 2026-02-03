from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB connection ---
def get_db_connection():
    return mysql.connector.connect(
        host="mysql_db",
        user="music_user",
        password="music_pass",
        database="music_mood"
    )

@app.get("/")
def root():
    return {"status": "API is running"}

@app.get("/songs/sample")
def get_sample_songs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, artists, release_date FROM songs LIMIT 5")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# 🔥 ADD THESE
@app.get("/api/moods")
def get_mood_counts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT mood, COUNT(*) AS count
        FROM songs
        GROUP BY mood
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/api/songs")
def get_songs(mood: str = None, year: int = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT name, artists, mood, energy, tempo, year FROM songs WHERE 1=1"
    params = []

    if mood:
        query += " AND mood = %s"
        params.append(mood)
    if year:
        query += " AND year = %s"
        params.append(year)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows
