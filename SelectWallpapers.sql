/*
SELECT *, lead(howchanged, 1, 'unknown') OVER(PARTITION BY `head` ORDER BY `date` ASC) lh
FROM wallpapers w
ORDER BY `date` ASC;
*/

-- INSERT INTO wallpapers(head,path,howchanged) VALUES (-1,'path1','idk');
-- INSERT INTO wallpapers(head,path,howchanged) VALUES (-1,'path2','manual');
-- DELETE FROM wallpapers where head=-1;

DROP VIEW wallpapers_leadchange;
CREATE VIEW wallpapers_leadchange AS
SELECT `date`, `head`, `path`, LEAD(howchanged, 1, 'unknown') OVER (PARTITION BY `head` ORDER BY date ASC) `leadchange`
FROM wallpapers
ORDER BY date DESC;

-- Ratio es el numero de veces que se ha cambiado manualmente
-- respecto al numero de veces que ha aparecido el wallpaper
-- No sé, lo chulo sería un indicador que subiese cuando se aproxime
-- el totalcnt a la media, y tambien cuando cnt se aproxime a cnt
SELECT `head`, `path`, (count(*))*1.0/(totalcnt*totalcnt-avgcnt) ratio, count(*) cnt, totalcnt, avgcnt, (totalcnt*totalcnt-avgcnt)
FROM wallpapers_leadchange JOIN (
	SELECT head, path, count(*) totalcnt
	FROM wallpapers_leadchange
	GROUP BY head, path
) USING (head, path) JOIN (
	SELECT head, avg(cnt) avgcnt
	FROM (
		SELECT head, count(*) cnt
		FROM wallpapers_leadchange
		GROUP BY path,head
	)
) USING (head)
WHERE leadchange = 'manual'
GROUP BY `head`, `path`
-- HAVING cnt > 1	-- Así no salen los que sólo has saltado una vez
ORDER BY ratio DESC;

-- Ahora sí joder
SELECT `head`, `path`, count(*)/(
    SELECT avg(cnt) FROM (
        SELECT count(*) AS cnt
        FROM wallpapers
        WHERE head=w.head
        GROUP BY `path`
    )
) avg, count(*) cnt
FROM wallpapers w 
JOIN (
    SELECT `head`, `path`, LEAD(howchanged, 1, 'unknown') OVER (PARTITION BY `head` ORDER BY `date` ASC) ld
    FROM wallpapers
) USING (`head`, `path`)
WHERE ld = 'manual'
GROUP BY `head`,`path`
ORDER BY avg DESC;

-- Esta consulta nos da el promedio de veces que ha pasado cada wallpaper
-- agrupado por head
-- Obviamente, para head 0 y 1 el valor debería ser el mismo
-- Con este valor podemos contrastar si un fondo de pantalla ha sido saltado
-- muchas veces o no
SELECT avg(cnt), head FROM (
    SELECT COUNT(*) AS cnt, head
    FROM wallpapers
    GROUP BY `path`, head
) GROUP BY head;
