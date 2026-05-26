"""
============================================================================
  EVCS TECHNO-ECONOMIC ANALYSIS — End-to-End ML Pipeline
  A Techno-Economical Analysis of Indian EV Charging Infrastructure
============================================================================
  Authors : , Sathvik G, Chaitanya Karthik M, Saireesh Murali G
  Course  : BCSE498J Project-II | SCOPE, VIT
  Date    : April 2026

  Pipeline Steps:
      1.  Dataset loading & validation
      2.  Feature engineering (8 statistical & temporal features per station)
      3.  Feature scaling (Z-score normalization via StandardScaler)
      4.  Unsupervised Model Selection — Comparative clustering (K-Means, Hierarchical, GMM)
      5.  Domain mapping (Clusters → Indian Tier Context)
      6.  Label creation for supervised learning (Rule-based inference)
      7.  Supervised Model Selection — Comparative classification (RF, SVM, GBM, Neural Network) using LOOCV
      8.  Comprehensive Evaluation — (Silhouette, Davies-Bouldin, F1-Score, Confusion Matrix)
      9.  Hybrid Decision Engine — Charger deployment recommendations powered by winning models
     10.  Prototype validation & Visualization Suite (Performance comparisons & Decision matrices)

  Usage:
      python evcs_analysis.py
      (Requires: pandas, numpy, scikit-learn, matplotlib, seaborn, scipy, openpyxl)
============================================================================
"""



"""
EVCS Comprehensive ML Analysis
Multiple Unsupervised & Supervised Models with Realistic Performance Metrics
"""
# ============================================================================
# DOMAIN CONFIGURATION (INDIAN CONTEXT)
# ============================================================================
INDIA_MAP = {
    "High-Density (Urban)":    {"Indian Tier": "Tier-1 City",  "Vehicle Mix": "HMV/LMV-dominant", "Charger": "DC Fast (150kW+)"},
    "Mid-Density (Town)":      {"Indian Tier": "Tier-2 City",  "Vehicle Mix": "Mixed (LMV+2W+3W)", "Charger": "AC (22kW) + DC (50kW)"},
    "Low-Usage (Semi-Rural)":  {"Indian Tier": "Semi-Rural",   "Vehicle Mix": "2W/3W dominant",    "Charger": "AC Slow (7.4kW)"},
}
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix, classification_report,
                             silhouette_score, davies_bouldin_score, calinski_harabasz_score)

# Unsupervised Learning
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture

# Supervised Learning
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility but allow some variance
np.random.seed(42)

print("="*80)
print("EVCS COMPREHENSIVE MACHINE LEARNING ANALYSIS")
print("Multiple Models | Realistic Metrics | Complete Comparison")
print("="*80)

# ============================================================================
# STEP 1: DATA LOADING & FEATURE ENGINEERING
# ============================================================================
print("\n[STEP 1] Loading Data & Feature Engineering...")

# Load data
# Load data
# Load data
# Load data using the Absolute Path
# Load data from the data folder
df = pd.read_excel('data/EVCSs.xlsx', sheet_name='in')
stations = ['EVCS1', 'EVCS2', 'EVCS3', 'EVCS4', 'EVCS5', 'EVCS6']

def extract_features(station_data):
    """Extract 8 features from hourly load data"""
    features = {}
    
    # Feature 1: Average Daily Load (kWh)
    daily_totals = [station_data[i:i+24].sum() for i in range(0, len(station_data), 24)]
    features['Avg_Daily_Load'] = np.mean(daily_totals)
    
    # Feature 2: Peak Load (kW)
    features['Peak_Load'] = station_data.max()
    
    # Feature 3: Peak-to-Average Ratio
    features['Peak_to_Avg_Ratio'] = features['Peak_Load'] / station_data.mean()
    
    # Feature 4: Load Variance
    features['Load_Variance'] = station_data.var()
    
    # Feature 5: Night-to-Day Ratio (0-5am vs 6-23pm)
    night_hours = station_data[station_data.index % 24 < 6]
    day_hours = station_data[station_data.index % 24 >= 6]
    features['Night_to_Day_Ratio'] = night_hours.mean() / day_hours.mean()
    
    # Feature 6: Weekly Consistency (Coefficient of Variation %)
    weekly_loads = [station_data[i:i+168].sum() for i in range(0, len(station_data), 168)]
    features['Weekly_Consistency'] = (np.std(weekly_loads) / np.mean(weekly_loads)) * 100
    
    # Feature 7: Idle Hour Ratio (% of time with zero load)
    features['Idle_Hour_Ratio'] = (station_data == 0).sum() / len(station_data) * 100
    
    # Feature 8: Median Load
    features['Median_Load'] = station_data.median()
    
    return features

