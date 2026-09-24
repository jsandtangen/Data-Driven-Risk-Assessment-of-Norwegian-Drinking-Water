/* The four part files were already merged into one file with a header row. */
USE MyDatabase;
GO
DROP TABLE IF EXISTS vannforsyningssystem_analyse;
CREATE TABLE vannforsyningssystem_analyse (
    mtid_vf NVARCHAR(500), periode NVARCHAR(500), analysetype NVARCHAR(500),
    ant_krav NVARCHAR(500), ant_analyser NVARCHAR(500), ant_avvik NVARCHAR(500),
    verdi_max NVARCHAR(500), verdi_min NVARCHAR(500), verdi_median NVARCHAR(500), verdi_gjsn NVARCHAR(500)
);
GO
BULK INSERT vannforsyningssystem_analyse
FROM 'C:\data\vannforsyningssystem_analyse.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ';', ROWTERMINATOR = '0x0a', CODEPAGE = '65001', TABLOCK);
GO
UPDATE vannforsyningssystem_analyse
SET mtid_vf = REPLACE(mtid_vf, NCHAR(65279), '')   -- strip invisible BOM
WHERE mtid_vf LIKE NCHAR(65279) + '%';
UPDATE vannforsyningssystem_analyse SET verdi_gjsn = REPLACE(verdi_gjsn, CHAR(13), '');
GO
