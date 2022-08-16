DROP TABLE IF EXISTS albums;

CREATE TABLE "albums" (
	"id" INTEGER,
	"title" TEXT NOT NULL,
	"releaseId" TEXT NOT NULL,
	"releaseResourceUrl" TEXT NOT NULL,
	"releaseUri" TEXT NOT NULL,
	"format" TEXT NOT NULL,
	"genre" TEXT NOT NULL,
	"masterId" TEXT NOT NULL,
	"masterUrl" TEXT NOT NULL,
	"lastView" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"songStyle" TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
