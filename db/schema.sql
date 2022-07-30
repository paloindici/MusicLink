DROP TABLE IF EXISTS albums;

CREATE TABLE "albums" (
	"id"	INTEGER,
	"artistId"	TEXT NOT NULL,
	"artistName"	TEXT NOT NULL,
	"ressourceUrl" TEXT NOT NULL,
	"lastView"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT)
);
