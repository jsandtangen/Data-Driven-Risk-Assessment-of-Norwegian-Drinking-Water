from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]

TXT = {
 "en": dict(
  h1="1. Raw CSV files", h2="2. Joined and typed table", h3="3. Clean analysis table", h4="4. Export",
  title="From five raw CSV files to one clean analysis file",
  rows="rows", cols="columns",
  roles=["master data:\nowner, municipality", "treatment methods:\naggregated per system",
         "backbone:\n1 row per system and year", "results pivoted\nlong to wide (8 parameters)", "not used\n(different level)"],
  aar=["1 row = 1 water system\nin 1 year", "2008-2025", "",
       "Join key: mtid_vf (+ periode)", "", "All columns converted from\ntext to numbers",
       "Text 'NULL' and empty\nstrings become real NULL"],
  clean=["1 row = 1 water system\nin 1 year", "2009-2025", "", "Rows removed:", "year 2008 (nearly empty)", "no samples taken",
         "outcome unknown", "", "Columns removed:", "consumption breakdown", "max water per person/day",
         "treatment without variation", "duplicate volume columns", "", "Added: avvik (0/1), avvik_rate"],
  arrow23="filter rows,\nselect columns", arrow34="Python\nexport",
  csv="vannverk_\nclean.csv", csvsub="ready for\nmodelling",
  foot="SQL Server: BULK INSERT (all columns as text), then TRY_CAST, JOIN and filtering in SQL. Source: Mattilsynet water supply register.")
}
SRC = [("vannforsyningssystem", 6109, 45, True),
       ("vannbehandlingsanlegg", 5741, 33, True),
       ("vannforsyningssystem_\ninnrapportering", 36036, 29, True),
       ("vannforsyningssystem_\nanalyse", 627311, 10, True),
       ("inntakspunkt_analyse", 271481, 10, False)]

BLUE, BLUE_E = "#E3EEF9", "#2F6DB5"
GREEN, GREEN_E = "#E2F3E6", "#2E8B57"
GREY, GREY_E = "#F1F1F1", "#9A9A9A"
DARK = "#222222"

def box(ax, x, y, w, h, fc, ec, ls="-", lw=1.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=lw, ls=ls))

def arrow(ax, p1, p2, color=DARK, ls="-", lw=1.6):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=14, color=color, lw=lw, ls=ls))

def draw(lang):
    t = TXT[lang]
    fig, ax = plt.subplots(figsize=(16, 8.4))
    ax.set_xlim(0, 16); ax.set_ylim(0, 8.4); ax.axis("off")
    ax.text(8, 8.05, t["title"], ha="center", va="center", fontsize=17, fontweight="bold", color=DARK)

    # headers
    for x, s in [(2.3, t["h1"]), (7.95, t["h2"]), (11.95, t["h3"]), (15.0, t["h4"])]:
        ax.text(x, 7.45, s, ha="center", va="center", fontsize=11, fontweight="bold", color="#555555")

    # column 1: five CSV boxes
    bh, gap, y0 = 1.1, 0.22, 0.85
    ys = [y0 + (4 - i) * (bh + gap) for i in range(5)]
    target_x = 6.6
    tall_y0, tall_h = 0.85, 5.9
    for i, ((name, n, c, used), y) in enumerate(zip(SRC, ys)):
        fc, ec, ls = (BLUE, BLUE_E, "-") if used else (GREY, GREY_E, (0, (4, 3)))
        box(ax, 0.2, y, 4.2, bh, fc, ec, ls)
        ax.text(2.3, y + bh * 0.66, name, ha="center", va="center", fontsize=9.5, fontweight="bold",
                color=DARK if used else "#777777", linespacing=1.05)
        ax.text(2.3, y + bh * 0.2, f"{n:,} {t['rows']} x {c} {t['cols']}".replace(",", " "),
                ha="center", va="center", fontsize=8.5, color="#444444" if used else "#888888")
        # arrow to tall box, spread endpoints
        ty = tall_y0 + 0.5 + i * (tall_h - 1.0) / 4
        ty = tall_y0 + tall_h - 0.5 - i * (tall_h - 1.0) / 4
        if used:
            arrow(ax, (4.42, y + bh / 2), (target_x - 0.04, ty), color=BLUE_E)
        else:
            ax.plot([4.42, 5.9], [y + bh / 2, y + bh / 2], color=GREY_E, lw=1.6, ls=(0, (4, 3)))
            ax.text(6.0, y + bh / 2, "x", ha="center", va="center", fontsize=13, color=GREY_E, fontweight="bold")
        ax.text(5.5, ((y + bh / 2 + ty) / 2 + 0.28) if used else (y + bh / 2 + 0.3), t["roles"][i], ha="center", va="center",
                fontsize=7.6, color="#333333" if used else "#888888", linespacing=1.05)

    # column 2: vannverk_aar
    box(ax, target_x, tall_y0, 2.7, tall_h, GREEN, GREEN_E)
    ax.text(target_x + 1.35, tall_y0 + tall_h - 0.4, "vannverk_aar", ha="center", va="center",
            fontsize=12, fontweight="bold", color=DARK)
    ax.text(target_x + 1.35, tall_y0 + tall_h - 0.85, f"36 034 {t['rows']} x 80 {t['cols']}",
            ha="center", va="center", fontsize=9.5, color="#333333")
    ax.text(target_x + 1.35, tall_y0 + tall_h - 3.0, "\n".join(s for s in t["aar"]),
            ha="center", va="center", fontsize=8.6, color="#333333", linespacing=1.25)

    # arrow 2 -> 3
    mid_y = tall_y0 + tall_h / 2
    arrow(ax, (target_x + 2.72, mid_y), (10.56, mid_y), color=GREEN_E, lw=2)
    ax.text(9.95, mid_y + 0.55, t["arrow23"], ha="center", va="center", fontsize=8.4, color="#333333", linespacing=1.05)

    # column 3: vannverk_clean
    cx = 10.6
    box(ax, cx, tall_y0, 2.7, tall_h, GREEN, GREEN_E, lw=2.4)
    ax.text(cx + 1.35, tall_y0 + tall_h - 0.4, "vannverk_clean", ha="center", va="center",
            fontsize=12, fontweight="bold", color=DARK)
    ax.text(cx + 1.35, tall_y0 + tall_h - 0.85, f"33 752 {t['rows']} x 33 {t['cols']}",
            ha="center", va="center", fontsize=9.5, color="#333333")
    ax.text(cx + 1.35, tall_y0 + tall_h - 3.15, "\n".join(t["clean"]),
            ha="center", va="center", fontsize=8.2, color="#333333", linespacing=1.22)

    # arrow 3 -> csv
    arrow(ax, (cx + 2.72, mid_y), (14.04, mid_y), color=GREEN_E, lw=2)
    ax.text(13.72, mid_y + 0.5, t["arrow34"], ha="center", va="center", fontsize=8.4, color="#333333", linespacing=1.05)
    box(ax, 14.1, mid_y - 0.7, 1.75, 1.4, "#FFF6DD", "#C9962B")
    ax.text(14.975, mid_y + 0.25, t["csv"], ha="center", va="center", fontsize=9.5, fontweight="bold", color=DARK, linespacing=1.05)
    ax.text(14.975, mid_y - 0.4, t["csvsub"], ha="center", va="center", fontsize=8, color="#555555", linespacing=1.05)

    ax.text(8, 0.3, t["foot"], ha="center", va="center", fontsize=8.4, color="#666666", style="italic")
    fig.savefig(ROOT / "results" / "figures" / "pipeline.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

draw("en")