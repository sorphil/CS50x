SELECT DISTINCT(people.name) 
FROM people
JOIN stars on stars.person_id = people.id
JOIN movies on stars.movie_id = movies.id
WHERE movies.year = 2004
ORDER BY birth