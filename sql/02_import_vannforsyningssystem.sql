USE MyDatabase;
GO
DROP TABLE IF EXISTS vannforsyningssystem;
CREATE TABLE vannforsyningssystem (
    aktiv NVARCHAR(500), orgform NVARCHAR(500), fnr NVARCHAR(500), fnavn NVARCHAR(500),
    orgnr NVARCHAR(500), virksomhet NVARCHAR(500), virksomhet_kommunenr NVARCHAR(500),
    virksomhet_kommune NVARCHAR(500), vannforsyningssystem NVARCHAR(500), mtid_vf NVARCHAR(500),
    ir_orgform NVARCHAR(500), vregnr NVARCHAR(500), kommunenr NVARCHAR(500), kommune NVARCHAR(500),
    mtregion NVARCHAR(500), mtavdeling NVARCHAR(500), siste_insp NVARCHAR(500), omraade NVARCHAR(500),
    periode NVARCHAR(500), vannprod NVARCHAR(500), vannegetnett NVARCHAR(500),
    vann_mottatt NVARCHAR(500), max_vann_pers NVARCHAR(500), max_vann_dogn NVARCHAR(500),
    beredskap NVARCHAR(500), beredsk_oppd NVARCHAR(500), beredsk_ovelse NVARCHAR(500),
    boliger NVARCHAR(500), helseinst NVARCHAR(500), skoler NVARCHAR(500), nmindustri NVARCHAR(500),
    hyttercamp NVARCHAR(500), gardsbruk NVARCHAR(500), fiskemottak NVARCHAR(500),
    ant_fastboende NVARCHAR(500), ant_personer_max NVARCHAR(500), ant_husstander NVARCHAR(500),
    ant_hytter NVARCHAR(500), forbr_fast_bosetting NVARCHAR(500), forbr_fritidsboliger NVARCHAR(500),
    forbr_industri NVARCHAR(500), forbr_tjytende NVARCHAR(500), forbr_primnaering NVARCHAR(500),
    forbr_annet NVARCHAR(500), forbr_lekkasje NVARCHAR(500)
);
GO
BULK INSERT vannforsyningssystem
FROM 'C:\data\vannforsyningssystem.csv'
WITH (FORMAT = 'CSV', FIELDQUOTE = '"', FIRSTROW = 2, FIELDTERMINATOR = ';',
      ROWTERMINATOR = '0x0a', CODEPAGE = '65001', TABLOCK);
GO
UPDATE vannforsyningssystem SET forbr_lekkasje = REPLACE(forbr_lekkasje, CHAR(13), '');
GO
