UPDATE songs
SET mood = 'Happy'
WHERE valence > 0.7 AND energy > 0.6;

UPDATE songs
SET mood = 'Sad'
WHERE valence < 0.3 AND energy < 0.4;

UPDATE songs
SET mood = 'Energetic'
WHERE energy > 0.75;

UPDATE songs
SET mood = 'Calm'
WHERE acousticness > 0.7;
