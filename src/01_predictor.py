"""
Steg 1: Utforsk sammenhengen mellom EN prediktor og target (avvik).

Tanke fra "Beyond linearity"-forelesningen: se på dataene FØR vi velger
modell. Er sammenhengen lineær, eller krummer den seg (trenger polynom/
spline/lokal regresjon)?

Target: avvik (0/1) - hadde vannverket minst ett avvik dette året?
Prediktor (foreløpig): vannprod (m3 vannproduksjon)
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "results" / "figures"

# ---- 1. Last inn data ----
df = pd.read_csv(ROOT / "data" / "processed" / "01_vannverk.csv")

TARGET = "avvik"
PREDICTOR = "vannprod"

# ---- 2. Enkel rydding: fjern rader uten verdi i det vi ser på ----
data = df[[TARGET, PREDICTOR]].dropna()
print(f"Rader før rydding: {len(df)}, etter rydding: {len(data)}")

# ---- 3. Grunnleggende tall ----
print(f"\nAndel avvik=1: {data[TARGET].mean():.3f}")
print(f"\n{PREDICTOR} beskrivelse:")
print(data[PREDICTOR].describe())

# vannprod er ofte skjevfordelt (noen få store vannverk drar opp snittet),
# så vi bruker log-skala på x-aksen for å se sammenhengen bedre
data = data[data[PREDICTOR] > 0].copy()
data["log_predictor"] = np.log10(data[PREDICTOR])

# ---- 4. Lokal regresjon (lowess) for å se den EKTE formen på sammenhengen ----
# Dette er akkurat "lokal regresjon"-konseptet fra slidene:
# vi fitter lokalt i stedet for å anta en rett linje med en gang.
smoothed = lowess(data[TARGET], data["log_predictor"], frac=0.3)

# ---- 5. Plot ----
plt.figure(figsize=(8, 5))
plt.scatter(data["log_predictor"], data[TARGET], alpha=0.05, s=10, label="Data (jitter skjult)")
plt.plot(smoothed[:, 0], smoothed[:, 1], color="red", linewidth=2, label="Lokal regresjon (lowess)")
plt.xlabel(f"log10({PREDICTOR})")
plt.ylabel("Sannsynlighet for avvik")
plt.title(f"Sammenheng mellom {PREDICTOR} og avvik")
plt.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "01_eda_single_predictor.png", dpi=150)
print("\nFigur lagret: 01_eda_single_predictor.png")
plt.show()