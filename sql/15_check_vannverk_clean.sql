/* Expected: 33752 rows, rader = unike_vannverk_aar, andel_med_avvik about 0.575 */
USE MyDatabase;
GO
SELECT COUNT(*) AS rader,
       COUNT(DISTINCT CONCAT(mtid_vf, '|', periode)) AS unike_vannverk_aar,
       COUNT(DISTINCT mtid_vf) AS antall_vannverk,
       ROUND(AVG(CAST(avvik AS FLOAT)), 3) AS andel_med_avvik
FROM vannverk_clean;

SELECT TOP 10 * FROM vannverk_clean ORDER BY mtid_vf, periode;
GO