# Extract features for all stations
feature_data = []
for station in stations:
    features = extract_features(df[station])
    features['Station'] = station
    feature_data.append(features)

features_df = pd.DataFrame(feature_data)
print(f"\n✓ Extracted 8 features for {len(stations)} stations")
print(f"\nFeature Statistics:")
print(features_df.drop('Station', axis=1).describe().round(2))

# ============================================================================
# STEP 2: FEATURE SCALING
# ============================================================================
print("\n[STEP 2] Feature Scaling...")

feature_cols = [col for col in features_df.columns if col != 'Station']
X = features_df[feature_cols].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"✓ Features scaled using StandardScaler (Z-score normalization)")
print(f"  Shape: {X_scaled.shape}")

# ============================================================================
# STEP 3: UNSUPERVISED LEARNING (3 MODELS)
# ============================================================================
print("\n" + "="*80)
print("[STEP 3] UNSUPERVISED LEARNING - CLUSTERING ANALYSIS")
print("="*80)

clustering_results = {}

# ------------------------------------------------------------------------
# MODEL 1: K-Means Clustering
# ------------------------------------------------------------------------
print("\n[MODEL 1] K-Means Clustering (k=3)...")

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans_labels = kmeans.fit_predict(X_scaled)

# Metrics
kmeans_silhouette = silhouette_score(X_scaled, kmeans_labels)
kmeans_davies_bouldin = davies_bouldin_score(X_scaled, kmeans_labels)
kmeans_calinski = calinski_harabasz_score(X_scaled, kmeans_labels)

clustering_results['K-Means'] = {
    'labels': kmeans_labels,
    'silhouette': kmeans_silhouette,
    'davies_bouldin': kmeans_davies_bouldin,
    'calinski_harabasz': kmeans_calinski
}

print(f"  Silhouette Score: {kmeans_silhouette:.4f} (higher is better, range: -1 to 1)")
print(f"  Davies-Bouldin Index: {kmeans_davies_bouldin:.4f} (lower is better)")
print(f"  Calinski-Harabasz Index: {kmeans_calinski:.2f} (higher is better)")
print(f"  Cluster Distribution: {np.bincount(kmeans_labels)}")

# ------------------------------------------------------------------------
# MODEL 2: Hierarchical Clustering (Agglomerative)
# ------------------------------------------------------------------------
print("\n[MODEL 2] Hierarchical Clustering (Agglomerative, linkage=ward)...")

hierarchical = AgglomerativeClustering(n_clusters=3, linkage='ward')
hierarchical_labels = hierarchical.fit_predict(X_scaled)

# Metrics
hier_silhouette = silhouette_score(X_scaled, hierarchical_labels)
hier_davies_bouldin = davies_bouldin_score(X_scaled, hierarchical_labels)
hier_calinski = calinski_harabasz_score(X_scaled, hierarchical_labels)

clustering_results['Hierarchical'] = {
    'labels': hierarchical_labels,
    'silhouette': hier_silhouette,
    'davies_bouldin': hier_davies_bouldin,
    'calinski_harabasz': hier_calinski
}

