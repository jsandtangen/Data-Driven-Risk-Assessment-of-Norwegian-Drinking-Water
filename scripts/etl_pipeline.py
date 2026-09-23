"""
ETL-pipeline: Mattilsynets Vannverksregister -> ett analyseklart datasett
=========================================================================

Formal: Slå sammen fem rakilder til ETT tabell med grain
    én rad = ett vannforsyningssystem (mtid_vf) x ett rapporteringsar (periode)

Kilder:
    1. vannforsyningssystem_analyse_part_{0,1,2,3}.csv  -> behandlet vann, malt PA NETTET/etter behandling
    2. inntakspunkt_analyse.csv                          -> ravannskvalitet FOR behandling
    3. vannforsyningssystem.csv                          -> statiske systemattributter (org, kommune, aktiv)
    4. vannforsyningssystem_innrapportering.csv          -> arlig driftsdata (produksjon, forbruk, befolkning)
    5. vannbehandlingsanlegg.csv                         -> boolske behandlingsmetode-flagg per anlegg

Kjør: python scripts/etl_pipeline.py   (fra repo-roten, eller hvor som helst -
                                         stiene er relative til scriptets egen
                                         plassering, ikke til gjeldende mappe)
Krever: pandas

Forventet mappestruktur (script ligger i scripts/, ved siden av data-mappene):
    prosjekt/
    ├── data_unfiltered/   <- de fem rafilene legges her
    ├── data/              <- final_datasett.csv + data_dictionary.md havner her
    └── scripts/
        └── etl_pipeline.py   (denne filen)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Stier regnes relativt til DENNE filens plassering, ikke til en hardkodet
# personlig sti (f.eks. "C:\Users\jsand\...") og ikke til mappa du står i når
# du kjører scriptet. Dermed fungerer koden uansett hvor repoet ligger, og
# uansett hvem som kloner det.
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

RAW_DIR = REPO_ROOT / "data_unfiltered"
OUT_DIR = REPO_ROOT / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Antall parametre som pivoteres til bredt format for hver av de to malepunktene.
# Valgt som de N mest malte parametrene i behandlet-vann-tabellen (dekker de
# aller fleste system-ar). Se data_dictionary.md for full liste og begrunnelse.
N_TOP_PARAMS = 16


# ---------------------------------------------------------------------------
# 0. Hjelpefunksjoner
# ---------------------------------------------------------------------------

def fix_mojibake(s):
    """
    Retter tegnkoding-feilen i vannforsyningssystem_analyse-filene.

    Rafilene ligger med gyldig UTF-8-header (BOM i part_1..3 mangler til og
    med header i det hele tatt), men *innholdet* i analysetype-kolonnen har
    vaert kjort gjennom en feil dekoding: UTF-8-bytene ble opprinnelig lest
    som Windows-1252 og deretter lagret pa nytt som UTF-8 ("dobbel koding").
    Sympt: "Kimtall 22Â° C" i stedet for "Kimtall 22° C", "KvikksÃ¸lv" i
    stedet for "Kvikksølv", og noen sjeldnere tilfeller som involverer C1-
    kontrolltegn ("UTGÃ…TT" i stedet for "UTGÅTT").

    Fasiten er entydig: encode('cp1252') + decode('utf-8') gjenoppretter alle
    87 unike analysetype-verdier korrekt (verifisert manuelt mot kjente
    norske kjemi-/mikrobiologibetegnelser). encode('latin-1') alene retter
    kun de vanligste tilfellene, ikke C1-kontrolltegn-variantene - derfor
    cp1252 og ikke latin-1.
    """
    if not isinstance(s, str):
        return s
    try:
        return s.encode("cp1252").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return s


def load_analyse_treated():
    """
    Laster og setter sammen de fire delfilene for behandlet-vann-analysene.

    VIKTIG STRUKTURFEIL I RAFILENE: kun part_0 har header-rad. part_1, part_2
    og part_3 mangler header helt og starter rett pa datarader - de er rene
    fortsettelser av part_0 og ma leses med header=None og de samme
    kolonnenavnene pafort manuelt. Uten a vite dette vil den forste dataraden
    i hver av de tre siste filene bli feilaktig tolket som kolonneoverskrift.
    """
    cols = [
        "mtid_vf", "periode", "analysetype", "ant_krav", "ant_analyser",
        "ant_avvik", "verdi_max", "verdi_min", "verdi_median", "verdi_gjsn",
    ]
    parts = [
        "vannforsyningssystem_analyse_part_0.csv",
        "vannforsyningssystem_analyse_part_1.csv",
        "vannforsyningssystem_analyse_part_2.csv",
        "vannforsyningssystem_analyse_part_3.csv",
    ]
    frames = []
    for i, fname in enumerate(parts):
        path = RAW_DIR / fname
        if i == 0:
            df = pd.read_csv(path, sep=";", encoding="utf-8", header=0,
                              names=cols, dtype={"periode": str})
        else:
            df = pd.read_csv(path, sep=";", encoding="utf-8", header=None,
                              names=cols, dtype={"periode": str})
        frames.append(df)

    analyse = pd.concat(frames, ignore_index=True)
    analyse["analysetype"] = analyse["analysetype"].apply(fix_mojibake)
    analyse["periode"] = pd.to_numeric(analyse["periode"], errors="coerce").astype("Int64")
    return analyse


def load_intakspunkt():
    """Ravannskvalitet malt ved inntakspunktet, FOR behandling."""
    df = pd.read_csv(RAW_DIR / "inntakspunkt_analyse.csv", sep=";", encoding="utf-8")
    df["periode"] = pd.to_numeric(df["periode"], errors="coerce").astype("Int64")
    return df


def load_vannforsyningssystem():
    """Statisk systemtabell (én rad per mtid_vf)."""
    df = pd.read_csv(RAW_DIR / "vannforsyningssystem.csv", sep=";", encoding="utf-8",
                      low_memory=False)
    return df


def load_innrapportering():
    """Årlig driftsrapportering (produksjon, forbruk, befolkning) - system x år."""
    df = pd.read_csv(RAW_DIR / "vannforsyningssystem_innrapportering.csv", sep=";",
                      encoding="utf-8", low_memory=False)
    return df


def load_behandlingsanlegg():
    """Behandlingsmetoder per anlegg (kan være flere anlegg per system)."""
    df = pd.read_csv(RAW_DIR / "vannbehandlingsanlegg.csv", sep=";", encoding="utf-8",
                      low_memory=False)
    return df


# ---------------------------------------------------------------------------
# 1. Rens vannforsyningssystem.csv -> statisk systemdimensjon
# ---------------------------------------------------------------------------

def build_dim_system(vfs: pd.DataFrame) -> pd.DataFrame:
    """
    Renser fil 3 til en statisk dimensjonstabell med én rad per mtid_vf.

    Valg som er gjort:
    - mtregion droppes helt: kolonnen inneholder KUN feilteksten
      "ERROR [MAT_EJBOrgUnit]" for alle 6109 rader (0% brukbar informasjon).
    - kommune-fallback: virksomhet_kommunenr/virksomhet_kommune brukes som
      primaer kommunekilde (kun 5,4% missing), med kommunenr/kommune som
      reserve der virksomhet-feltet mangler (kommunenr mangler i 56,3%
      av radene alene, sa det duger ikke som primaerkilde).
    - periode/vannprod/vannegetnett/vann_mottatt/max_vann_* og
      forbr_*-kolonnene i denne filen droppes: de er arlige/tidsvarierende
      felt, men denne tabellen har kun ÉN rad per system (en "siste kjente"
      snapshot), sa de gir et misvisende engangs-tidsstempel i stedet for en
      ordentlig tidsserie. De samme feltene finnes ar-for-ar i
      innrapportering.csv, som brukes til det formalet i stedet.
    - omraade droppes: 1009 av 1073 ikke-null-verdier er sopp ("0", ".", "?",
      "x") uten tydelig betydning.
    """
    df = vfs.copy()

    df["kommunenr_final"] = df["virksomhet_kommunenr"].fillna(df["kommunenr"])
    df["kommune_final"] = df["virksomhet_kommune"].fillna(df["kommune"])

    keep = [
        "mtid_vf", "aktiv", "orgform", "fnavn", "virksomhet",
        "kommunenr_final", "kommune_final", "mtavdeling", "siste_insp",
    ]
    dim = df[keep].rename(columns={
        "kommunenr_final": "kommunenr",
        "kommune_final": "kommune",
        "aktiv": "system_aktiv",
    })
    dim["system_aktiv"] = (dim["system_aktiv"] == "ja")

    dup = dim["mtid_vf"].duplicated().sum()
    assert dup == 0, f"Uventet: {dup} duplikate mtid_vf i vannforsyningssystem.csv"
    return dim


# ---------------------------------------------------------------------------
# 2. Aggreger vannbehandlingsanlegg.csv til system-nivå
# ---------------------------------------------------------------------------

TREATMENT_COLS = [
    "kunstig_infiltrasjon", "siling", "filtrering_membran", "desinfeksjon_membran",
    "avsalting", "koagulering", "flokkulering", "flotasjon", "sedimentering",
    "ionebytte", "filtrering_ozon", "desinfeksjon_ozon", "uv_bestraaling",
    "klorering", "kloramin", "desinfeksjon_annen", "lufting",
    "fjerning_jern_mangan", "fjerning_uorg_stoff", "ph_just_korrosjonkontroll",
    "avherding", "dosering_andre_kjemikalier", "andre_behandlingsmetoder",
]


def build_dim_treatment(vba: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregerer behandlingsmetode-flaggene fra anleggsniva til systemniva.

    Et system kan ha flere anlegg (snitt 1,27, opptil 16). Vi definerer
    "systemet har metode X" = TRUE hvis MINST ETT av systemets anlegg
    (uavhengig av periode/rapporteringsar og uavhengig av om anlegget selv
    er "aktiv") har flagget satt til "ja". Dette er en bevisst forenkling:
    vi ser bort fra NAR i tid en gitt behandlingsmetode ble tatt i bruk, og
    behandler behandlingsprofilen som en (tilnaermet) statisk systemegenskap.
    Begrunnelse: vba.periode er stort sett en rapporteringsdato/siste-
    oppdatert-dato (1579 av 5741 rader mangler periode helt, og 1879 er
    satt til 2025), ikke en pålitelig historisk tidsserie - a prøve a
    koble behandlingsmetoder ar-for-ar mot analyse-tabellen ville gitt et
    falskt presisjonsniva.

    Systemer som mangler helt i vba.csv (640 av 3863, ca. 16,6%) far
    NaN i alle behandlingskolonner - IKKE False. Det finnes ingen kilde i
    datasettet som bekrefter at disse systemene faktisk mangler enhver
    behandling; det kan like gjerne vaere manglende rapportering. Modeller
    som bruker disse kolonnene ma eksplisitt handtere denne NaN-kategorien
    (f.eks. som "ukjent behandling", ikke som "nei").
    """
    grp = vba.groupby("mtid_vf")

    agg = grp[TREATMENT_COLS].apply(lambda g: (g == "ja").any())
    agg = agg.astype("boolean")  # nullable bool - NaN bevares eksplisitt der aktuelt

    meta = grp.agg(
        n_anlegg=("mtid_vb", "nunique"),
        n_anlegg_aktive=("aktiv", lambda s: (s == "ja").sum()),
    )

    dim = pd.concat([agg, meta], axis=1).reset_index()
    dim = dim.add_prefix("beh_")
    dim = dim.rename(columns={"beh_mtid_vf": "mtid_vf"})
    return dim


