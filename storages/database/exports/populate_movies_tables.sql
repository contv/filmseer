-- FilmSeer Movie Tables --

CREATE SCHEMA IF NOT EXISTS backup;

CREATE EXTENSION pgcrypto;

-- Create backup of Public tables
CREATE TABLE IF NOT EXISTS backup.movies AS TABLE public.movies;
CREATE TABLE IF NOT EXISTS backup.genres AS TABLE public.genres;
CREATE TABLE IF NOT EXISTS backup.movie_genres AS TABLE public.movie_genres;
CREATE TABLE IF NOT EXISTS backup.people AS TABLE public.people;
CREATE TABLE IF NOT EXISTS backup.positions AS TABLE public.positions;
CREATE TABLE IF NOT EXISTS backup.profileimages AS TABLE public.profileimages;
CREATE TABLE IF NOT EXISTS backup.users AS TABLE public.users;

-- Populate backup tables with IMDB data
-- Genres
;WITH genres AS (
	SELECT DISTINCT	unnest(string_to_array(trim(both '{}' from genres::text), ',')) as genre
	FROM imdbdata.imdb_movies
)
INSERT INTO backup.Genres (genre_id, name)
SELECT
	gen_random_uuid() as genre_id,
	genre as name
FROM genres
WHERE genre != 'N' -- Exclude IMDB's genre value of 'N' which represents null

-- People
ALTER TABLE backup.people
ADD COLUMN imdb_person_id text;

;INSERT INTO backup.people (person_id, name, image, imdb_person_id)
SELECT
	gen_random_uuid() as person_id,
	a."primaryname" as name,
	b."url" as image,
	a."nconst" as imdb_person_id
FROM imdbdata.imdb_names a
LEFT JOIN (
	SELECT "nconst", "url"
	FROM imdbdata.scrape_imdb_actor
	UNION
	SELECT "nconst", "url"
	FROM imdbdata.scrape_imdb_director
) b
ON a.nconst = b.nconst
WHERE LENGTH(a."primaryname") < 200 -- imdb_name seems to have 1 row with excessive length that causes crashing

-- Movies
ALTER TABLE backup.movies
ADD COLUMN imdb_movie_id text;

;INSERT INTO backup.movies (movie_id, title, release_date, description, image, trailer, imdb_movie_id)
SELECT
	gen_random_uuid() as movie_id,
	a."primarytitle" as title,
	TO_TIMESTAMP(a."startyear"::text, 'YYYY') as release_date,
	b."summary" as description,
	b."poster" as image,
	c."trailer" as trailer,
	a."tconst" as imdb_movie_id
FROM imdbdata.imdb_movies a
LEFT JOIN imdbdata.scrape_imdb_summary_poster b
ON a."tconst" = b."tconst"
LEFT JOIN imdbdata.scrape_themoviedb_summary_trailer c
ON a."tconst" = c."tconst"
WHERE a."startyear" IS NOT NULL -- Exclude movies without a year

-- MovieGenres
;WITH moviesWithGenreSplit AS (
	SELECT
		"tconst",
		unnest(string_to_array(trim(both '{}' from genres::text), ',')) as genre
	FROM imdbdata.imdb_movies
)
INSERT INTO backup.movie_genres (moviegenre_id, movie_id, genre_id)
SELECT
	gen_random_uuid() as moviegenre_id,
	c.movie_id as movie_id,
	b.genre_id as genre_id
FROM moviesWithGenreSplit a
JOIN backup.genres b
ON a."genre" = b."name"
JOIN backup.movies c
ON a."tconst" = c."imdb_movie_id"
WHERE a.genre != 'N' -- Exclude IMDB's genre value of 'N' which represents null

-- Positions
;INSERT INTO backup.positions (position_id, movie_id, person_id, position, char_name)
SELECT
	gen_random_uuid() as position_id,
	b."movie_id" as movie_id,
	c."person_id" as person_id,
	a."category" as position,
	CASE WHEN a."characters" = '\N' THEN NULL ELSE a.characters END as char_name
FROM imdbdata.imdb_principals a
JOIN backup.movies b
ON a."tconst" = b."imdb_movie_id"
JOIN backup.people c
ON a."nconst" = c."imdb_person_id"
WHERE LENGTH(a."category") < 100

-- Drop temporary columns used for joining
ALTER TABLE backup.people
DROP COLUMN imdb_person_id;

ALTER TABLE backup.movies
DROP COLUMN imdb_movie_id;


