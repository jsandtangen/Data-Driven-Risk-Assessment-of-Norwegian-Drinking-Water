/* vannverk_clean: one row = one water system in one year (2009-2025).
   Pipeline: 5 raw CSVs -> 5 raw tables (text) -> vannverk_aar (typed, 80 cols) -> vannverk_clean (33 cols).
   Expected: 33752 rows, about 57.5% with a deviation. */
USE MyDatabase;
GO
DROP TABLE IF EXISTS vannverk_clean;
GO

SELECT
    /* Identification (keys, not model variables) */
    mtid_vf, periode, navn, kommune,

    /* Outcome */
    total_analyser,
    total_avvik,
    CASE WHEN total_avvik > 0 THEN 1 ELSE 0 END            AS avvik,       -- main target
    CAST(total_avvik AS FLOAT) / NULLIF(total_analyser, 0) AS avvik_rate,  -- deviations per sample

    /* Bacterial outcome (side analysis). Never use as features when the target is avvik/total_avvik. */
    koli_avvik, ecoli_avvik, enterok_avvik,
    CASE WHEN koli_avvik IS NULL AND ecoli_avvik IS NULL AND enterok_avvik IS NULL THEN NULL
         WHEN COALESCE(koli_avvik, 0) + COALESCE(ecoli_avvik, 0) + COALESCE(enterok_avvik, 0) > 0 THEN 1
         ELSE 0 END                                         AS bakterie_avvik,

    /* Size (use log transform in modelling) */
    vannprod, ant_fastboende, ant_hytter, ant_husstander,

    /* Treatment (columns with real variation; per water system, not per year; NULL = not in register) */
    antall_anlegg, uv, klorering, koagulering, membranfiltrering, siling, lufting, ph_justering,

    /* Structure */
    orgform,
    CASE WHEN aktiv = 'ja' THEN 1 WHEN aktiv = 'nei' THEN 0 END AS aktiv,  -- status today

    /* Services and preparedness (secondary, ja/nei -> 1/0) */
    CASE WHEN boliger        = 'ja' THEN 1 WHEN boliger        = 'nei' THEN 0 END AS boliger,
    CASE WHEN helseinst      = 'ja' THEN 1 WHEN helseinst      = 'nei' THEN 0 END AS helseinst,
    CASE WHEN skoler         = 'ja' THEN 1 WHEN skoler         = 'nei' THEN 0 END AS skoler,
    CASE WHEN hyttercamp     = 'ja' THEN 1 WHEN hyttercamp     = 'nei' THEN 0 END AS hyttercamp,
    CASE WHEN gardsbruk      = 'ja' THEN 1 WHEN gardsbruk      = 'nei' THEN 0 END AS gardsbruk,
    CASE WHEN beredsk_oppd   = 'ja' THEN 1 WHEN beredsk_oppd   = 'nei' THEN 0 END AS beredsk_oppd,
    CASE WHEN beredsk_ovelse = 'ja' THEN 1 WHEN beredsk_ovelse = 'nei' THEN 0 END AS beredsk_ovelse
INTO vannverk_clean
FROM vannverk_aar
WHERE periode >= 2009           -- 2008 is nearly empty
  AND total_analyser > 0        -- drop rows without samples
  AND total_avvik IS NOT NULL;  -- drop rows where the outcome is unknown
GO
