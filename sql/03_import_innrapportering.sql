USE MyDatabase;
GO
DROP TABLE IF EXISTS vannforsyningssystem_innrapportering;
CREATE TABLE vannforsyningssystem_innrapportering (
    mtid_vf NVARCHAR(500), periode NVARCHAR(500), vannprod NVARCHAR(500), vannegetnett NVARCHAR(500),
    vann_mottatt NVARCHAR(500), max_vann_pers NVARCHAR(500), max_vann_dogn NVARCHAR(500),
    beredsk_oppd NVARCHAR(500), beredsk_ovelse NVARCHAR(500), boliger NVARCHAR(500),
    helseinst NVARCHAR(500), skoler NVARCHAR(500), nmindustri NVARCHAR(500), hyttercamp NVARCHAR(500),
    gardsbruk NVARCHAR(500), fiskemottak NVARCHAR(500), ant_fastboende NVARCHAR(500),
    ant_personer_max NVARCHAR(500), ant_husstander NVARCHAR(500), ant_hytter NVARCHAR(500),
    forbr_fast_bosetting NVARCHAR(500), forbr_fritidsboliger NVARCHAR(500), forbr_industri NVARCHAR(500),
    forbr_tjytende NVARCHAR(500), forbr_primnaering NVARCHAR(500), forbr_annet NVARCHAR(500),
    forbr_lekkasje NVARCHAR(500), vannuttak NVARCHAR(500), noedvann_inngaar_alt_kilde NVARCHAR(500)
);
GO
BULK INSERT vannforsyningssystem_innrapportering
FROM 'C:\data\vannforsyningssystem_innrapportering.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ';', ROWTERMINATOR = '0x0a', CODEPAGE = '65001', TABLOCK);
GO
UPDATE vannforsyningssystem_innrapportering
SET noedvann_inngaar_alt_kilde = REPLACE(noedvann_inngaar_alt_kilde, CHAR(13), '');
GO
