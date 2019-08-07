CREATE TABLE "wallpapers" (
	"date"	DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"head"	INTEGER NOT NULL,
	"path"	TEXT NOT NULL,
	"howchanged"	TEXT DEFAULT 'auto',
	PRIMARY KEY("date","head")
);

DROP VIEW wallpapers_leadchange;
CREATE VIEW wallpapers_leadchange AS
SELECT `date`, `head`, `path`, LEAD(howchanged, 1, 'unknown') OVER (PARTITION BY `head` ORDER BY date ASC) `leadchange`
FROM wallpapers
ORDER BY date DESC;