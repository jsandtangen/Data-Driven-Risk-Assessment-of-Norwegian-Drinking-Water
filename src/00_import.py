from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[1]

engine = create_engine(
    "mssql+pyodbc://@localhost/MyDatabase"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&trusted_connection=yes&TrustServerCertificate=yes"
)

df = pd.read_sql("SELECT * FROM vannverk_clean ORDER BY mtid_vf, periode", engine)
print(df.shape)   # forventet: (33752, 33)

out = ROOT / "data" / "processed" / "01_vannverk.csv"
df.to_csv(out, index=False, encoding="utf-8-sig")
print("Lagret til:", out)