print(f"  Silhouette Score: {hier_silhouette:.4f}")
print(f"  Davies-Bouldin Index: {hier_davies_bouldin:.4f}")
print(f"  Calinski-Harabasz Index: {hier_calinski:.2f}")
print(f"  Cluster Distribution: {np.bincount(hierarchical_labels)}")

# ------------------------------------------------------------------------
# MODEL 3: Gaussian Mixture Model (GMM)
# ------------------------------------------------------------------------
print("\n[MODEL 3] Gaussian Mixture Model (n_components=3)...")

gmm = GaussianMixture(n_components=3, random_state=42, covariance_type='full')
gmm_labels = gmm.fit_predict(X_scaled)

# Metrics
gmm_silhouette = silhouette_score(X_scaled, gmm_labels)
gmm_davies_bouldin = davies_bouldin_score(X_scaled, gmm_labels)
gmm_calinski = calinski_harabasz_score(X_scaled, gmm_labels)
gmm_bic = gmm.bic(X_scaled)
gmm_aic = gmm.aic(X_scaled)

clustering_results['GMM'] = {
    'labels': gmm_labels,
    'silhouette': gmm_silhouette,
    'davies_bouldin': gmm_davies_bouldin,
    'calinski_harabasz': gmm_calinski,
    'bic': gmm_bic,
    'aic': gmm_aic
}

print(f"  Silhouette Score: {gmm_silhouette:.4f}")
print(f"  Davies-Bouldin Index: {gmm_davies_bouldin:.4f}")
print(f"  Calinski-Harabasz Index: {gmm_calinski:.2f}")
print(f"  BIC (Bayesian Information Criterion): {gmm_bic:.2f} (lower is better)")
print(f"  AIC (Akaike Information Criterion): {gmm_aic:.2f} (lower is better)")
print(f"  Cluster Distribution: {np.bincount(gmm_labels)}")

# ============================================================================
# STEP 4: SELECT BEST CLUSTERING FOR LABEL CREATION
# ============================================================================
print("\n[STEP 4] Selecting Best Clustering Model...")

# Use K-Means as baseline (best silhouette score typically)
best_clustering = 'K-Means'
cluster_labels = kmeans_labels

print(f"✓ Selected: {best_clustering} for supervised learning labels")

# Map clusters to demand levels (High, Medium, Low)
# Cluster with highest peak load = High demand
cluster_peak_loads = {}
for cluster_id in range(3):
    mask = cluster_labels == cluster_id
    cluster_stations = features_df[mask]
    cluster_peak_loads[cluster_id] = cluster_stations['Peak_Load'].mean()

# Sort clusters by peak load
sorted_clusters = sorted(cluster_peak_loads.items(), key=lambda x: x[1], reverse=True)
cluster_mapping = {
    sorted_clusters[0][0]: 0,  # High demand -> 0
    sorted_clusters[1][0]: 2,  # Medium demand -> 2  
    sorted_clusters[2][0]: 1   # Low demand -> 1
}

# Create supervised labels based on clustering + load characteristics
# Use clustering to inform vehicle type assignment
def assign_vehicle_type_v2(idx, row, cluster):
    """Assign vehicle type based on clustering and load characteristics"""
    peak = row['Peak_Load']
    idle_ratio = row['Idle_Hour_Ratio']
    
    # Determine thresholds based on data quartiles
    peak_high = features_df['Peak_Load'].quantile(0.67)  # Top 33%
    peak_low = features_df['Peak_Load'].quantile(0.33)   # Bottom 33%
    
    # High demand cluster + high peak load = HMV
    if peak > peak_high and idle_ratio < 10:
        return 0  # HMV
    # Low demand cluster OR low peak load = LMV/2W/3W
    elif peak < peak_low or idle_ratio > 10:
        return 1  # LMV/2W/3W
    # Everything in between = Mixed
    else:
        return 2  # Mixed

# Apply classification
vehicle_types = []
for idx, row in features_df.iterrows():
    cluster = cluster_labels[idx]
    vtype = assign_vehicle_type_v2(idx, row, cluster)
    vehicle_types.append(vtype)

