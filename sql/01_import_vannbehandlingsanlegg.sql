/* Raw import (all columns as text = staging). CSV files must be in C:\data.
   FORMAT = 'CSV' is needed because text fields contain semicolons inside quotes. */
USE MyDatabase;
GO
DROP TABLE IF EXISTS vannbehandlingsanlegg;
CREATE TABLE vannbehandlingsanlegg (
    aktiv NVARCHAR(500), mtid_vf NVARCHAR(500), mtid_vb NVARCHAR(500), mtid_parent NVARCHAR(500),
    vannforsyningssystem NVARCHAR(500), behandlingsanlegg NVARCHAR(500), kommunenr NVARCHAR(500),
    kommune NVARCHAR(500), funksjon NVARCHAR(500), kunstig_infiltrasjon NVARCHAR(500),
    siling NVARCHAR(500), filtrering_membran NVARCHAR(500), desinfeksjon_membran NVARCHAR(500),
    avsalting NVARCHAR(500), koagulering NVARCHAR(500), flokkulering NVARCHAR(500),
    flotasjon NVARCHAR(500), sedimentering NVARCHAR(500), ionebytte NVARCHAR(500),
    filtrering_ozon NVARCHAR(500), desinfeksjon_ozon NVARCHAR(500), uv_bestraaling NVARCHAR(500),
    klorering NVARCHAR(500), kloramin NVARCHAR(500), desinfeksjon_annen NVARCHAR(500),
    lufting NVARCHAR(500), fjerning_jern_mangan NVARCHAR(500), fjerning_uorg_stoff NVARCHAR(500),
    ph_just_korrosjonkontroll NVARCHAR(500), avherding NVARCHAR(500),
    dosering_andre_kjemikalier NVARCHAR(500), andre_behandlingsmetoder NVARCHAR(500),
    periode NVARCHAR(500)
);
GO
BULK INSERT vannbehandlingsanlegg
FROM 'C:\data\vannbehandlingsanlegg.csv'
WITH (FORMAT = 'CSV', FIELDQUOTE = '"', FIRSTROW = 2, FIELDTERMINATOR = ';',
      ROWTERMINATOR = '0x0a', CODEPAGE = '65001', TABLOCK);
GO
UPDATE vannbehandlingsanlegg SET periode = REPLACE(periode, CHAR(13), '');  -- strip stray \r
GO
