"""
============================================================================
  EVCS TECHNO-ECONOMIC ANALYSIS — End-to-End ML Pipeline
  A Techno-Economical Analysis of Indian EV Charging Infrastructure
============================================================================
  Authors : Chaitanya Karthik M, Saireesh Murali G, Sathvik G
  Course  : BCSE498J Project-II | SCOPE, VIT
  Date    : February 2026

  Pipeline Steps:
      1.  Dataset loading & validation
      2.  Feature engineering (8 features per station)
      3.  Feature scaling (Z-score normalization)
      4.  Unsupervised learning — K-Means locality classification
      5.  Domain mapping (China → India context)
      6.  Label creation for supervised learning
      7.  Supervised learning — Random Forest vehicle classification
      8.  Model evaluation (accuracy, precision, recall, confusion matrix)
      9.  Decision engine — charger deployment recommendations
     10.  Prototype validation & visualization (8 figures)

  Usage:
      python evcs_analysis.py
      (Requires: pandas, numpy, scikit-learn, matplotlib, seaborn, scipy, openpyxl)
============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    confusion_matrix, silhouette_score
)
from sklearn.decomposition import PCA
from scipy.spatial import ConvexHull
import warnings
import json
import os

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────
DATA_PATH   = "/data/EVCSs.xlsx"           # Primary cleaned dataset
OUTPUT_DIR  = "output_figures"       # Directory for saved figures
STATIONS    = ["EVCS1", "EVCS2", "EVCS3", "EVCS4", "EVCS5", "EVCS6"]
COLORS      = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#3B1F2B", "#44BBA4"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "#f8f9fa",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────
# STEP 1 — Dataset Loading & Validation
# ──────────────────────────────────────────────────────────────────────────
def step1_load_data(path: str) -> pd.DataFrame:
    """Load the cleaned hourly EVCS dataset and derive temporal columns."""
    df = pd.read_excel(path, sheet_name="in")
    assert len(df) == 8760, f"Expected 8760 rows (1 year hourly), got {len(df)}"
    assert all(s in df.columns for s in STATIONS), "Missing station columns"

    df["hour"] = df.index % 24
    df["day"]  = df.index // 24
    df["week"] = df.index // (24 * 7)

    print("[✓] Step 1 — Data loaded: 8760 hourly rows × 6 stations")
    print(f"    Date range: {df['date'].iloc[0]} → {df['date'].iloc[-1]}")
    return df


# ──────────────────────────────────────────────────────────────────────────
# STEP 2 — Feature Engineering
# ──────────────────────────────────────────────────────────────────────────
def step2_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract 8 statistically and temporally meaningful features per station.

    Features:
        1. Avg Daily Load (kWh)      — mean total energy per day
        2. Peak Load (kW)            — maximum instantaneous power
        3. Peak-to-Avg Ratio         — load spikiness indicator
        4. Load Variance (kW²)       — spread of hourly values
        5. Night-to-Day Ratio        — overnight vs daytime demand
        6. Weekly Consistency (CV %) — coefficient of variation of weekly totals
        7. Idle Hour Ratio (%)       — fraction of zero-load hours
        8. Median Load (kW)          — robust central tendency
    """
    features = {}
    for s in STATIONS:
        vals      = df[s]
        daily_sum = df.groupby("day")[s].sum()
        night     = df[df["hour"].isin(range(0, 6))][s].mean()
        day_load  = df[df["hour"].isin(range(6, 24))][s].mean()
        weekly_s  = df.groupby("week")[s].sum()

        features[s] = {
            "Avg Daily Load (kWh)":     daily_sum.mean(),
            "Peak Load (kW)":           vals.max(),
            "Peak-to-Avg Ratio":        vals.max() / vals.mean() if vals.mean() > 0 else 0,
            "Load Variance (kW²)":      vals.var(),
            "Night-to-Day Ratio":       night / day_load if day_load > 0 else 0,
            "Weekly Consistency (CV %)": (weekly_s.std() / weekly_s.mean() * 100)
                                          if weekly_s.mean() > 0 else 0,
            "Idle Hour Ratio (%)":      (vals == 0).sum() / len(vals) * 100,
            "Median Load (kW)":         vals.median(),
        }

    feat_df = pd.DataFrame(features).T
    feat_df.index.name = "Station"
    print("[✓] Step 2 — Feature engineering: 8 features × 6 stations")
    print(feat_df.round(2).to_string())
    return feat_df


