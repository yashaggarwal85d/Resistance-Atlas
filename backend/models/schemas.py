from pydantic import BaseModel, field_validator
from typing import Optional

class AnalyseRequest(BaseModel):
    sequence: str           # Raw input — may contain FASTA headers
    sequence_name: Optional[str] = "Unknown isolate"

    @field_validator("sequence")
    @classmethod
    def validate_sequence(cls, v: str) -> str:
        # Validate but preserve original input (including FASTA headers)
        # so that parse_fasta() in the router can extract the name.
        lines = v.strip().splitlines()
        seq_lines = [l for l in lines if not l.startswith(">")]
        sequence = "".join(seq_lines).upper().replace(" ", "").replace("\n", "")

        if len(sequence) < 100:
            raise ValueError("Sequence too short. Minimum 100 bases required.")
        if len(sequence) > 1_000_000:
            raise ValueError("Sequence too long. Maximum 1,000,000 bases.")

        invalid = set(sequence) - set("ATGCNRYSWKMBDHV")
        if invalid:
            raise ValueError(f"Invalid characters in sequence: {invalid}")

        return v.strip()    # Return original text, not stripped sequence

class AntibioticResult(BaseModel):
    antibiotic: str
    antibiotic_class: str
    prediction: str          # "Resistant" | "Susceptible"
    confidence: float        # 0.0 - 1.0
    explanation: str         # Plain English

class SaeFeature(BaseModel):
    feature_name: str
    activation_strength: float   # 0.0 - 1.0
    biological_meaning: str

class AnalyseResponse(BaseModel):
    sequence_name: str
    sequence_length: int
    overall_risk: str        # "Critical" | "High" | "Moderate" | "Low"
    risk_explanation: str
    antibiotics: list[AntibioticResult]
    sae_features: list[SaeFeature]   # Top interpretability features
    genomic_summary: str
    processing_time_seconds: float
    model_version: str = "evo2-40b"

class ErrorResponse(BaseModel):
    error: str
    detail: str
    suggestion: str