# ---------------------------------------------------------------------------
# 3. Pivoter lange analyse-tabeller til bredt format
# ---------------------------------------------------------------------------

def top_parameters(df: pd.DataFrame, n: int) -> list:
    return df.groupby("analysetype").size().sort_values(ascending=False).head(n).index.tolist()


def slugify(name: str) -> str:
    """Enkel normalisering av analysetype-navn til gyldige kolonnenavn."""
    repl = {
        "æ": "ae", "ø": "oe", "å": "aa", "Æ": "Ae", "Ø": "Oe", "Å": "Aa",
        "°": "grad", ".": "", "(": "", ")": "", ",": "", "-": "_", " ": "_",
    }
    out = name
    for a, b in repl.items():
        out = out.replace(a, b)
    return out.lower().strip("_")


def pivot_wide(df: pd.DataFrame, params: list, prefix: str,
               value_col: str = "verdi_gjsn") -> pd.DataFrame:
    """
    Pivoterer (mtid_vf, periode, analysetype) -> bredt format med én kolonne
    per analysetype (prefix_<parameter> = value_col for den maleserien).

    Hvis samme (mtid_vf, periode, analysetype)-kombinasjon forekommer flere
    ganger (skjer i inntakspunkt_analyse.csv fordi ett system kan ha flere
    inntakspunkt - 68 604 duplikate nokler av 271 481 rader), tas
    gjennomsnittet pa tvers av malepunktene FOR pivotering. Dette gir "typisk
    ravannskvalitet for systemet det aret", ikke verstefall-punktet - et
    bevisst, dokumentert valg.
    """
    sub = df[df["analysetype"].isin(params)].copy()
    sub = sub.groupby(["mtid_vf", "periode", "analysetype"], as_index=False)[value_col].mean()

    wide = sub.pivot(index=["mtid_vf", "periode"], columns="analysetype", values=value_col)
    wide.columns = [f"{prefix}_{slugify(c)}" for c in wide.columns]
    wide = wide.reset_index()
    return wide


