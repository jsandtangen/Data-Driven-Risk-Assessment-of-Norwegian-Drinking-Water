/* Validation of vannverk_aar. Expected: 36034 rows, no duplicates, 0 analyses without reporting. */
USE MyDatabase;
GO
-- 1) No duplicates: both numbers must be equal
SELECT COUNT(*) AS rader, COUNT(DISTINCT CONCAT(mtid_vf, '|', periode)) AS unike_vannverk_aar FROM vannverk_aar;

-- 2) Coverage of analysis / treatment / municipality data
SELECT COUNT(*) AS rader,
       SUM(CASE WHEN total_analyser IS NOT NULL THEN 1 ELSE 0 END) AS med_analyse,
       SUM(CASE WHEN antall_anlegg  IS NOT NULL THEN 1 ELSE 0 END) AS med_behandling,
       SUM(CASE WHEN kommune        IS NOT NULL THEN 1 ELSE 0 END) AS med_kommune
FROM vannverk_aar;

-- 3) Analyses dropped because the water system/year is missing in the reporting table (result: 0)
SELECT COUNT(*) AS analyse_uten_innrapportering
FROM (SELECT DISTINCT mtid_vf, periode FROM vannforsyningssystem_analyse) a
LEFT JOIN vannforsyningssystem_innrapportering i ON i.mtid_vf = a.mtid_vf AND i.periode = a.periode
WHERE i.mtid_vf IS NULL;

SELECT TOP 10 * FROM vannverk_aar ORDER BY mtid_vf, periode;
GO
