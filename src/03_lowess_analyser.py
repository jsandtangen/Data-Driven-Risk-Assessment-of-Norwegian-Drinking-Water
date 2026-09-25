"""
Steg 3: Sjekk FORMEN på sammenhengen mellom total_analyser og avvik.

Vi antok lineaer sammenheng i log-skala i steg 2 (logistisk regresjon).
Her sjekker vi om den antagelsen faktisk stemmer, med samme lokal
regresjon (lowess)-teknikk som i steg 1.

Hypotese aa teste: flater sammenhengen ut naar total_analyser blir
stor (avtagende marginaleffekt), eller er den virkelig lineaer i
log-skala slik steg 2 antok?
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "results" / "figures"

# ---- 1. Last inn og rydd ----
df = pd.read_csv(ROOT / "data" / "processed" / "01_vannverk.csv")

TARGET = "avvik"
PREDICTOR = "total_analyser"

data = df[[TARGET, PREDICTOR]].dropna()
data = data[data[PREDICTOR] > 0].copy()
print(f"Rader etter rydding: {len(data)}")

data["log_predictor"] = np.log10(data[PREDICTOR])

# ---- 2. Sjekk tetthet per bin, saa vi vet hvor vi kan stole paa kurven ----
data["bin"] = pd.cut(data["log_predictor"], bins=range(0, 6))
print("\nAntall observasjoner per log-bin:")
print(data.groupby("bin", observed=True).size())

# ---- 3. Lokal regresjon (lowess) ----
smoothed = lowess(data[TARGET], data["log_predictor"], frac=0.3)

# ---- 4. For sammenligning: en ren lineaer logistisk fit (steg 2-antagelsen) ----
import statsmodels.api as sm
X = sm.add_constant(data["log_predictor"])
linear_model = sm.Logit(data[TARGET], X).fit(disp=0)
linear_pred = linear_model.predict(X)

# ---- 5. Plot begge sammen ----
plt.figure(figsize=(8, 5))
plt.scatter(data["log_predictor"], data[TARGET], alpha=0.05, s=10, label="Data (jitter skjult)")
plt.plot(smoothed[:, 0], smoothed[:, 1], color="red", linewidth=2, label="Lokal regresjon (lowess)")
order = np.argsort(data["log_predictor"])
plt.plot(data["log_predictor"].values[order], linear_pred.values[order],
          color="black", linestyle="--", linewidth=2, label="Lineaer logistisk fit")
plt.xlabel(f"log10({PREDICTOR})")
plt.ylabel("Sannsynlighet for avvik")
plt.title(f"Sammenheng mellom {PREDICTOR} og avvik: lowess vs. lineaer")
plt.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "03_lowess_total_analyser.png", dpi=150)
print("\nFigur lagret: 03_lowess_total_analyser.png")
plt.show()