def build_target(analyse: pd.DataFrame) -> pd.DataFrame:
    """
    Bygger malvariabelen pa system-ar-niva fra HELE analyse-tabellen (alle 87
    parametre), ikke bare de N parametrene som pivoteres til features.
    Begrunnelse: malvariabelen skal reflektere det fulle regulatoriske bildet
    (et avvik pa hvilken som helst av de 87 parametrene teller), mens
    feature-settet er begrenset av praktiske grunner (dekning/sparsity).

    To varianter leveres:
    - har_avvik   : boolsk, 1 hvis minst ett avvik ble registrert det aret
    - antall_avvik: sum av ant_avvik pa tvers av alle malte parametre
    - andel_avvik : antall_avvik / totalt antall analyser det aret (0-1)
    """
    g = analyse.groupby(["mtid_vf", "periode"]).agg(
        antall_avvik=("ant_avvik", "sum"),
        antall_analyser_totalt=("ant_analyser", "sum"),
        antall_parametre_malt=("analysetype", "nunique"),
    ).reset_index()

    g["har_avvik"] = (g["antall_avvik"] > 0).astype(int)
    g["andel_avvik"] = np.where(
        g["antall_analyser_totalt"] > 0,
        g["antall_avvik"] / g["antall_analyser_totalt"],
        np.nan,
    )
    return g


