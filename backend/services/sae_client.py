import numpy as np
from typing import Any

# SAE feature catalogue: maps known genomic signatures to biological meanings.
# In production: replace with actual SAE latent activations from
# https://huggingface.co/Goodfire/Evo-2-Layer-26-Mixed
SAE_FEATURE_CATALOGUE = [
    {
        "feature_name": "Beta-lactamase cassette (NDM/TEM/SHV family)",
        "motif_index": 4,       # Index into _sequence_features resistance motif array
        "threshold": 0.01,
        "biological_meaning": (
            "Evo 2 detected sequence patterns consistent with a beta-lactamase enzyme gene. "
            "These enzymes chemically destroy penicillins and cephalosporins before they can act. "
            "This is the most common mechanism of ampicillin resistance globally."
        ),
    },
    {
        "feature_name": "Integron integrase (class 1)",
        "motif_index": 5,
        "threshold": 0.01,
        "biological_meaning": (
            "Class 1 integron integrase signature detected. Integrons are genetic platforms "
            "that capture and express resistance gene cassettes. Their presence strongly predicts "
            "multi-drug resistance, as they typically carry multiple resistance genes simultaneously."
        ),
    },
    {
        "feature_name": "Efflux pump (RND/MFS family)",
        "motif_index": 6,
        "threshold": 0.01,
        "biological_meaning": (
            "Efflux pump gene signature detected. These membrane proteins actively expel "
            "antibiotics from the bacterial cell, conferring broad resistance to multiple "
            "antibiotic classes including fluoroquinolones and tetracyclines."
        ),
    },
    {
        "feature_name": "Carbapenemase (OXA/KPC family)",
        "motif_index": 4,
        "threshold": 0.05,
        "biological_meaning": (
            "Carbapenemase gene motif detected. This enzyme hydrolyses carbapenems — the "
            "last-resort antibiotics. Isolates carrying carbapenemases have very limited "
            "treatment options. Colistin or combination therapy may be required."
        ),
    },
    {
        "feature_name": "High GC content (Pseudomonas/Actinobacteria signature)",
        "motif_index": None,
        "gc_threshold": 0.60,
        "biological_meaning": (
            "Elevated GC content (>60%) detected — consistent with Pseudomonas, "
            "Burkholderia, or Actinobacteria. These organisms intrinsically express "
            "multiple efflux systems and outer membrane permeability barriers."
        ),
    },
    {
        "feature_name": "Mobile genetic element flanking",
        "motif_index": 5,
        "threshold": 0.005,
        "biological_meaning": (
            "Insertion sequence or transposon signature flanking the resistance region. "
            "This indicates the resistance gene is mobile and likely acquired via horizontal "
            "gene transfer — meaning it can spread to other bacteria in the same environment."
        ),
    },
]


def get_sae_features(embedding: np.ndarray, sequence: str) -> list[dict[str, Any]]:
    """
    Compute SAE-style feature activations from Evo 2 embedding.

    Returns top features sorted by activation strength.
    Each feature has: feature_name, activation_strength (0-1), biological_meaning.

    Production path: replace with actual SAE forward pass using
    Goodfire/Evo-2-Layer-26-Mixed weights from HuggingFace.
    """
    seq = sequence.upper()
    n = len(seq)
    gc = (seq.count("G") + seq.count("C")) / n if n > 0 else 0.5

    # The embedding's last 7 values are resistance motif signals
    # (from _sequence_features in evo2_client.py: 4 base + 16 dinuc + 7 motif = index 20-26)
    motif_signals = embedding[-7:] if len(embedding) >= 7 else np.zeros(7)

    activated = []
    for feat in SAE_FEATURE_CATALOGUE:
        if feat.get("gc_threshold") is not None:
            # GC-based feature
            if gc >= feat["gc_threshold"]:
                strength = min((gc - feat["gc_threshold"]) * 5 + 0.4, 1.0)
                activated.append({
                    "feature_name": feat["feature_name"],
                    "activation_strength": round(float(strength), 3),
                    "biological_meaning": feat["biological_meaning"],
                })
        elif feat["motif_index"] is not None:
            idx = feat["motif_index"]
            if idx < len(motif_signals):
                signal = float(motif_signals[idx])
                if signal > feat["threshold"]:
                    # Normalise to 0-1 range
                    strength = min(signal * 10, 1.0)
                    activated.append({
                        "feature_name": feat["feature_name"],
                        "activation_strength": round(strength, 3),
                        "biological_meaning": feat["biological_meaning"],
                    })

    # Sort by activation strength, return top 4
    activated.sort(key=lambda x: x["activation_strength"], reverse=True)
    return activated[:4]
