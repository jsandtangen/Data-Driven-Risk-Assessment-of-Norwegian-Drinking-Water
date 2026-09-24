/* Detects rows where semicolons inside text shifted the columns (periode not a 4-digit year).
   All numbers should be 0. */
USE MyDatabase;
GO
SELECT 'vannforsyningssystem' AS tabell, COUNT(*) AS feil FROM vannforsyningssystem WHERE periode NOT LIKE '[0-9][0-9][0-9][0-9]'
UNION ALL SELECT 'vannbehandlingsanlegg', COUNT(*) FROM vannbehandlingsanlegg WHERE periode NOT LIKE '[0-9][0-9][0-9][0-9]' AND periode <> ''
UNION ALL SELECT 'innrapportering', COUNT(*) FROM vannforsyningssystem_innrapportering WHERE periode NOT LIKE '[0-9][0-9][0-9][0-9]'
UNION ALL SELECT 'analyse', COUNT(*) FROM vannforsyningssystem_analyse WHERE periode NOT LIKE '[0-9][0-9][0-9][0-9]'
UNION ALL SELECT 'inntakspunkt', COUNT(*) FROM inntakspunkt_analyse WHERE periode NOT LIKE '[0-9][0-9][0-9][0-9]';
GO