# ---------------------------------------------------------------------------
# 4. Rens innrapportering.csv (den ar-for-ar-varierende basetabellen)
# ---------------------------------------------------------------------------

def build_fact_innrapportering(inn: pd.DataFrame) -> pd.DataFrame:
    """
    innrapportering.csv er tidsseriekilden for drift/forbruk (36 036 rader,
    4053 systemer, 2000-2025), i motsetning til vannforsyningssystem.csv som
    kun har én statisk snapshot-rad per system. Denne brukes derfor som
    grunntabell for de ar-varierende operasjonelle feltene.

    Missing data pa forbr_*, max_vann_pers/max_vann_dogn og
    noedvann_inngaar_alt_kilde (40-62,5% missing) behandles som STRUKTURELT
    missing (mindre vannverk rapporterer ikke pa samme detaljniva), IKKE
    imputert her - det overlates til modelleringssteget a velge
    imputeringsstrategi, med denne antagelsen dokumentert.
    """
    df = inn.copy()
    df["periode"] = pd.to_numeric(df["periode"], errors="coerce").astype("Int64")
    dup = df.duplicated(subset=["mtid_vf", "periode"]).sum()
    assert dup == 0, f"Uventet: {dup} duplikate (mtid_vf, periode) i innrapportering.csv"
    return df


# ---------------------------------------------------------------------------
# 5. Hovedpipeline
# ---------------------------------------------------------------------------

