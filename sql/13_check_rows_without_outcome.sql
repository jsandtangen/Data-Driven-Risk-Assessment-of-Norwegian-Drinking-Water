/* Water-system years with samples but no deviation data (result: 546). These are dropped in vannverk_clean. */
USE MyDatabase;
GO
SELECT COUNT(*) AS vannverk_aar_med_analyser_men_uten_avvik
FROM vannverk_aar
WHERE total_analyser IS NOT NULL AND total_avvik IS NULL;
GO
