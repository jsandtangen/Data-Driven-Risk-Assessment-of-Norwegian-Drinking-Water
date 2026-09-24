/* Are NULLs in the numeric columns empty in the source, or did TRY_CAST fail silently?
   feilet_konvertering and ikke_heltall should be 0. Result from our run: 0 / 0 (7572 empty ant_avvik in the source). */
USE MyDatabase;
GO
SELECT 'ant_analyser' AS kolonne, COUNT(*) AS rader,
       SUM(CASE WHEN ant_analyser IS NULL THEN 1 ELSE 0 END) AS tom_i_kilden,
       SUM(CASE WHEN ant_analyser IS NOT NULL AND TRY_CAST(ant_analyser AS FLOAT) IS NULL THEN 1 ELSE 0 END) AS feilet_konvertering,
       SUM(CASE WHEN TRY_CAST(ant_analyser AS FLOAT) <> FLOOR(TRY_CAST(ant_analyser AS FLOAT)) THEN 1 ELSE 0 END) AS ikke_heltall
FROM vannforsyningssystem_analyse
UNION ALL
SELECT 'ant_avvik', COUNT(*),
       SUM(CASE WHEN ant_avvik IS NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN ant_avvik IS NOT NULL AND TRY_CAST(ant_avvik AS FLOAT) IS NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN TRY_CAST(ant_avvik AS FLOAT) <> FLOOR(TRY_CAST(ant_avvik AS FLOAT)) THEN 1 ELSE 0 END)
FROM vannforsyningssystem_analyse
UNION ALL
SELECT 'verdi_gjsn', COUNT(*),
       SUM(CASE WHEN verdi_gjsn IS NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN verdi_gjsn IS NOT NULL AND TRY_CAST(verdi_gjsn AS FLOAT) IS NULL THEN 1 ELSE 0 END),
       0
FROM vannforsyningssystem_analyse;
GO
