/* Expected: 5741 / 6109 / 36036 / 271481 / 627311 */
USE MyDatabase;
GO
SELECT 'vannbehandlingsanlegg' AS tabell, COUNT(*) AS antall FROM vannbehandlingsanlegg
UNION ALL SELECT 'vannforsyningssystem', COUNT(*) FROM vannforsyningssystem
UNION ALL SELECT 'vannforsyningssystem_innrapportering', COUNT(*) FROM vannforsyningssystem_innrapportering
UNION ALL SELECT 'inntakspunkt_analyse', COUNT(*) FROM inntakspunkt_analyse
UNION ALL SELECT 'vannforsyningssystem_analyse', COUNT(*) FROM vannforsyningssystem_analyse;
GO
