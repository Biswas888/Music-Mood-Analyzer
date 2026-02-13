import pandas as pd
import mysql.connector
import ast

# --- CSV path inside container ---
CSV_FILE = "/app/app/data/data.csv"

# --- Load CSV ---
df = pd.read_csv(CSV_FILE)
print(f"✅ Loaded {len(df)} rows")

# --- Fill missing values ---
df.fillna({
    "valence": 0.0,
    "year": 0,
    "acousticness": 0.0,
    "artists": "Unknown",
    "danceability": 0.0,
    "duration_ms": 0,
    "energy": 0.0,
    "explicit": 0,
    "id": "unknown_id",
    "instrumentalness": 0.0,
    "key": 0,
    "liveness": 0.0,
    "loudness": 0.0,
    "mode": 0,
    "name": "Unknown",
    "popularity": 0,
    "release_date": "1900-01-01",
    "speechiness": 0.0,
    "tempo": 0.0
}, inplace=True)

# --- Clean artists column ---
def clean_artists(val):
    try:
        if isinstance(val, str) and val.startswith("["):
            return ", ".join(ast.literal_eval(val))
        return str(val)
    except:
        return str(val)

df["artists"] = df["artists"].apply(clean_artists)

# --- Fix release_date ---
df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
df["release_date"] = df["release_date"].fillna(pd.Timestamp("1900-01-01"))
df["release_date"] = df["release_date"].dt.strftime("%Y-%m-%d")
df["release_date"] = df["release_date"].astype(str).str.strip()

# --- Remove duplicate IDs before inserting ---
df = df.drop_duplicates(subset=["id"])
print(f"✅ {len(df)} rows after removing duplicates")

# --- Add Mood column before inserting ---
def get_mood(row):
    if row['valence'] > 0.6 and row['energy'] > 0.6:
        return 'Happy'
    elif row['valence'] < 0.4 and row['energy'] < 0.4:
        return 'Sad'
    elif row['energy'] > 0.7 and row['tempo'] > 120:
        return 'Energetic'
    elif row['acousticness'] > 0.6 and row['energy'] < 0.5:
        return 'Calm'
    else:
        return 'Neutral'

df['mood'] = df.apply(get_mood, axis=1)

# --- Connect to MySQL ---
conn = mysql.connector.connect(
    host="db",
    port=3306,
    user="music_user",
    password="music_pass",
    database="music_mood"
)
cursor = conn.cursor()
print("✅ Connected to MySQL!")

# --- Insert query (skip duplicates in DB) ---
insert_sql = """
INSERT IGNORE INTO songs (
    valence, year, acousticness, artists, danceability, duration_ms, energy,
    explicit, id, instrumentalness, `key`, liveness, loudness, mode, name,
    popularity, release_date, speechiness, tempo, mood
) VALUES (
    %(valence)s, %(year)s, %(acousticness)s, %(artists)s, %(danceability)s,
    %(duration_ms)s, %(energy)s, %(explicit)s, %(id)s, %(instrumentalness)s,
    %(key)s, %(liveness)s, %(loudness)s, %(mode)s, %(name)s, %(popularity)s,
    %(release_date)s, %(speechiness)s, %(tempo)s, %(mood)s
)
"""

# --- Bulk insert for speed ---
cursor.executemany(insert_sql, df.to_dict(orient="records"))
conn.commit()
print(f"✅ Inserted {len(df)} rows (duplicates skipped automatically)")

cursor.close()
conn.close()
print("🎉 Done inserting all rows!")

# --- Optional: save CSV with mood ---
CSV_EXPORT = "/app/app/data/song_moods.csv"
df.to_csv(CSV_EXPORT, index=False)
print(f"✅ CSV ready: {CSV_EXPORT}")
