from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

c = pd.read_csv("data/vannverk_clean.csv", encoding="utf-8-sig")

fig, ax = plt.subplots(2, 2, figsize=(13, 9))

# 1. Andel vannverk med minst ett avvik, per år
c.groupby("periode")["avvik"].mean().plot(kind="bar", ax=ax[0, 0], color="#2F6DB5")
ax[0, 0].set_title("Andel vannverk med minst ett avvik, per år")
ax[0, 0].set_xlabel("År")
ax[0, 0].set_ylabel("Andel")

# 2. Størrelse på vannverkene (logaritmisk skala, siden noen få er enorme)
np.log10(c.loc[c.vannprod > 0, "vannprod"]).hist(bins=40, ax=ax[0, 1], color="#2E8B57")
ax[0, 1].set_title("Fordeling av vannproduksjon (log10)")
ax[0, 1].set_xlabel("log10(vannprod)")
ax[0, 1].set_ylabel("Antall vannverk-år")
ax[0, 1].grid(False)

# 3. Avviksandel per eierform (de seks vanligste)
topp = c["orgform"].value_counts().head(6).index
(c[c["orgform"].isin(topp)].groupby("orgform")["avvik"].mean()
   .sort_values().plot(kind="barh", ax=ax[1, 0], color="#2F6DB5"))
ax[1, 0].set_title("Andel med avvik, per eierform")
ax[1, 0].set_xlabel("Andel")

# 4. Med og uten UV-behandling
(c.dropna(subset=["uv"]).groupby("uv")["avvik"].mean()
   .rename(index={0.0: "Uten UV", 1.0: "Med UV"})
   .plot(kind="bar", ax=ax[1, 1], color="#2E8B57", rot=0))
ax[1, 1].set_title("Andel med avvik, med og uten UV")
ax[1, 1].set_ylabel("Andel")
ax[1, 1].set_xlabel("")

plt.tight_layout()
plt.savefig(Path(__file__).parent / "oversikt.png", dpi=200)
plt.show()