DROP TABLE IF EXISTS songs;

CREATE TABLE songs (
    id VARCHAR(50) PRIMARY KEY,
    name TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    artists TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
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
    mood VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
);

CREATE INDEX idx_mood ON songs(mood);
CREATE INDEX idx_name ON songs(name(100));
CREATE INDEX idx_artists ON songs(artists(100));
CREATE INDEX idx_year ON songs(year);
CREATE INDEX idx_popularity ON songs(popularity);
