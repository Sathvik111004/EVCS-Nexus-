"""
ML Model Export Script
Saves trained models for integration with FastAPI backend
"""

import pickle
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingClassifier

print("="*80)
print("ML MODEL EXPORT FOR FULL-STACK INTEGRATION")
print("="*80)

# Load your data (same as your main script)
df = pd.read_excel('../data/EVCSs.xlsx', sheet_name='in')
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
    
    # Feature 5: Night-to-Day Ratio
    night_hours = station_data[station_data.index % 24 < 6]
    day_hours = station_data[station_data.index % 24 >= 6]
    features['Night_to_Day_Ratio'] = night_hours.mean() / day_hours.mean()
    
    # Feature 6: Weekly Consistency
    weekly_loads = [station_data[i:i+168].sum() for i in range(0, len(station_data), 168)]
    features['Weekly_Consistency'] = (np.std(weekly_loads) / np.mean(weekly_loads)) * 100
    
    # Feature 7: Idle Hour Ratio
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
feature_cols = [col for col in features_df.columns if col != 'Station']
X = features_df[feature_cols].values

# Train scaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train K-Means (best clustering model)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans_labels = kmeans.fit_predict(X_scaled)

# Create labels for supervised learning (same logic as your script)
def assign_vehicle_type_v2(idx, row, cluster):
    peak = row['Peak_Load']
    idle_ratio = row['Idle_Hour_Ratio']
    peak_high = features_df['Peak_Load'].quantile(0.67)
    peak_low = features_df['Peak_Load'].quantile(0.33)
    
    if peak > peak_high and idle_ratio < 10:
        return 0  # HMV
    elif peak < peak_low or idle_ratio > 10:
        return 1  # LMV/2W/3W
    else:
        return 2  # Mixed

vehicle_types = []
for idx, row in features_df.iterrows():
    cluster = kmeans_labels[idx]
    vtype = assign_vehicle_type_v2(idx, row, cluster)
    vehicle_types.append(vtype)

y_true = np.array(vehicle_types)

# Train Gradient Boosting (best classification model)
gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, 
                                max_depth=3, random_state=42)
gb.fit(X_scaled, y_true)

# Create cluster mapping (for locality inference)
cluster_means = {}
for c in range(3):
    mask = kmeans_labels == c
    cluster_means[c] = features_df.loc[mask, 'Avg_Daily_Load'].mean()

sorted_c = sorted(cluster_means, key=cluster_means.get)
cluster_to_locality = {
    sorted_c[0]: "Low-Usage (Semi-Rural)",
    sorted_c[1]: "Mid-Density (Town)",
    sorted_c[2]: "High-Density (Urban)",
}

# ============================================================================
# SAVE ALL MODELS AND MAPPINGS
# ============================================================================

print("\n[STEP 1] Saving Models...")
os.makedirs('models', exist_ok=True)
# Save StandardScaler
with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("  ✓ scaler.pkl saved")

# Save K-Means model
with open('models/kmeans_model.pkl', 'wb') as f:
    pickle.dump(kmeans, f)
print("  ✓ kmeans_model.pkl saved")

# Save Gradient Boosting model
with open('models/gradient_boosting_model.pkl', 'wb') as f:
    pickle.dump(gb, f)
print("  ✓ gradient_boosting_model.pkl saved")

# Save cluster to locality mapping
with open('models/cluster_to_locality.pkl', 'wb') as f:
    pickle.dump(cluster_to_locality, f)
print("  ✓ cluster_to_locality.pkl saved")

# Save feature column names (important for consistency)
with open('models/feature_columns.pkl', 'wb') as f:
    pickle.dump(feature_cols, f)
print("  ✓ feature_columns.pkl saved")

# Save cluster means for reference
with open('models/cluster_means.pkl', 'wb') as f:
    pickle.dump(cluster_means, f)
print("  ✓ cluster_means.pkl saved")

print("\n" + "="*80)
print("MODEL EXPORT COMPLETE!")
print("="*80)
print("\nSaved models:")
print("  • scaler.pkl - StandardScaler for feature normalization")
print("  • kmeans_model.pkl - K-Means clustering (Silhouette: 0.30)")
print("  • gradient_boosting_model.pkl - Gradient Boosting (F1: 0.67)")
print("  • cluster_to_locality.pkl - Cluster → Locality mapping")
print("  • feature_columns.pkl - Feature name order")
print("  • cluster_means.pkl - Cluster statistics")
print("\nNext step: Copy these models to backend/models/ directory")
print("="*80)
