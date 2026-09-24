USE MyDatabase;
GO
DROP TABLE IF EXISTS inntakspunkt_analyse;
CREATE TABLE inntakspunkt_analyse (
    mtid_vf NVARCHAR(500), mtid_ip NVARCHAR(500), periode NVARCHAR(500), analysetype NVARCHAR(500),
    ant_krav NVARCHAR(500), ant_analyser NVARCHAR(500), verdi_max NVARCHAR(500),
    verdi_min NVARCHAR(500), verdi_median NVARCHAR(500), verdi_gjsn NVARCHAR(500)
);
GO
BULK INSERT inntakspunkt_analyse
FROM 'C:\data\inntakspunkt_analyse.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ';', ROWTERMINATOR = '0x0a', CODEPAGE = '65001', TABLOCK);
GO
UPDATE inntakspunkt_analyse SET verdi_gjsn = REPLACE(verdi_gjsn, CHAR(13), '');
GO
