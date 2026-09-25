"""
Steg 2: Sjekk om sammenhengen mellom vannprod og avvik overlever
naar vi kontrollerer for total_analyser (testintensitet).

Fra "Beyond linearity"-tankegangen: nå gaar vi fra én prediktor
til flere - foerste steg mot en additiv modell (GAM-tankegang),
men fortsatt enkelt: lineaer logistisk regresjon på to log-transformerte
prediktorer.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm

# ---- 1. Last inn og rydd ----
df = pd.read_csv("data/01_vannverk.csv")

TARGET = "avvik"
PRED_1 = "vannprod"
PRED_2 = "total_analyser"

data = df[[TARGET, PRED_1, PRED_2]].dropna()
data = data[(data[PRED_1] > 0) & (data[PRED_2] > 0)].copy()
print(f"Rader etter all rydding (begge prediktorer > 0, ingen NaN): {len(data)}")

# Log-transformer begge - vi vet fra forrige steg at begge er sterkt skjevfordelte
data["log_vannprod"] = np.log10(data[PRED_1])
data["log_total_analyser"] = np.log10(data[PRED_2])

y = data[TARGET]

def fit_and_report(X_cols, label):
    X = sm.add_constant(data[X_cols])
    model = sm.Logit(y, X).fit(disp=0)
    print(f"\n--- {label} ---")
    print(model.summary2().tables[1][["Coef.", "P>|z|"]])
    return model

# ---- 2. Tre modeller for sammenligning ----
fit_and_report(["log_vannprod"], "Kun vannprod")
fit_and_report(["log_total_analyser"], "Kun total_analyser")
fit_and_report(["log_vannprod", "log_total_analyser"], "Begge sammen")