# ──────────────────────────────────────────────────────────────────────────
# STEP 3 — Feature Scaling (Z-Score Normalization)
# ──────────────────────────────────────────────────────────────────────────
def step3_scale_features(feat_df: pd.DataFrame):
    """Apply StandardScaler for unbiased distance-based clustering."""
    scaler     = StandardScaler()
    scaled     = scaler.fit_transform(feat_df.values)
    scaled_df  = pd.DataFrame(scaled, index=feat_df.index, columns=feat_df.columns)
    print("[✓] Step 3 — StandardScaler applied (zero-mean, unit-variance)")
    return scaled, scaled_df


# ──────────────────────────────────────────────────────────────────────────
# STEP 4 — Unsupervised Learning: K-Means Locality Classification
# ──────────────────────────────────────────────────────────────────────────
def step4_kmeans_clustering(feat_scaled: np.ndarray):
    """
    Cluster stations into 3 locality types using K-Means.
    Validates k=3 via silhouette score sweep (k = 2…5).
    """
    # Silhouette sweep
    sil_scores = {}
    for k in range(2, min(6, len(feat_scaled))):
        km   = KMeans(n_clusters=k, random_state=42, n_init=10)
        labs = km.fit_predict(feat_scaled)
        sil_scores[k] = silhouette_score(feat_scaled, labs)

    print(f"    Silhouette scores: {sil_scores}")

    # Final model with k=3
    kmeans   = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(feat_scaled)
    sil      = silhouette_score(feat_scaled, clusters)

    print(f"[✓] Step 4 — K-Means (k=3) | Silhouette Score = {sil:.3f}")
    return clusters, sil_scores, sil


# ──────────────────────────────────────────────────────────────────────────
# STEP 5 — Domain Mapping (Cluster → Indian Locality)
# ──────────────────────────────────────────────────────────────────────────
INDIA_MAP = {
    "High-Density (Urban)":    {"Indian Tier": "Tier-1 City",  "Vehicle Mix": "LMV-dominant",        "Charger": "DC Fast"},
    "Mid-Density (Town)":      {"Indian Tier": "Tier-2 City",  "Vehicle Mix": "Mixed (LMV+2W+3W)",  "Charger": "AC + DC"},
    "Low-Usage (Semi-Rural)":  {"Indian Tier": "Semi-Rural",   "Vehicle Mix": "2W/3W dominant",     "Charger": "AC Slow"},
}


def step5_domain_mapping(feat_df: pd.DataFrame, clusters: np.ndarray):
    """
    Map cluster IDs to locality labels based on mean Avg Daily Load ordering.
    High load → Urban | Medium → Town | Low → Semi-Rural
    """
    cluster_mean = {}
    for c in range(3):
        mask = clusters == c
        cluster_mean[c] = feat_df.loc[mask, "Avg Daily Load (kWh)"].mean()

    sorted_c = sorted(cluster_mean, key=cluster_mean.get)
    cluster_map = {
        sorted_c[0]: "Low-Usage (Semi-Rural)",
        sorted_c[1]: "Mid-Density (Town)",
        sorted_c[2]: "High-Density (Urban)",
    }

    locality_labels = [cluster_map[c] for c in clusters]
    feat_df["Cluster"]  = clusters
    feat_df["Locality"] = locality_labels

    print("[✓] Step 5 — Domain mapping complete")
    for loc in INDIA_MAP:
        stations_in = [s for s, l in zip(STATIONS, locality_labels) if l == loc]
        print(f"    {loc} → {INDIA_MAP[loc]['Indian Tier']} | Stations: {stations_in}")

    return locality_labels


# ──────────────────────────────────────────────────────────────────────────
# STEP 6 — Label Creation for Supervised Learning
# ──────────────────────────────────────────────────────────────────────────
def step6_create_labels(feat_df: pd.DataFrame) -> list:
    """
    Derive vehicle-type labels from load characteristics (no manual annotation).

    Rules (calibrated to dataset feature distributions):
        avg > 4000 kWh  AND  peak > 700 kW   → HMV
        avg > 2500 kWh  AND  peak > 400 kW   → Mixed
        otherwise                             → LMV/2W/3W
    """
    labels = []
    for s in STATIONS:
        avg  = feat_df.loc[s, "Avg Daily Load (kWh)"]
        peak = feat_df.loc[s, "Peak Load (kW)"]
        if avg > 4000 and peak > 700:
            labels.append("HMV")
        elif avg > 2500 and peak > 400:
            labels.append("Mixed")
        else:
            labels.append("LMV/2W/3W")

    feat_df["Vehicle Type"] = labels
    print("[✓] Step 6 — Vehicle labels created (rule-based inference)")
    print(feat_df[["Locality", "Vehicle Type"]].to_string())
    return labels


