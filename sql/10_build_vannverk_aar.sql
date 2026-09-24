/* vannverk_aar: one row = one water system in one year (2008-2025), typed, 80 columns.
   Backbone: innrapportering. Analyses are pivoted from long to wide (8 parameters).
   Treatment is aggregated per water system (periode is mostly empty in the source). */
USE MyDatabase;
GO
DROP TABLE IF EXISTS vannverk_aar;
GO

WITH analyse_t AS (
    SELECT mtid_vf,
           TRY_CAST(periode AS INT) AS periode,
           TRY_CAST(TRY_CAST(ant_analyser AS FLOAT) AS INT) AS n,
           TRY_CAST(TRY_CAST(ant_avvik AS FLOAT) AS INT)    AS avvik,
           TRY_CAST(verdi_gjsn AS FLOAT)                    AS gjsn,
           CASE WHEN analysetype = 'Koliforme bakterier'          THEN 'koli'
                WHEN analysetype = 'E. Coli'                      THEN 'ecoli'
                WHEN analysetype LIKE 'Kimtall 22%'               THEN 'kimtall'
                WHEN analysetype = 'Turbiditet'                   THEN 'turb'
                WHEN analysetype = 'Farge'                        THEN 'farge'
                WHEN analysetype = 'pH'                           THEN 'ph'
                WHEN analysetype LIKE 'Intestinale enterokokker%' THEN 'enterok'
                WHEN analysetype = 'Ledningsevne'                 THEN 'ledn'
           END AS p
    FROM vannforsyningssystem_analyse
),
analyse_p AS (
    SELECT mtid_vf, periode,
           SUM(n) AS total_analyser, SUM(avvik) AS total_avvik, COUNT(*) AS antall_parametere,
           MAX(CASE WHEN p='koli'    THEN n     END) AS koli_analyser,
           MAX(CASE WHEN p='koli'    THEN avvik END) AS koli_avvik,
           MAX(CASE WHEN p='koli'    THEN gjsn  END) AS koli_gjsn,
           MAX(CASE WHEN p='ecoli'   THEN n     END) AS ecoli_analyser,
           MAX(CASE WHEN p='ecoli'   THEN avvik END) AS ecoli_avvik,
           MAX(CASE WHEN p='ecoli'   THEN gjsn  END) AS ecoli_gjsn,
           MAX(CASE WHEN p='kimtall' THEN n     END) AS kimtall_analyser,
           MAX(CASE WHEN p='kimtall' THEN avvik END) AS kimtall_avvik,
           MAX(CASE WHEN p='kimtall' THEN gjsn  END) AS kimtall_gjsn,
           MAX(CASE WHEN p='turb'    THEN n     END) AS turb_analyser,
           MAX(CASE WHEN p='turb'    THEN avvik END) AS turb_avvik,
           MAX(CASE WHEN p='turb'    THEN gjsn  END) AS turb_gjsn,
           MAX(CASE WHEN p='farge'   THEN n     END) AS farge_analyser,
           MAX(CASE WHEN p='farge'   THEN avvik END) AS farge_avvik,
           MAX(CASE WHEN p='farge'   THEN gjsn  END) AS farge_gjsn,
           MAX(CASE WHEN p='ph'      THEN n     END) AS ph_analyser,
           MAX(CASE WHEN p='ph'      THEN avvik END) AS ph_avvik,
           MAX(CASE WHEN p='ph'      THEN gjsn  END) AS ph_gjsn,
           MAX(CASE WHEN p='enterok' THEN n     END) AS enterok_analyser,
           MAX(CASE WHEN p='enterok' THEN avvik END) AS enterok_avvik,
           MAX(CASE WHEN p='enterok' THEN gjsn  END) AS enterok_gjsn,
           MAX(CASE WHEN p='ledn'    THEN n     END) AS ledn_analyser,
           MAX(CASE WHEN p='ledn'    THEN avvik END) AS ledn_avvik,
           MAX(CASE WHEN p='ledn'    THEN gjsn  END) AS ledn_gjsn
    FROM analyse_t
    GROUP BY mtid_vf, periode
),
stamdata AS (
    SELECT mtid_vf, vannforsyningssystem AS navn, aktiv, orgform,
           COALESCE(kommunenr, virksomhet_kommunenr) AS kommunenr,
           COALESCE(kommune, virksomhet_kommune)     AS kommune
    FROM vannforsyningssystem
),
behandling AS (
    SELECT mtid_vf,
           COUNT(DISTINCT mtid_vb) AS antall_anlegg,
           MAX(CASE WHEN uv_bestraaling = 'ja' THEN 1 ELSE 0 END)            AS uv,
           MAX(CASE WHEN klorering = 'ja' THEN 1 ELSE 0 END)                 AS klorering,
           MAX(CASE WHEN kloramin = 'ja' THEN 1 ELSE 0 END)                  AS kloramin,
           MAX(CASE WHEN desinfeksjon_ozon = 'ja' THEN 1 ELSE 0 END)         AS ozon_desinf,
           MAX(CASE WHEN desinfeksjon_membran = 'ja' THEN 1 ELSE 0 END)      AS membran_desinf,
           MAX(CASE WHEN filtrering_membran = 'ja' THEN 1 ELSE 0 END)        AS membranfiltrering,
           MAX(CASE WHEN siling = 'ja' THEN 1 ELSE 0 END)                    AS siling,
           MAX(CASE WHEN koagulering = 'ja' THEN 1 ELSE 0 END)               AS koagulering,
           MAX(CASE WHEN flokkulering = 'ja' THEN 1 ELSE 0 END)              AS flokkulering,
           MAX(CASE WHEN sedimentering = 'ja' THEN 1 ELSE 0 END)             AS sedimentering,
           MAX(CASE WHEN flotasjon = 'ja' THEN 1 ELSE 0 END)                 AS flotasjon,
           MAX(CASE WHEN lufting = 'ja' THEN 1 ELSE 0 END)                   AS lufting,
           MAX(CASE WHEN fjerning_jern_mangan = 'ja' THEN 1 ELSE 0 END)      AS fjerning_jern_mangan,
           MAX(CASE WHEN ph_just_korrosjonkontroll = 'ja' THEN 1 ELSE 0 END) AS ph_justering,
           MAX(CASE WHEN avherding = 'ja' THEN 1 ELSE 0 END)                 AS avherding,
           MAX(CASE WHEN ionebytte = 'ja' THEN 1 ELSE 0 END)                 AS ionebytte,
           MAX(CASE WHEN avsalting = 'ja' THEN 1 ELSE 0 END)                 AS avsalting,
           MAX(CASE WHEN kunstig_infiltrasjon = 'ja' THEN 1 ELSE 0 END)      AS kunstig_infiltrasjon
    FROM vannbehandlingsanlegg
    GROUP BY mtid_vf
)
SELECT
    i.mtid_vf,
    TRY_CAST(i.periode AS INT) AS periode,
    s.navn, s.aktiv, s.orgform, s.kommunenr, s.kommune,

    TRY_CAST(i.vannprod AS FLOAT)      AS vannprod,
    TRY_CAST(i.vannegetnett AS FLOAT)  AS vannegetnett,
    TRY_CAST(i.vann_mottatt AS FLOAT)  AS vann_mottatt,
    TRY_CAST(i.vannuttak AS FLOAT)     AS vannuttak,
    TRY_CAST(i.max_vann_pers AS FLOAT) AS max_vann_pers,
    TRY_CAST(i.max_vann_dogn AS FLOAT) AS max_vann_dogn,
    TRY_CAST(TRY_CAST(i.ant_fastboende AS FLOAT) AS INT)   AS ant_fastboende,
    TRY_CAST(TRY_CAST(i.ant_personer_max AS FLOAT) AS INT) AS ant_personer_max,
    TRY_CAST(TRY_CAST(i.ant_husstander AS FLOAT) AS INT)   AS ant_husstander,
    TRY_CAST(TRY_CAST(i.ant_hytter AS FLOAT) AS INT)       AS ant_hytter,
    i.boliger, i.helseinst, i.skoler, i.nmindustri, i.hyttercamp, i.gardsbruk, i.fiskemottak,
    i.beredsk_oppd, i.beredsk_ovelse, i.noedvann_inngaar_alt_kilde,
    TRY_CAST(i.forbr_fast_bosetting AS FLOAT) AS forbr_fast_bosetting,
    TRY_CAST(i.forbr_fritidsboliger AS FLOAT) AS forbr_fritidsboliger,
    TRY_CAST(i.forbr_industri AS FLOAT)       AS forbr_industri,
    TRY_CAST(i.forbr_tjytende AS FLOAT)       AS forbr_tjytende,
    TRY_CAST(i.forbr_primnaering AS FLOAT)    AS forbr_primnaering,
    TRY_CAST(i.forbr_annet AS FLOAT)          AS forbr_annet,
    TRY_CAST(i.forbr_lekkasje AS FLOAT)       AS forbr_lekkasje,

    b.antall_anlegg, b.uv, b.klorering, b.kloramin, b.ozon_desinf, b.membran_desinf,
    b.membranfiltrering, b.siling, b.koagulering, b.flokkulering, b.sedimentering,
    b.flotasjon, b.lufting, b.fjerning_jern_mangan, b.ph_justering, b.avherding,
    b.ionebytte, b.avsalting, b.kunstig_infiltrasjon,

    a.total_analyser, a.total_avvik, a.antall_parametere,
    a.koli_analyser, a.koli_avvik, a.koli_gjsn,
    a.ecoli_analyser, a.ecoli_avvik, a.ecoli_gjsn,
    a.kimtall_analyser, a.kimtall_avvik, a.kimtall_gjsn,
    a.turb_analyser, a.turb_avvik, a.turb_gjsn,
    a.farge_analyser, a.farge_avvik, a.farge_gjsn,
    a.ph_analyser, a.ph_avvik, a.ph_gjsn,
    a.enterok_analyser, a.enterok_avvik, a.enterok_gjsn,
    a.ledn_analyser, a.ledn_avvik, a.ledn_gjsn
INTO vannverk_aar
FROM vannforsyningssystem_innrapportering i
LEFT JOIN stamdata s    ON s.mtid_vf = i.mtid_vf
LEFT JOIN behandling b  ON b.mtid_vf = i.mtid_vf
LEFT JOIN analyse_p a   ON a.mtid_vf = i.mtid_vf AND a.periode = TRY_CAST(i.periode AS INT)
WHERE TRY_CAST(i.periode AS INT) BETWEEN 2008 AND 2025;
GO
