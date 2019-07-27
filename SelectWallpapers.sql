/*
SELECT *, lead(howchanged, 1, 'unknown') OVER(PARTITION BY `head` ORDER BY `date` ASC) lh
FROM wallpapers w
ORDER BY `date` ASC;
*/

/*
SELECT `head`, `path`, count(*) cnt
FROM wallpapers w
WHERE lead(howchanged, 'unknown') OVER(PARTITION BY `head` ORDER BY `date` ASC) = 'manual'
GROUP BY `head`,`path`
ORDER BY cnt ASC;
*/

-- Este funciona pero es lento de cojones
SELECT head,`path`, count(*)/(
    SELECT avg(cnt) FROM (
        SELECT COUNT(*) AS cnt, head
        FROM wallpapers
        WHERE head=w.head
        GROUP BY `path`
    )
) pct
FROM wallpapers w
WHERE (SELECT MAX(w2.`date`)
    FROM wallpapers w2
    WHERE w2.head = w.head AND w2.`date` > w.`date`) IN (SELECT `date` FROM wallpapers WHERE head = w.head AND howchanged = 'manual' AND date = (SELECT MAX(w2.`date`)
    FROM wallpapers w2
    WHERE w2.head = w.head AND w2.`date` > w.`date`))
GROUP BY head,`path`
ORDER BY pct;

-- Esta consulta nos da el promedio de veces que ha pasado cada wallpaper
-- agrupado por head
-- Obviamente, para head 0 y 1 el valor debería ser el mismo
-- Con este valor podemos contrastar si un fondo de pantalla ha sido saltado
-- muchas veces o no
SELECT avg(cnt), head FROM (
    SELECT COUNT(*) AS cnt, head
    FROM wallpapers
    GROUP BY `path`, `head`
) GROUP BY head;