def main():
    print("Laster rafiler ...")
    analyse = load_analyse_treated()
    ip = load_intakspunkt()
    vfs = load_vannforsyningssystem()
    inn = load_innrapportering()
    vba = load_behandlingsanlegg()

    print(f"  behandlet-vann-analyser : {len(analyse):>8,} rader, "
          f"{analyse['mtid_vf'].nunique():,} systemer, {analyse['analysetype'].nunique()} parametre")
    print(f"  ravann-analyser (intak) : {len(ip):>8,} rader, "
          f"{ip['mtid_vf'].nunique():,} systemer, {ip['analysetype'].nunique()} parametre")
    print(f"  systemtabell            : {len(vfs):>8,} rader")
    print(f"  innrapportering         : {len(inn):>8,} rader, {inn['mtid_vf'].nunique():,} systemer")
    print(f"  behandlingsanlegg       : {len(vba):>8,} rader, {vba['mtid_vf'].nunique():,} systemer")

    print("\nBygger dimensjoner og faktatabeller ...")
    dim_system = build_dim_system(vfs)
    dim_treatment = build_dim_treatment(vba)
    fact_inn = build_fact_innrapportering(inn)
    target = build_target(analyse)

    top_treated = top_parameters(analyse, N_TOP_PARAMS)
    top_raw = top_parameters(ip, N_TOP_PARAMS)
    treated_wide = pivot_wide(analyse, top_treated, prefix="behandlet")
    raw_wide = pivot_wide(ip, top_raw, prefix="raavann")

    print(f"  {len(dim_system):,} systemer i dim_system")
    print(f"  {len(dim_treatment):,} systemer i dim_treatment "
          f"({vba['mtid_vf'].nunique()} av {analyse['mtid_vf'].nunique()} malekvalitet-systemer dekket)")
    print(f"  {len(target):,} system-ar-rader med definert malvariabel")
    print(f"  Topp {N_TOP_PARAMS} behandlet-vann-parametre: {top_treated}")
    print(f"  Topp {N_TOP_PARAMS} ravann-parametre: {top_raw}")

    print("\nSlar sammen til endelig tabell (grain = mtid_vf x periode) ...")
    # Grunntabellen er (mtid_vf, periode)-kombinasjonene som HAR en definert
    # malvariabel (target). Dette er en bevisst innsnevring fra
    # innrapporterings 36 036 rader (ar 2000-2025) til de 34 420 radene som
    # har en tilsvarende ma-lekvalitetsrapport (ar 2008-2025) - uten
    # malvariabel kan ikke raden brukes til klassifisering/regresjon.
    final = target.merge(fact_inn, on=["mtid_vf", "periode"], how="left")
    final = final.merge(dim_system, on="mtid_vf", how="left")
    final = final.merge(dim_treatment, on="mtid_vf", how="left")
    final = final.merge(treated_wide, on=["mtid_vf", "periode"], how="left")
    final = final.merge(raw_wide, on=["mtid_vf", "periode"], how="left")

    # Lag-feature: hadde systemet avvik i FORRIGE rapporteringsar?
    # (nyttig autokorrelasjonssignal, og unngar lekkasje siden det kun bruker
    # informasjon fra fortiden)
    final = final.sort_values(["mtid_vf", "periode"])
    final["har_avvik_forrige_aar"] = (
        final.groupby("mtid_vf")["har_avvik"].shift(1)
    )

    n_before = len(final)
    dup_final = final.duplicated(subset=["mtid_vf", "periode"]).sum()
    assert dup_final == 0, f"Uventet: {dup_final} duplikate rader i sluttresultatet"

    print(f"  Ferdig tabell: {len(final):,} rader x {final.shape[1]} kolonner")
    print(f"  Systemer: {final['mtid_vf'].nunique():,}")
    print(f"  Ar: {int(final['periode'].min())}-{int(final['periode'].max())}")
    print(f"  Andel har_avvik=1: {final['har_avvik'].mean()*100:.2f}%")

    out_path = OUT_DIR / "vannkvalitet_final_datasett.csv"
    final.to_csv(out_path, index=False, sep=";", encoding="utf-8")
    print(f"\nLagret: {out_path}")

    return final


if __name__ == "__main__":
    main()
