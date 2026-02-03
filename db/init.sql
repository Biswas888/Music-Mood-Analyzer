USE music_mood;
DROP TABLE IF EXISTS songs;

CREATE TABLE songs (
    valence FLOAT,
    year INT,
    acousticness FLOAT,
    artists TEXT,
    danceability FLOAT,
    duration_ms INT,
    energy FLOAT,
    explicit INT,
    id VARCHAR(50) PRIMARY KEY,
    instrumentalness FLOAT,
    `key` INT,
    liveness FLOAT,
    loudness FLOAT,
    mode INT,
    name TEXT,
    popularity INT,
    release_date DATE,        -- change to DATE
    speechiness FLOAT,
    tempo FLOAT
);

