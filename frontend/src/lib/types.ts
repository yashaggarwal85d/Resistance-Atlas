export interface AntibioticResult {
  antibiotic: string;
  antibiotic_class: string;
  prediction: "Resistant" | "Susceptible";
  confidence: number;
  explanation: string;
}

export interface SaeFeature {
  feature_name: string;
  activation_strength: number;
  biological_meaning: string;
}

export interface AnalysisResult {
  sequence_name: string;
  sequence_length: number;
  overall_risk: "Critical" | "High" | "Moderate" | "Low";
  risk_explanation: string;
  antibiotics: AntibioticResult[];
  sae_features: SaeFeature[];
  genomic_summary: string;
  processing_time_seconds: number;
  model_version: string;
}

export type AnalysisState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: AnalysisResult }
  | { status: "error"; message: string; suggestion: string };
