import pandas as pd
import mysql.connector

CSV_FILE = "/app/app/data/data_cleaned.csv"

# --- Load cleaned CSV ---
df = pd.read_csv(CSV_FILE)

print(f"✅ Loaded {len(df)} clean rows")

# --- Fix release_date ---
df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
df["release_date"] = df["release_date"].fillna(pd.Timestamp("1900-01-01"))
df["release_date"] = df["release_date"].dt.strftime("%Y-%m-%d")

# --- Remove duplicates ---
df = df.drop_duplicates(subset=["id"])
print(f"✅ {len(df)} rows after removing duplicates")

# --- Add Mood column ---
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

# --- Insert query ---
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

cursor.executemany(insert_sql, df.to_dict(orient="records"))
conn.commit()

print(f"✅ Inserted {len(df)} rows")

cursor.close()
conn.close()

print("🎉 Clean data loaded successfully!")
