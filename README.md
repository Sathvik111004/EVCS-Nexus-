# ⚡ EVCS Nexus — EV Charging Infrastructure Planning System

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![Scikit-Learn](https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)

**EVCS Nexus** is a premium, machine-learning-driven infrastructure planning system specifically calibrated for the Indian EV charging ecosystem. The platform transforms raw, hourly station-charging logs into strategic, data-backed deployment insights—bridging the gap between raw data science and real-world commercial viability.

---

## 🚀 Core Features

- 📈 **End-to-End ML Pipeline (`evcs_analysis.py`):**
  - **Feature Engineering:** Extracts 8 temporal and load features (e.g., peak-to-average ratio, load variance, night-to-day ratio, idle hours) from raw hourly datasets.
  - **Unsupervised K-Means Clustering:** Groups stations into three distinct locality archetypes (Urban, Town, Semi-Rural), mathematically validated via silhouette scores.
  - **Domain Mapping:** Contextualizes clusters into specific Indian demographic tiers (Tiers 1, 2, and 3).
  - **Supervised Random Forest Classifier:** Trains a 100-tree classifier to predict vehicle fleet dominance (e.g., HMV, LMV, or Mixed fleets) based on load profiles.
- ⚙️ **Robust Techno-Economic Engine (FastAPI):**
  - Instant calculations in **INR** for **CAPEX** (chargers, installation, grid load upgrades) and **OPEX** (annual energy and maintenance fees).
  - Accurate financial returns (revenues, absolute profit, ROI %, payback period) and **ESG Impact metrics** (tonnes of CO2 avoided, equivalent petrol saved).
  - *Robust JSON Compliance:* Built-in fail-safes for unprofitable scenarios, preventing server serialization crashes.
- 🖥️ **Interactive Planning Dashboard (React + Vite):**
  - Sleek, modern interface using TailwindCSS and Framer Motion for smooth micro-animations.
  - What-if scenario modeling with real-time charting via Recharts.

---

## 🛠️ Tech Stack

### Backend & ML Core
- **FastAPI / Uvicorn** — High-performance ASGI web framework.
- **Scikit-Learn (1.5.2)** — Model training (K-Means, Random Forest) and scaling.
- **Pandas & NumPy** — Data manipulation and statistical feature extraction.

### Frontend
- **React (18) + Vite** — High-performance frontend toolchain.
- **TailwindCSS** — Fully responsive utility-first CSS styling.
- **Recharts** — Dynamic SVG-rendered analytics charts.
- **Axios** — Seamless HTTP communication with the backend API.

---

## 📥 Setup and Installation

### 1. Prerequisite Checklist
Ensure you have the following installed:
- Python 3.11+
- Node.js v18+ & npm

### 2. Backend Installation & Run
```bash
# Navigate to the backend directory
cd backend

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the dependencies
pip install -r requirements.txt

# Start the FastAPI server
python3 main.py
```
The backend server runs locally on **`http://127.0.0.1:8000`**.

### 3. Frontend Installation & Run
```bash
# Navigate to the frontend directory
cd frontend

# Install package dependencies
npm install

# Start the Vite development server
npm run dev
```
Open **`http://localhost:3000`** in your browser to access the dashboard interface.

---

## 📊 Analytical Pipeline Execution
If you wish to re-run the ML data pipeline and regenerate the publication-ready visualizations:
```bash
# In the repository root
python3 evcs_analysis.py
```
Outputs are generated in:
- `feature_matrix.csv` & `decision_output.csv`
- `metrics.json`
- `output_figures/` (contains 8 generated `.png` analytical charts)

---

## 🤝 Project Developers
- **Chaitanya Karthik M**
- **Saireesh Murali G**
- **Sathvik G**
*VIT Chennai - SCOPE (BCSE498J Project-II | February 2026)*
