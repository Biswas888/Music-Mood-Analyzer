USE music_mood;

DROP TABLE IF EXISTS songs;

CREATE TABLE songs (
    id VARCHAR(50) PRIMARY KEY,
    name TEXT,
    artists TEXT,
    valence FLOAT,
    year INT,
    acousticness FLOAT,
    danceability FLOAT,
    duration_ms INT,
    energy FLOAT,
    explicit INT,
    instrumentalness FLOAT,
    `key` INT,
    liveness FLOAT,
    loudness FLOAT,
    mode INT,
    popularity INT,
    release_date DATE,
    speechiness FLOAT,
    tempo FLOAT,
    mood VARCHAR(20)
);