features_df['Vehicle_Type'] = vehicle_types
y_true = np.array(vehicle_types)

print("\nVehicle Type Distribution:")
print(f"  HMV (0): {(y_true == 0).sum()} stations")
print(f"  LMV/2W/3W (1): {(y_true == 1).sum()} stations")
print(f"  Mixed (2): {(y_true == 2).sum()} stations")

# ============================================================================
# STEP 5: SUPERVISED LEARNING (4 MODELS)
# ============================================================================
print("\n" + "="*80)
print("[STEP 5] SUPERVISED LEARNING - CLASSIFICATION")
print("="*80)

# For small dataset, use Leave-One-Out Cross-Validation
from sklearn.model_selection import LeaveOneOut, cross_validate

print(f"\nUsing Leave-One-Out Cross-Validation (LOOCV) due to small dataset size")
print(f"Each of {len(X_scaled)} stations will be tested individually\n")

classification_results = {}
loo = LeaveOneOut()

# Store all predictions for overall confusion matrix
all_y_true = []
all_predictions = {}

# ------------------------------------------------------------------------
# MODEL 1: Random Forest
# ------------------------------------------------------------------------
print("\n[MODEL 1] Random Forest (n_estimators=100)...")

rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=4)

# LOOCV evaluation
cv_results = cross_validate(rf, X_scaled, y_true, cv=loo, 
                            scoring=['accuracy', 'precision_weighted', 
                                    'recall_weighted', 'f1_weighted'],
                            return_train_score=False)

rf_acc = cv_results['test_accuracy'].mean()
rf_prec = cv_results['test_precision_weighted'].mean()
rf_rec = cv_results['test_recall_weighted'].mean()
rf_f1 = cv_results['test_f1_weighted'].mean()
rf_std = cv_results['test_accuracy'].std()

# Fit on full data for predictions
rf.fit(X_scaled, y_true)
rf_pred = rf.predict(X_scaled)

classification_results['Random Forest'] = {
    'accuracy': rf_acc,
    'precision': rf_prec,
    'recall': rf_rec,
    'f1_score': rf_f1,
    'accuracy_std': rf_std,
    'predictions': rf_pred,
    'model': rf
}

all_predictions['Random Forest'] = rf_pred

print(f"  Accuracy: {rf_acc:.4f} ± {rf_std:.4f}")
print(f"  Precision: {rf_prec:.4f}")
print(f"  Recall: {rf_rec:.4f}")
print(f"  F1-Score: {rf_f1:.4f}")
print(f"  LOOCV Std Dev: {rf_std:.4f}")

# ------------------------------------------------------------------------
# MODEL 2: Support Vector Machine (SVM)
# ------------------------------------------------------------------------
print("\n[MODEL 2] Support Vector Machine (kernel=rbf)...")

svm = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)

# LOOCV evaluation
cv_results = cross_validate(svm, X_scaled, y_true, cv=loo,
                            scoring=['accuracy', 'precision_weighted',
                                    'recall_weighted', 'f1_weighted'],
                            return_train_score=False)

svm_acc = cv_results['test_accuracy'].mean()
svm_prec = cv_results['test_precision_weighted'].mean()
svm_rec = cv_results['test_recall_weighted'].mean()
svm_f1 = cv_results['test_f1_weighted'].mean()
svm_std = cv_results['test_accuracy'].std()

# Fit on full data
svm.fit(X_scaled, y_true)
svm_pred = svm.predict(X_scaled)

classification_results['SVM'] = {
    'accuracy': svm_acc,
    'precision': svm_prec,
    'recall': svm_rec,
    'f1_score': svm_f1,
    'accuracy_std': svm_std,
    'predictions': svm_pred,
    'model': svm
}

all_predictions['SVM'] = svm_pred

print(f"  Accuracy: {svm_acc:.4f} ± {svm_std:.4f}")
print(f"  Precision: {svm_prec:.4f}")
print(f"  Recall: {svm_rec:.4f}")
print(f"  F1-Score: {svm_f1:.4f}")
print(f"  LOOCV Std Dev: {svm_std:.4f}")

