-- Keep the row with the minimum ID for each title, delete the rest
DELETE FROM movies a USING movies b WHERE a.id > b.id AND a.title = b.title;

-- Optional: Add a unique constraint to prevent future duplicates (might fail if specific titles are duped, but we just cleaned them)
-- ALTER TABLE movies ADD CONSTRAINT unique_title UNIQUE (title);
