/* Converts the text 'NULL' and empty strings to real NULL in all raw tables.
   Must run BEFORE TRY_CAST, because TRY_CAST('' AS FLOAT) returns 0, not NULL. */
USE MyDatabase;
GO
DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql += N'UPDATE ' + QUOTENAME(TABLE_NAME) + N' SET ' + QUOTENAME(COLUMN_NAME)
             + N' = NULL WHERE LTRIM(RTRIM(' + QUOTENAME(COLUMN_NAME) + N')) IN (N'''', N''NULL'');' + CHAR(10)
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME IN ('vannforsyningssystem', 'vannbehandlingsanlegg',
                     'vannforsyningssystem_innrapportering',
                     'vannforsyningssystem_analyse', 'inntakspunkt_analyse');
EXEC sp_executesql @sql;
GO
