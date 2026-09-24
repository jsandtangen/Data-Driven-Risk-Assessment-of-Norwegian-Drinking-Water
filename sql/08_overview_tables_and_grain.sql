/* Read-only overview: table sizes, columns, grain, years covered, join coverage, parameters, samples.
   Run each SELECT separately or all at once and click through the result tabs. */
USE MyDatabase;
GO

/* 1. Size of each table */
SELECT t.name AS tabell, SUM(p.rows) AS antall_rader,
       (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS c WHERE c.TABLE_NAME = t.name) AS antall_kolonner
FROM sys.tables t
JOIN sys.partitions p ON p.object_id = t.object_id AND p.index_id IN (0, 1)
GROUP BY t.name ORDER BY t.name;

/* 2. Column names per table */
SELECT TABLE_NAME AS tabell, ORDINAL_POSITION AS nr, COLUMN_NAME AS kolonne
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME IN ('vannforsyningssystem', 'vannbehandlingsanlegg',
                     'vannforsyningssystem_innrapportering',
                     'vannforsyningssystem_analyse', 'inntakspunkt_analyse')
ORDER BY TABLE_NAME, ORDINAL_POSITION;

/* 3. Grain check: what does one row mean in each table? */
SELECT 'vannforsyningssystem' AS tabell, COUNT(*) AS rader, COUNT(DISTINCT mtid_vf) AS unike_systemer,
       COUNT(DISTINCT CONCAT(mtid_vf, '|', periode)) AS unike_system_periode, NULL AS unike_med_analysetype
FROM vannforsyningssystem
UNION ALL
SELECT 'vannbehandlingsanlegg', COUNT(*), COUNT(DISTINCT mtid_vf),
       COUNT(DISTINCT CONCAT(mtid_vf, '|', periode)), COUNT(DISTINCT mtid_vb)
FROM vannbehandlingsanlegg
UNION ALL
SELECT 'innrapportering', COUNT(*), COUNT(DISTINCT mtid_vf),
       COUNT(DISTINCT CONCAT(mtid_vf, '|', periode)), NULL
FROM vannforsyningssystem_innrapportering
UNION ALL
SELECT 'vannforsyningssystem_analyse', COUNT(*), COUNT(DISTINCT mtid_vf),
       COUNT(DISTINCT CONCAT(mtid_vf, '|', periode)),
       COUNT(DISTINCT CONCAT(mtid_vf, '|', periode, '|', analysetype))
FROM vannforsyningssystem_analyse
UNION ALL
SELECT 'inntakspunkt_analyse', COUNT(*), COUNT(DISTINCT mtid_vf),
       COUNT(DISTINCT CONCAT(mtid_vf, '|', periode)),
       COUNT(DISTINCT CONCAT(mtid_vf, '|', mtid_ip, '|', periode, '|', analysetype))
FROM inntakspunkt_analyse;

/* 4. Years covered per table */
SELECT 'vannforsyningssystem' AS tabell, MIN(periode) AS fra, MAX(periode) AS til, COUNT(DISTINCT periode) AS antall_ar FROM vannforsyningssystem
UNION ALL SELECT 'innrapportering', MIN(periode), MAX(periode), COUNT(DISTINCT periode) FROM vannforsyningssystem_innrapportering
UNION ALL SELECT 'vannforsyningssystem_analyse', MIN(periode), MAX(periode), COUNT(DISTINCT periode) FROM vannforsyningssystem_analyse
UNION ALL SELECT 'inntakspunkt_analyse', MIN(periode), MAX(periode), COUNT(DISTINCT periode) FROM inntakspunkt_analyse;

/* 5. Do the tables share the same water systems? */
SELECT 'innrapportering' AS tabell, COUNT(DISTINCT i.mtid_vf) AS systemer_i_tabellen,
       COUNT(DISTINCT CASE WHEN s.mtid_vf IS NOT NULL THEN i.mtid_vf END) AS finnes_i_hovedtabell
FROM vannforsyningssystem_innrapportering i LEFT JOIN vannforsyningssystem s ON s.mtid_vf = i.mtid_vf
UNION ALL
SELECT 'vannforsyningssystem_analyse', COUNT(DISTINCT a.mtid_vf),
       COUNT(DISTINCT CASE WHEN s.mtid_vf IS NOT NULL THEN a.mtid_vf END)
FROM vannforsyningssystem_analyse a LEFT JOIN vannforsyningssystem s ON s.mtid_vf = a.mtid_vf
UNION ALL
SELECT 'inntakspunkt_analyse', COUNT(DISTINCT a.mtid_vf),
       COUNT(DISTINCT CASE WHEN s.mtid_vf IS NOT NULL THEN a.mtid_vf END)
FROM inntakspunkt_analyse a LEFT JOIN vannforsyningssystem s ON s.mtid_vf = a.mtid_vf
UNION ALL
SELECT 'vannbehandlingsanlegg', COUNT(DISTINCT b.mtid_vf),
       COUNT(DISTINCT CASE WHEN s.mtid_vf IS NOT NULL THEN b.mtid_vf END)
FROM vannbehandlingsanlegg b LEFT JOIN vannforsyningssystem s ON s.mtid_vf = b.mtid_vf;

/* 6. Which parameters are measured, and how often? */
SELECT TOP 30 analysetype, COUNT(*) AS antall_rader, COUNT(DISTINCT mtid_vf) AS antall_systemer
FROM vannforsyningssystem_analyse GROUP BY analysetype ORDER BY antall_rader DESC;

/* 7. Sample rows */
SELECT TOP 5 * FROM vannforsyningssystem;
SELECT TOP 5 * FROM vannbehandlingsanlegg;
SELECT TOP 5 * FROM vannforsyningssystem_innrapportering;
SELECT TOP 5 * FROM vannforsyningssystem_analyse;
SELECT TOP 5 * FROM inntakspunkt_analyse;
GO