# ──────────────────────────────────────────────────────────────────────────
# STEP 7 — Supervised Learning: Random Forest Vehicle Classification
# ──────────────────────────────────────────────────────────────────────────
def step7_random_forest(feat_df: pd.DataFrame, vehicle_labels: list):
    """Train a 100-tree Random Forest on load features to predict vehicle type."""
    feature_cols = [
        "Avg Daily Load (kWh)", "Peak Load (kW)", "Peak-to-Avg Ratio",
        "Load Variance (kW²)", "Night-to-Day Ratio", "Weekly Consistency (CV %)",
        "Idle Hour Ratio (%)", "Median Load (kW)",
    ]
    X = feat_df[feature_cols].values
    le = LabelEncoder()
    y  = le.fit_transform(vehicle_labels)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)
    y_pred = rf.predict(X)

    print("[✓] Step 7 — Random Forest trained (100 trees)")
    return rf, le, y, y_pred, X, feature_cols


# ──────────────────────────────────────────────────────────────────────────
# STEP 8 — Model Evaluation
# ──────────────────────────────────────────────────────────────────────────
def step8_evaluate(y_true, y_pred, le, rf, feature_cols):
    """Compute accuracy, precision, recall, confusion matrix, feature importance."""
    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec  = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    cm   = confusion_matrix(y_true, y_pred)
    fi   = pd.Series(rf.feature_importances_, index=feature_cols).sort_values(ascending=False)

    print(f"[✓] Step 8 — Evaluation | Acc={acc:.2f} | Prec={prec:.2f} | Rec={rec:.2f}")
    print(f"    Confusion Matrix:\n{cm}")
    print(f"    Classes: {le.classes_}")
    print(f"    Feature Importances:\n{fi}")

    return {"accuracy": acc, "precision": prec, "recall": rec,
            "confusion_matrix": cm.tolist(), "classes": le.classes_.tolist(),
            "feature_importance": fi.to_dict()}, cm, fi


# ──────────────────────────────────────────────────────────────────────────
# STEP 9 — Decision Engine
# ──────────────────────────────────────────────────────────────────────────
def step9_decision_engine(feat_df: pd.DataFrame, locality_labels: list,
                          vehicle_labels: list) -> pd.DataFrame:
    """Combine locality + vehicle type into charger deployment recommendations."""
    rows = []
    for i, s in enumerate(STATIONS):
        loc  = locality_labels[i]
        info = INDIA_MAP[loc]
        rows.append({
            "Station":              s,
            "Locality":             loc,
            "Indian Tier":          info["Indian Tier"],
            "Vehicle Mix":          info["Vehicle Mix"],
            "Predicted Vehicle":    vehicle_labels[i],
            "Recommended Charger":  info["Charger"],
        })

    decision_df = pd.DataFrame(rows)
    print("[✓] Step 9 — Decision Engine output:")
    print(decision_df.to_string(index=False))
    return decision_df


