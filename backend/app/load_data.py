import pandas as pd
import mysql.connector
import ast

# -----------------------
# CONFIG
# -----------------------
CSV_FILE = "/app/app/data/data.csv"  # adjust if needed inside container

DB_CONFIG = {
    "host": "db",        # Docker service name
    "port": 3306,
    "user": "music_user",
    "password": "music_pass",
    "database": "music_mood"
}

# -----------------------
# LOAD CSV
# -----------------------
df = pd.read_csv(CSV_FILE)
print(f"✅ Loaded {len(df)} rows")

# -----------------------
# CLEAN DATA
# -----------------------
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

def clean_artists(val):
    try:
        if isinstance(val, str) and val.startswith("["):
            return ", ".join(ast.literal_eval(val))
        return str(val)
    except:
        return str(val)

df["artists"] = df["artists"].apply(clean_artists)

# -----------------------
# FIX DATES
# -----------------------
df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
df["release_date"] = df["release_date"].fillna(pd.Timestamp("1900-01-01"))
df["release_date"] = df["release_date"].dt.strftime("%Y-%m-%d")

# -----------------------
# REMOVE DUPLICATES
# -----------------------
df = df.drop_duplicates(subset=["id"])
print(f"✅ {len(df)} rows after dedupe")

# -----------------------
# MOOD CLASSIFICATION
# -----------------------
def get_mood(row):
    if row["valence"] > 0.6 and row["energy"] > 0.6:
        return "Happy"
    elif row["valence"] < 0.4 and row["energy"] < 0.4:
        return "Sad"
    elif row["energy"] > 0.7 and row["tempo"] > 120:
        return "Energetic"
    elif row["acousticness"] > 0.6 and row["energy"] < 0.5:
        return "Calm"
    else:
        return "Neutral"

df["mood"] = df.apply(get_mood, axis=1)

# -----------------------
# CONNECT TO MYSQL
# -----------------------
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()
print("✅ Connected to MySQL")

# -----------------------
# INSERT DATA
# -----------------------
insert_sql = """
INSERT IGNORE INTO songs (
    id, name, artists, valence, year, acousticness, danceability,
    duration_ms, energy, explicit, instrumentalness, `key`,
    liveness, loudness, mode, popularity, release_date,
    speechiness, tempo, mood
) VALUES (
    %(id)s, %(name)s, %(artists)s, %(valence)s, %(year)s,
    %(acousticness)s, %(danceability)s, %(duration_ms)s,
    %(energy)s, %(explicit)s, %(instrumentalness)s, %(key)s,
    %(liveness)s, %(loudness)s, %(mode)s, %(popularity)s,
    %(release_date)s, %(speechiness)s, %(tempo)s, %(mood)s
)
"""

data = df.to_dict(orient="records")

cursor.executemany(insert_sql, data)
conn.commit()

print(f"🎉 Inserted {cursor.rowcount} rows into songs")

cursor.close()
conn.close()
print("✅ Done!")