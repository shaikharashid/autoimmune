import joblib
import pandas as pd
import shap
import numpy as np

# Load the saved model and scaler
rf_model = joblib.load("models/autoimmune_rf_model.pkl")
scaler = joblib.load("models/scaler.pkl")

# Correct feature order — must match training data exactly
FEATURE_COLUMNS = [
    "Age", "Gender", "ESR", "CRP", "RF", "Anti_CCP", "HLA_B27",
    "ANA", "Anti_Ro", "Anti_La", "Anti_dsDNA", "Anti_Sm",
    "C3", "C4", "ASCA", "Anti_CBir1", "Anti_OmpC", "pANCA",
    "EMA", "DGP", "Anti_tTG", "Anti_TPO", "Anti_SMA"
]

# Columns that need scaling (same as notebook)
scale_cols = ["Age", "ESR", "CRP", "C3", "C4"]

# SHAP explainer
explainer = shap.TreeExplainer(rf_model)

def predict(data: dict):
    # Convert incoming data to a DataFrame with correct column order
    df = pd.DataFrame([data])[FEATURE_COLUMNS]

    # Scale the necessary columns
    df[scale_cols] = scaler.transform(df[scale_cols])

    # Make prediction
    prediction_index = int(rf_model.predict(df)[0])

    # Disease names
    disease_classes = [
        "Ankylosing Spondylitis",
        "Celiac disease",
        "Crohn's disease",
        "Multiple sclerosis",
        "Normal",
        "Psoriatic Arthritis",
        "Reactive Arthritis",
        "Rheumatoid Arthritis",
        "Sjogren's Syndrome",
        "Systemic Lupus Erythematosus"
    ]

    prediction = disease_classes[prediction_index]

    # Get confidence percentage
    probabilities = rf_model.predict_proba(df)[0]
    confidence = round(float(np.max(probabilities)) * 100, 2)

    # Get SHAP values
    shap_values = explainer.shap_values(df)

    if isinstance(shap_values, list):
        shap_array = shap_values[prediction_index][0]
    else:
        shap_array = shap_values[0, :, prediction_index]

    shap_dict = dict(zip(df.columns.tolist(), shap_array.tolist()))
    top_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

    return {
        "disease": prediction,
        "confidence": float(confidence),
        "top_features": [
            {"feature": str(k), "impact": round(float(v), 4)}
            for k, v in top_features
        ]
    }