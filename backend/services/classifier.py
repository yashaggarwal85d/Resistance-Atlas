import numpy as np
import joblib
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent / "ml"
CLASSIFIER_PATH = MODEL_DIR / "classifier.joblib"
ENCODER_PATH = MODEL_DIR / "label_encoder.joblib"

# Antibiotic metadata for display
ANTIBIOTIC_METADATA = {
    "Ampicillin": {
        "class": "Penicillins",
        "resistant_explanation": "This bacterium produces beta-lactamase enzymes that destroy ampicillin before it can act. Ampicillin-class antibiotics will not work.",
        "susceptible_explanation": "Ampicillin should be effective against this infection. Standard dosing applies.",
    },
    "Ciprofloxacin": {
        "class": "Fluoroquinolones",
        "resistant_explanation": "Mutations in DNA gyrase genes prevent ciprofloxacin from binding its target. This antibiotic is predicted to be ineffective.",
        "susceptible_explanation": "Ciprofloxacin is predicted to be effective. A commonly used, well-tolerated option.",
    },
    "Gentamicin": {
        "class": "Aminoglycosides",
        "resistant_explanation": "Aminoglycoside-modifying enzymes detected. Gentamicin will be inactivated before reaching its ribosomal target.",
        "susceptible_explanation": "Gentamicin is predicted to work. Often used for serious infections.",
    },
    "Tetracycline": {
        "class": "Tetracyclines",
        "resistant_explanation": "Efflux pump genes detected that actively expel tetracycline from the bacterial cell.",
        "susceptible_explanation": "Tetracycline is predicted to be effective for this isolate.",
    },
    "Trimethoprim": {
        "class": "Folate inhibitors",
        "resistant_explanation": "Modified DHFR gene detected — trimethoprim can no longer block folate synthesis in this bacterium.",
        "susceptible_explanation": "Trimethoprim should work. Often combined with sulfamethoxazole for enhanced effect.",
    },
    "Chloramphenicol": {
        "class": "Amphenicols",
        "resistant_explanation": "Chloramphenicol acetyltransferase enzyme detected, which inactivates the drug.",
        "susceptible_explanation": "Chloramphenicol is predicted to be active against this isolate.",
    },
    "Meropenem": {
        "class": "Carbapenems",
        "resistant_explanation": "CRITICAL: Carbapenemase genes detected (e.g. NDM, KPC, or OXA-type). This is a last-resort antibiotic and it is predicted to fail. Urgent specialist review required.",
        "susceptible_explanation": "Meropenem (carbapenem) is predicted to be effective. Reserve for severe infections.",
    },
    "Colistin": {
        "class": "Polymyxins",
        "resistant_explanation": "MCR gene or membrane modification detected. Colistin resistance is present — very few treatment options remain.",
        "susceptible_explanation": "Colistin is predicted to be effective. This is a last-resort antibiotic — use only when other options fail.",
    },
}

_classifier = None
_label_encoders = None


def load_model():
    """Load classifier and encoders. Call once at startup."""
    global _classifier, _label_encoders

    if CLASSIFIER_PATH.exists() and ENCODER_PATH.exists():
        _classifier = joblib.load(CLASSIFIER_PATH)
        _label_encoders = joblib.load(ENCODER_PATH)
    else:
        _classifier = None
        _label_encoders = None


def predict_resistance(embedding: np.ndarray) -> list[dict]:
    """
    Run resistance prediction for all antibiotics.
    Returns list of prediction dicts.
    Requires a trained model — run `make download-data && make train-model` first.
    """
    if _classifier is None or _label_encoders is None:
        raise RuntimeError(
            "No trained model found. Run 'make download-data' then 'make train-model' "
            "to train the resistance classifier before analysing sequences."
        )

    results = []
    for antibiotic, encoder in _label_encoders.items():
        proba = _classifier[antibiotic].predict_proba(
            embedding.reshape(1, -1)
        )[0]
        pred_idx = np.argmax(proba)
        prediction = encoder.inverse_transform([pred_idx])[0]
        confidence = float(np.max(proba))
        results.append(_format_result(antibiotic, prediction, confidence))

    return results


def _format_result(antibiotic: str, prediction: str, confidence: float) -> dict:
    """Format a single prediction with metadata."""
    meta = ANTIBIOTIC_METADATA.get(antibiotic, {
        "class": "Unknown class",
        "resistant_explanation": f"This bacterium is predicted to be resistant to {antibiotic}.",
        "susceptible_explanation": f"This bacterium is predicted to be susceptible to {antibiotic}.",
    })

    if prediction == "Resistant":
        explanation = meta["resistant_explanation"]
    else:
        explanation = meta["susceptible_explanation"]

    return {
        "antibiotic": antibiotic,
        "antibiotic_class": meta["class"],
        "prediction": prediction,
        "confidence": round(confidence, 3),
        "explanation": explanation,
    }


def compute_overall_risk(predictions: list[dict]) -> tuple[str, str]:
    """
    Compute an overall risk level from all predictions.
    Returns (risk_level, plain_english_explanation).
    """
    resistant = [p for p in predictions if p["prediction"] == "Resistant"]
    carbapenem_resistant = any(
        p["antibiotic"] == "Meropenem" and p["prediction"] == "Resistant"
        for p in predictions
    )
    colistin_resistant = any(
        p["antibiotic"] == "Colistin" and p["prediction"] == "Resistant"
        for p in predictions
    )
    n_resistant = len(resistant)

    if carbapenem_resistant and colistin_resistant:
        risk = "Critical"
        explanation = (
            "This isolate is predicted to be resistant to both carbapenems and colistin — "
            "the two last-resort antibiotic classes. Very few treatment options remain. "
            "Immediate specialist review and infection control measures are strongly advised."
        )
    elif carbapenem_resistant:
        risk = "High"
        explanation = (
            f"This isolate is predicted to be resistant to {n_resistant} of {len(predictions)} antibiotics tested, "
            "including carbapenems (last-resort antibiotics). "
            "Treatment options are severely limited. Specialist review required."
        )
    elif n_resistant >= 6:
        risk = "High"
        explanation = (
            f"This isolate is predicted to be resistant to {n_resistant} of {len(predictions)} antibiotics tested. "
            "This is consistent with extensively drug-resistant (XDR) status. "
            "Combination therapy or specialist antibiotics may be required."
        )
    elif n_resistant >= 3:
        risk = "Moderate"
        explanation = (
            f"This isolate is predicted to be resistant to {n_resistant} of {len(predictions)} antibiotics tested. "
            "Multiple resistance is present but treatment options remain. "
            "Review susceptible antibiotics for appropriate treatment selection."
        )
    else:
        risk = "Low"
        explanation = (
            f"This isolate shows limited resistance ({n_resistant} of {len(predictions)} antibiotics). "
            "Standard treatment protocols should be effective. Confirm with culture-based testing."
        )

    return risk, explanation