# ------------------------------------------------------------------------
# MODEL 3: Gradient Boosting (XGBoost-style)
# ------------------------------------------------------------------------
print("\n[MODEL 3] Gradient Boosting (n_estimators=100, learning_rate=0.1)...")

gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, 
                                max_depth=3, random_state=42)

# LOOCV evaluation
cv_results = cross_validate(gb, X_scaled, y_true, cv=loo,
                            scoring=['accuracy', 'precision_weighted',
                                    'recall_weighted', 'f1_weighted'],
                            return_train_score=False)

gb_acc = cv_results['test_accuracy'].mean()
gb_prec = cv_results['test_precision_weighted'].mean()
gb_rec = cv_results['test_recall_weighted'].mean()
gb_f1 = cv_results['test_f1_weighted'].mean()
gb_std = cv_results['test_accuracy'].std()

# Fit on full data
gb.fit(X_scaled, y_true)
gb_pred = gb.predict(X_scaled)

classification_results['Gradient Boosting'] = {
    'accuracy': gb_acc,
    'precision': gb_prec,
    'recall': gb_rec,
    'f1_score': gb_f1,
    'accuracy_std': gb_std,
    'predictions': gb_pred,
    'model': gb
}

all_predictions['Gradient Boosting'] = gb_pred

print(f"  Accuracy: {gb_acc:.4f} ± {gb_std:.4f}")
print(f"  Precision: {gb_prec:.4f}")
print(f"  Recall: {gb_rec:.4f}")
print(f"  F1-Score: {gb_f1:.4f}")
print(f"  LOOCV Std Dev: {gb_std:.4f}")

# ------------------------------------------------------------------------
# MODEL 4: Neural Network (Multi-Layer Perceptron)
# ------------------------------------------------------------------------
print("\n[MODEL 4] Neural Network MLP (hidden_layers=(50,30))...")

mlp = MLPClassifier(hidden_layer_sizes=(50, 30), activation='relu', 
                    solver='adam', max_iter=500, random_state=42, 
                    early_stopping=False)

# LOOCV evaluation
cv_results = cross_validate(mlp, X_scaled, y_true, cv=loo,
                            scoring=['accuracy', 'precision_weighted',
                                    'recall_weighted', 'f1_weighted'],
                            return_train_score=False)

mlp_acc = cv_results['test_accuracy'].mean()
mlp_prec = cv_results['test_precision_weighted'].mean()
mlp_rec = cv_results['test_recall_weighted'].mean()
mlp_f1 = cv_results['test_f1_weighted'].mean()
mlp_std = cv_results['test_accuracy'].std()

# Fit on full data
mlp.fit(X_scaled, y_true)
mlp_pred = mlp.predict(X_scaled)

classification_results['Neural Network'] = {
    'accuracy': mlp_acc,
    'precision': mlp_prec,
    'recall': mlp_rec,
    'f1_score': mlp_f1,
    'accuracy_std': mlp_std,
    'predictions': mlp_pred,
    'model': mlp
}

all_predictions['Neural Network'] = mlp_pred

print(f"  Accuracy: {mlp_acc:.4f} ± {mlp_std:.4f}")
print(f"  Precision: {mlp_prec:.4f}")
print(f"  Recall: {mlp_rec:.4f}")
print(f"  F1-Score: {mlp_f1:.4f}")
print(f"  LOOCV Std Dev: {mlp_std:.4f}")

# ============================================================================
# STEP 6: COMPREHENSIVE COMPARISON
# ============================================================================
print("\n" + "="*80)
print("[STEP 6] MODEL COMPARISON & ANALYSIS")
print("="*80)

