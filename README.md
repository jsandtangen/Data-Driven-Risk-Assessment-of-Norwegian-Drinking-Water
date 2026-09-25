# Data-Driven Risk Assessment of Norwegian Drinking Water

## Struktur

```
├── data/
│   ├── raw/              # de 5 originale CSV-filene
│   └── processed/        # 00_vannverk.csv, 01_vannverk.csv (ikke i git)
├── sql/                  # SQL Server: import av rådata og bygging av vannverk_clean
├── src/
│   ├── 00_import.py              # henter vannverk_clean fra SQL Server -> data/processed/01_vannverk.csv
│   ├── 01_predictor.py           # EDA: én prediktor (vannprod) mot avvik
│   ├── 02_multivariable_check.py # logistisk regresjon med vannprod + total_analyser
│   ├── 03_lowess_analyser.py     # lowess vs. lineær fit for total_analyser
│   ├── 04_pipeline_figure.py     # figur av datapipelinen
│   └── 05_oversikt_figure.py     # 2x2 oversiktsfigur (avvik per år, eierform, UV)
├── notebooks/
│   └── data_analyze.ipynb
└── results/
    └── figures/          # alle figurer
```

## Kjøring

1. Kjør `sql/` i nummerrekkefølge i SQL Server (rådata fra `data/raw/`).
2. `python src/00_import.py`
3. `python src/01_predictor.py`, osv.

Skriptene finner stiene sine selv, så de kan kjøres fra hvilken som helst mappe.