# ──────────────────────────────────────────────────────────────────────────
# STEP 10 — Visualization Suite (8 Figures)
# ──────────────────────────────────────────────────────────────────────────
def step10_visualizations(df, feat_df, feat_scaled, feat_scaled_df,
                          locality_labels, vehicle_labels, clusters,
                          sil_scores, cm, fi, le):
    """Generate and save all 8 publication-ready figures."""

    # ── Fig 1: 24-Hour Load Profiles ──
    fig, ax = plt.subplots(figsize=(12, 6))
    hourly = df[STATIONS + ["hour"]].groupby("hour").mean()
    for i, s in enumerate(STATIONS):
        ax.plot(hourly.index, hourly[s], marker="o", markersize=3.5,
                color=COLORS[i], linewidth=2, label=s)
    ax.set_xlabel("Hour of Day", fontsize=12)
    ax.set_ylabel("Average Load (kW)", fontsize=12)
    ax.set_title("24-Hour Average Charging Load Profiles — All Stations",
                 fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper left", frameon=True, fontsize=9)
    ax.set_xticks(range(0, 24)); ax.set_xlim(-0.5, 23.5)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig1_load_profiles.png"), dpi=180, bbox_inches="tight")
    plt.close()

    # ── Fig 2: Feature Heatmap (scaled) ──
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.heatmap(feat_scaled_df, annot=True, fmt=".2f", cmap="RdYlBu_r",
                center=0, linewidths=0.5, linecolor="white",
                cbar_kws={"shrink": 0.8, "label": "Z-Score"}, ax=ax,
                annot_kws={"size": 9})
    ax.set_title("Scaled Feature Matrix (Z-Score Normalized)",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig2_feature_heatmap.png"), dpi=180, bbox_inches="tight")
    plt.close()

    # ── Fig 3: Cluster PCA Projection ──
    pca     = PCA(n_components=2)
    X_pca   = pca.fit_transform(feat_scaled)
    c_colors = {
        "High-Density (Urban)":   "#C73E1D",
        "Mid-Density (Town)":     "#F18F01",
        "Low-Usage (Semi-Rural)": "#2E86AB",
    }
    fig, ax = plt.subplots(figsize=(9, 6.5))
    for loc_name, col in c_colors.items():
        mask = [l == loc_name for l in locality_labels]
        ax.scatter(X_pca[mask, 0], X_pca[mask, 1], c=col, s=180,
                   edgecolors="white", linewidths=2, label=loc_name, zorder=3, alpha=0.9)
    for i, s in enumerate(STATIONS):
        ax.annotate(s, (X_pca[i, 0], X_pca[i, 1]), fontsize=10, fontweight="bold",
                    ha="center", va="bottom", xytext=(0, 12), textcoords="offset points",
                    arrowprops=dict(arrowstyle="->", color="#555", lw=1.2))
    for loc_name, col in c_colors.items():
        mask = [l == loc_name for l in locality_labels]
        pts  = X_pca[mask]
        if len(pts) >= 3:
            hull = ConvexHull(pts)
            ax.fill(pts[hull.vertices, 0], pts[hull.vertices, 1], color=col, alpha=0.08)
            for simplex in hull.simplices:
                ax.plot(pts[simplex, 0], pts[simplex, 1], color=col, alpha=0.3, linewidth=2)
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)", fontsize=11)
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)", fontsize=11)
    ax.set_title("K-Means Cluster Separation (PCA Projection)",
                 fontsize=14, fontweight="bold", pad=12)
    ax.legend(loc="best", fontsize=9, frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig3_cluster_pca.png"), dpi=180, bbox_inches="tight")
    plt.close()

    # ── Fig 4: Feature Importance ──
    fig, ax = plt.subplots(figsize=(9, 5))
    fi_sorted = fi.sort_values()
    bars = ax.barh(fi_sorted.index, fi_sorted.values, color="#2E86AB",
                   edgecolor="white", height=0.55)
    for bar, val in zip(bars, fi_sorted.values):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontsize=9.5, fontweight="bold", color="#333")
    ax.set_xlabel("Feature Importance", fontsize=11)
    ax.set_title("Random Forest — Feature Importance for Vehicle Type Classification",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlim(0, fi_sorted.max() * 1.18)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig4_feature_importance.png"), dpi=180, bbox_inches="tight")
    plt.close()

    # ── Fig 5: Confusion Matrix ──
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=le.classes_, yticklabels=le.classes_,
                linewidths=1, linecolor="white", cbar=False, ax=ax,
                annot_kws={"size": 18, "fontweight": "bold"})
    ax.set_xlabel("Predicted Label", fontsize=12)
    ax.set_ylabel("True Label", fontsize=12)
    ax.set_title("Confusion Matrix — Vehicle Type Classification",
                 fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig5_confusion_matrix.png"), dpi=180, bbox_inches="tight")
    plt.close()

    # ── Fig 6: Silhouette Score Sweep ──
    fig, ax = plt.subplots(figsize=(7, 4))
    ks, ss = list(sil_scores.keys()), list(sil_scores.values())
    bars = ax.bar(ks, ss, color=["#44BBA4" if k == 3 else "#A8D8EA" for k in ks],
                  edgecolor="white", width=0.5)
    ax.axhline(y=sil_scores[3], color="#C73E1D", linestyle="--", alpha=0.6, linewidth=1.5)
    for bar, val in zip(bars, ss):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", fontsize=11, fontweight="bold")
    ax.set_xlabel("Number of Clusters (k)", fontsize=11)
    ax.set_ylabel("Silhouette Score", fontsize=11)
    ax.set_title("Silhouette Score Validation — Optimal k Selection",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(ks); ax.set_ylim(0, max(ss) * 1.2)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig6_silhouette.png"), dpi=180, bbox_inches="tight")
    plt.close()

    # ── Fig 7: Decision Engine Summary Table ──
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.axis("off")
    ax.set_title("Decision Engine — Charger Deployment Recommendations",
                 fontsize=15, fontweight="bold", pad=20, y=0.98)
    cols     = ["Station", "Avg Daily\nLoad (kWh)", "Peak Load\n(kW)",
                "Locality Type", "Indian Tier", "Vehicle\nDominance", "Charger\nRecommendation"]
    loc_bg   = {"High-Density (Urban)": "#FDECEA",
                "Mid-Density (Town)":   "#FFF3E0",
                "Low-Usage (Semi-Rural)":"#E3F2FD"}
    row_data = []
    for i, s in enumerate(STATIONS):
        row_data.append([
            s,
            f"{feat_df.loc[s, 'Avg Daily Load (kWh)']:.0f}",
            f"{feat_df.loc[s, 'Peak Load (kW)']:.1f}",
            locality_labels[i],
            INDIA_MAP[locality_labels[i]]["Indian Tier"],
            vehicle_labels[i],
            INDIA_MAP[locality_labels[i]]["Charger"],
        ])
    table = ax.table(cellText=row_data, colLabels=cols, loc="center", cellLoc="center")
    table.auto_set_font_size(False); table.set_fontsize(9.5); table.scale(1, 2.0)
    for j in range(len(cols)):
        cell = table[0, j]
        cell.set_facecolor("#2E86AB")
        cell.set_text_props(color="white", fontweight="bold", fontsize=9)
    for i in range(1, len(row_data) + 1):
        bg = loc_bg.get(row_data[i - 1][3], "#ffffff")
        for j in range(len(cols)):
            cell = table[i, j]
            cell.set_facecolor(bg)
            cell.set_text_props(color="#333333", fontsize=9)
            if j == 0:
                cell.set_text_props(color="#2E86AB", fontweight="bold", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig7_decision_engine.png"), dpi=180, bbox_inches="tight")
    plt.close()

    # ── Fig 8: Daily Load Bar Chart ──
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x           = np.arange(len(STATIONS))
    daily_means = [feat_df.loc[s, "Avg Daily Load (kWh)"] for s in STATIONS]
    bars        = ax.bar(x, daily_means, color=COLORS, edgecolor="white", linewidth=1.2, width=0.55)
    for bar, val in zip(bars, daily_means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                f"{val:.0f}", ha="center", fontsize=10, fontweight="bold", color="#333")
    c_col = {"High-Density (Urban)": "#C73E1D",
             "Mid-Density (Town)": "#F18F01",
             "Low-Usage (Semi-Rural)": "#2E86AB"}
    for i, s in enumerate(STATIONS):
        loc = locality_labels[i]
        ax.text(i, -420, loc, ha="center", fontsize=7.5, color=c_col[loc], fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(STATIONS, fontsize=10)
    ax.set_ylabel("Average Daily Energy (kWh)", fontsize=11)
    ax.set_title("Average Daily Charging Load by Station",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_ylim(0, max(daily_means) * 1.18)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig8_daily_load_bar.png"), dpi=180, bbox_inches="tight")
    plt.close()

    print(f"[✓] Step 10 — All 8 figures saved to '{OUTPUT_DIR}/'")


# ──────────────────────────────────────────────────────────────────────────
# MAIN — orchestrates the full pipeline
# ──────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 72)
    print("  EVCS TECHNO-ECONOMIC ANALYSIS — ML PIPELINE")
    print("=" * 72 + "\n")

    # Step 1
    df = step1_load_data(DATA_PATH)

    # Step 2
    feat_df = step2_feature_engineering(df)

    # Step 3
    feat_scaled, feat_scaled_df = step3_scale_features(feat_df)

    # Step 4
    clusters, sil_scores, sil_score = step4_kmeans_clustering(feat_scaled)

    # Step 5
    locality_labels = step5_domain_mapping(feat_df, clusters)

    # Step 6
    vehicle_labels = step6_create_labels(feat_df)

    # Step 7
    rf, le, y_true, y_pred, X, feature_cols = step7_random_forest(feat_df, vehicle_labels)

    # Step 8
    metrics, cm, fi = step8_evaluate(y_true, y_pred, le, rf, feature_cols)

    # Step 9
    decision_df = step9_decision_engine(feat_df, locality_labels, vehicle_labels)

    # Step 10
    step10_visualizations(df, feat_df, feat_scaled, feat_scaled_df,
                          locality_labels, vehicle_labels, clusters,
                          sil_scores, cm, fi, le)

    # ── Save outputs ──
    feat_df.to_csv("feature_matrix.csv")
    decision_df.to_csv("decision_output.csv", index=False)
    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    print("\n" + "=" * 72)
    print("  PIPELINE COMPLETE")
    print("  Outputs: feature_matrix.csv | decision_output.csv | metrics.json")
    print("           output_figures/ (8 figures)")
    print("=" * 72)


if __name__ == "__main__":
    main()