# Clustering Comparison Table
print("\n" + "-"*80)
print("UNSUPERVISED LEARNING - CLUSTERING COMPARISON")
print("-"*80)
print(f"{'Model':<20} {'Silhouette':<15} {'Davies-Bouldin':<15} {'Calinski-Harabasz':<15}")
print("-"*80)
for model_name, results in clustering_results.items():
    print(f"{model_name:<20} {results['silhouette']:<15.4f} "
          f"{results['davies_bouldin']:<15.4f} {results['calinski_harabasz']:<15.2f}")
print("-"*80)
print("Interpretation:")
print("  • Silhouette Score: Higher is better (range -1 to 1, >0.5 is good)")
print("  • Davies-Bouldin: Lower is better (measures cluster separation)")
print("  • Calinski-Harabasz: Higher is better (ratio of between/within cluster variance)")

# Classification Comparison Table
print("\n" + "-"*80)
print("SUPERVISED LEARNING - CLASSIFICATION COMPARISON")
print("-"*80)
print(f"{'Model':<20} {'Accuracy':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
print("-"*80)
for model_name, results in classification_results.items():
    print(f"{model_name:<20} {results['accuracy']:.4f}±{results['accuracy_std']:.4f}   "
          f"{results['precision']:<12.4f} {results['recall']:<12.4f} "
          f"{results['f1_score']:<12.4f}")
print("-"*80)

# Best models
best_clustering = max(clustering_results.items(), 
                     key=lambda x: x[1]['silhouette'])
best_classification = max(classification_results.items(), 
                         key=lambda x: x[1]['f1_score'])

print(f"\n✓ Best Clustering Model: {best_clustering[0]} "
      f"(Silhouette: {best_clustering[1]['silhouette']:.4f})")
print(f"✓ Best Classification Model: {best_classification[0]} "
      f"(F1-Score: {best_classification[1]['f1_score']:.4f})")

# ============================================================================
# STEP 7: DETAILED METRICS FOR BEST CLASSIFIER
# ============================================================================
print("\n" + "="*80)
print(f"[STEP 7] DETAILED METRICS - {best_classification[0]}")
print("="*80)

best_model_name = best_classification[0]
best_predictions = classification_results[best_model_name]['predictions']

# Class-wise metrics (use full dataset predictions)
class_names = ['HMV', 'LMV/2W/3W', 'Mixed']
print("\nClassification Report (on full dataset):")
print(classification_report(y_true, best_predictions, target_names=class_names, zero_division=0))

# Confusion Matrix
cm = confusion_matrix(y_true, best_predictions)
print("\nConfusion Matrix:")
print(f"{'':>15} {'Predicted HMV':>15} {'Predicted LMV':>15} {'Predicted Mixed':>15}")
for i, class_name in enumerate(class_names):
    print(f"{'Actual ' + class_name:<15} {cm[i,0]:>15} {cm[i,1]:>15} {cm[i,2]:>15}")

# ============================================================================
# STEP 7.5: HYBRID DECISION ENGINE (BUSINESS CONCLUSIONS)
# ============================================================================
print("\n" + "="*80)
print("[STEP 7.5] HYBRID DECISION ENGINE - INFRASTRUCTURE RECOMMENDATIONS")
print("="*80)

# 1. Get the labels from the BEST clustering model
best_cluster_labels = clustering_results[best_clustering[0]]['labels']

# 2. Map clusters to Locality Types based on Avg Daily Load
cluster_means = {}
for c in range(3):
    mask = best_cluster_labels == c
    cluster_means[c] = features_df.loc[mask, 'Avg_Daily_Load'].mean()

sorted_c = sorted(cluster_means, key=cluster_means.get)
cluster_map = {
    sorted_c[0]: "Low-Usage (Semi-Rural)",
    sorted_c[1]: "Mid-Density (Town)",
    sorted_c[2]: "High-Density (Urban)",
}
locality_labels = [cluster_map[c] for c in best_cluster_labels]

# 3. Get predictions from the BEST classification model
best_preds_numeric = classification_results[best_classification[0]]['predictions']
pred_mapping = {0: 'HMV', 1: 'LMV/2W/3W', 2: 'Mixed'}
final_vehicle_preds = [pred_mapping[p] for p in best_preds_numeric]

# 4. Generate the Final Decision DataFrame
decision_rows = []
for i, s in enumerate(stations):
    loc = locality_labels[i]
    info = INDIA_MAP[loc]
    decision_rows.append({
        "Station": s,
        "Locality": loc,
        "Indian Tier": info["Indian Tier"],
        "ML Predicted Vehicle": final_vehicle_preds[i],
        "Recommended Charger": info["Charger"]
    })

decision_df = pd.DataFrame(decision_rows)
print(f"\nFinal Infrastructure Plan based on winning models ({best_clustering[0]} & {best_classification[0]}):")
print("-" * 80)
print(decision_df.to_string(index=False))
print("-" * 80)

# Save the actionable output
decision_df.to_csv('output_figures/final_decision_plan.csv', index=False)

# ============================================================================
# STEP 8: VISUALIZATIONS
# ============================================================================
print("\n[STEP 8] Generating Visualizations...")

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Figure 1: Clustering Comparison
fig1, axes = plt.subplots(1, 3, figsize=(18, 5))

for idx, (model_name, results) in enumerate(clustering_results.items()):
    ax = axes[idx]
    scatter = ax.scatter(X_scaled[:, 0], X_scaled[:, 1], 
                        c=results['labels'], cmap='viridis', 
                        s=200, alpha=0.6, edgecolors='black', linewidth=1.5)
    ax.set_title(f'{model_name}\nSilhouette: {results["silhouette"]:.3f}', 
                fontsize=12, fontweight='bold')
    ax.set_xlabel('Feature 1 (Standardized)', fontsize=10)
    ax.set_ylabel('Feature 2 (Standardized)', fontsize=10)
    plt.colorbar(scatter, ax=ax)

plt.tight_layout()
plt.savefig('output_figures/clustering_comparison.png', dpi=300, bbox_inches='tight')
print("  ✓ clustering_comparison.png")

# Figure 2: Classification Performance Comparison
fig2, ax = plt.subplots(figsize=(12, 6))

metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
x = np.arange(len(metrics))
width = 0.2

for idx, (model_name, results) in enumerate(classification_results.items()):
    values = [results['accuracy'], results['precision'], 
              results['recall'], results['f1_score']]
    ax.bar(x + idx*width, values, width, label=model_name, alpha=0.8)

ax.set_xlabel('Metrics', fontsize=12, fontweight='bold')
ax.set_ylabel('Score', fontsize=12, fontweight='bold')
ax.set_title('Classification Models Performance Comparison', fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(metrics)
ax.legend(loc='lower right', fontsize=10)
ax.set_ylim(0, 1.1)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('output_figures/classification_comparison.png', dpi=300, bbox_inches='tight')
print("  ✓ classification_comparison.png")

# Figure 3: Confusion Matrix for Best Model
fig3, ax = plt.subplots(figsize=(8, 7))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=class_names, yticklabels=class_names,
            cbar_kws={'label': 'Count'}, ax=ax, 
            annot_kws={'size': 14, 'weight': 'bold'})
ax.set_title(f'Confusion Matrix - {best_model_name}', fontsize=14, fontweight='bold')
ax.set_ylabel('Actual Class', fontsize=12, fontweight='bold')
ax.set_xlabel('Predicted Class', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('output_figures/confusion_matrix_best.png', dpi=300, bbox_inches='tight')
print("  ✓ confusion_matrix_best.png")

# Figure 4: Model Ranking
fig4, ax = plt.subplots(figsize=(10, 6))

model_names = list(classification_results.keys())
f1_scores = [results['f1_score'] for results in classification_results.values()]

colors = ['#2ecc71' if score == max(f1_scores) else '#3498db' for score in f1_scores]
bars = ax.barh(model_names, f1_scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_xlabel('F1-Score', fontsize=12, fontweight='bold')
ax.set_title('Classification Models Ranked by F1-Score', fontsize=14, fontweight='bold')
ax.set_xlim(0, 1.0)
ax.grid(axis='x', alpha=0.3)



# Add value labels
for bar, score in zip(bars, f1_scores):
    ax.text(score + 0.02, bar.get_y() + bar.get_height()/2, 
            f'{score:.4f}', va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('output_figures/model_ranking_f1.png', dpi=300, bbox_inches='tight')
print("  ✓ model_ranking_f1.png")

# Figure 5: Decision Engine Summary Table (From Code 1)
fig5, ax = plt.subplots(figsize=(14, 5))
ax.axis("off")
ax.set_title(f"Decision Engine Recommendations (Powered by {best_classification[0]})",
             fontsize=15, fontweight="bold", pad=20, y=0.98)

cols = ["Station", "Locality Type", "Indian Tier", "ML Predicted\nVehicle", "Charger\nRecommendation"]
loc_bg = {"High-Density (Urban)": "#FDECEA", "Mid-Density (Town)": "#FFF3E0", "Low-Usage (Semi-Rural)":"#E3F2FD"}

row_data = []
for i, row in decision_df.iterrows():
    row_data.append([row["Station"], row["Locality"], row["Indian Tier"], row["ML Predicted Vehicle"], row["Recommended Charger"]])
    
table = ax.table(cellText=row_data, colLabels=cols, loc="center", cellLoc="center")
table.auto_set_font_size(False); table.set_fontsize(10); table.scale(1, 2.0)

for j in range(len(cols)):
    cell = table[0, j]
    cell.set_facecolor("#2E86AB")
    cell.set_text_props(color="white", fontweight="bold", fontsize=10)
    
for i in range(1, len(row_data) + 1):
    bg = loc_bg.get(row_data[i - 1][1], "#ffffff")
    for j in range(len(cols)):
        cell = table[i, j]
        cell.set_facecolor(bg)
        
plt.tight_layout()
plt.savefig('output_figures/fig5_decision_engine.png', dpi=300, bbox_inches="tight")
print("  ✓ fig5_decision_engine.png")

print("\n✓ All visualizations saved to output_figures/")


# ============================================================================
# STEP 9: SAVE RESULTS
# ============================================================================
print("\n[STEP 9] Saving Results...")

# Clustering results
clustering_df = pd.DataFrame({
    'Model': list(clustering_results.keys()),
    'Silhouette_Score': [r['silhouette'] for r in clustering_results.values()],
    'Davies_Bouldin_Index': [r['davies_bouldin'] for r in clustering_results.values()],
    'Calinski_Harabasz_Score': [r['calinski_harabasz'] for r in clustering_results.values()]
})
clustering_df.to_csv('output_figures/clustering_results.csv', index=False)
print("  ✓ clustering_results.csv")

# Classification results
classification_df = pd.DataFrame({
    'Model': list(classification_results.keys()),
    'Accuracy': [r['accuracy'] for r in classification_results.values()],
    'Accuracy_Std': [r['accuracy_std'] for r in classification_results.values()],
    'Precision': [r['precision'] for r in classification_results.values()],
    'Recall': [r['recall'] for r in classification_results.values()],
    'F1_Score': [r['f1_score'] for r in classification_results.values()]
})
classification_df.to_csv('output_figures/classification_results.csv', index=False)
print("  ✓ classification_results.csv")

# Feature importance from Random Forest
feature_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': classification_results['Random Forest']['model'].feature_importances_
}).sort_values('Importance', ascending=False)
feature_importance.to_csv('output_figures/feature_importance.csv', index=False)
print("  ✓ feature_importance.csv")

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print(f"\n✓ Total Models Evaluated: {len(clustering_results)} Clustering + {len(classification_results)} Classification")
print(f"✓ Best Clustering: {best_clustering[0]}")
print(f"✓ Best Classification: {best_classification[0]} (F1: {best_classification[1]['f1_score']:.4f})")
print(f"\n✓ All results saved to: output_figures/")