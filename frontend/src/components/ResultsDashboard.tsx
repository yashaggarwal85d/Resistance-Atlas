"use client";
import { AnalysisResult } from "@/lib/types";
import AntibioticCard from "./AntibioticCard";
import ResistanceChart from "./ResistanceChart";
import ExplanationPanel from "./ExplanationPanel";
import clsx from "clsx";
import { Clock, Dna, AlertTriangle, CheckCircle, XCircle } from "lucide-react";

interface Props {
  result: AnalysisResult;
  onReset: () => void;
}

const RISK_CONFIG = {
  Critical: { color: "bg-red-600 text-white", icon: XCircle, border: "border-red-200 bg-red-50" },
  High:     { color: "bg-orange-500 text-white", icon: AlertTriangle, border: "border-orange-200 bg-orange-50" },
  Moderate: { color: "bg-yellow-500 text-white", icon: AlertTriangle, border: "border-yellow-200 bg-yellow-50" },
  Low:      { color: "bg-emerald-500 text-white", icon: CheckCircle, border: "border-emerald-200 bg-emerald-50" },
};

export default function ResultsDashboard({ result, onReset }: Props) {
  const config = RISK_CONFIG[result.overall_risk as keyof typeof RISK_CONFIG] || RISK_CONFIG.Moderate;
  const Icon = config.icon;
  const resistantCount = result.antibiotics.filter((a) => a.prediction === "Resistant").length;

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6">

      {/* Header bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">{result.sequence_name}</h2>
          <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Dna className="w-3 h-3" />
              {result.sequence_length.toLocaleString()} bp
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {result.processing_time_seconds}s
            </span>
            <span>Model: {result.model_version}</span>
          </div>
        </div>
        <button
          onClick={onReset}
          className="text-sm text-teal-600 hover:text-teal-700 underline"
        >
          Analyse another
        </button>
      </div>

      {/* Overall risk banner */}
      <div className={clsx("rounded-xl border p-4", config.border)}>
        <div className="flex items-start gap-3">
          <span className={clsx("inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold flex-shrink-0", config.color)}>
            <Icon className="w-3.5 h-3.5" />
            {result.overall_risk} Risk
          </span>
          <p className="text-sm text-gray-700 leading-relaxed">{result.risk_explanation}</p>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-gray-50 rounded-xl p-4 text-center border border-gray-100">
          <div className="text-2xl font-semibold text-red-600">{resistantCount}</div>
          <div className="text-xs text-gray-500 mt-1">Antibiotics resistant to</div>
        </div>
        <div className="bg-gray-50 rounded-xl p-4 text-center border border-gray-100">
          <div className="text-2xl font-semibold text-emerald-600">
            {result.antibiotics.length - resistantCount}
          </div>
          <div className="text-xs text-gray-500 mt-1">Antibiotics still effective</div>
        </div>
        <div className="bg-gray-50 rounded-xl p-4 text-center border border-gray-100">
          <div className="text-2xl font-semibold text-gray-800">
            {Math.round(
              (result.antibiotics.reduce((s, a) => s + a.confidence, 0) /
                result.antibiotics.length) *
                100
            )}%
          </div>
          <div className="text-xs text-gray-500 mt-1">Mean confidence</div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white rounded-xl border border-gray-100 p-4">
        <h3 className="text-sm font-medium text-gray-700 mb-4">
          Resistance profile — confidence by antibiotic
        </h3>
        <ResistanceChart antibiotics={result.antibiotics} />
        <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-red-400 inline-block" /> Resistant</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-emerald-500 inline-block" /> Susceptible</span>
          <span>Bar length = prediction confidence</span>
        </div>
      </div>

      {/* Antibiotic cards */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">
          Detailed results — {result.antibiotics.length} antibiotics tested
        </h3>
        <div className="space-y-2">
          {[...result.antibiotics]
            .sort((a, b) => {
              if (a.prediction === b.prediction) return 0;
              return a.prediction === "Resistant" ? -1 : 1;
            })
            .map((ab) => (
              <AntibioticCard key={ab.antibiotic} result={ab} />
            ))}
        </div>
      </div>

      {/* SAE interpretability features */}
      {result.sae_features && result.sae_features.length > 0 && (
        <ExplanationPanel
          features={result.sae_features}
          genomicSummary={result.genomic_summary}
        />
      )}

      {/* Genomic summary */}
      <div className="bg-gray-50 rounded-xl border border-gray-100 p-4">
        <h3 className="text-sm font-medium text-gray-700 mb-2">How this was analysed</h3>
        <p className="text-xs text-gray-500 leading-relaxed">{result.genomic_summary}</p>
      </div>

      {/* Disclaimer */}
      <div className="text-xs text-gray-400 leading-relaxed border-t border-gray-100 pt-4">
        <strong>Research use only.</strong> ResistanceAtlas predictions are for research purposes.
        Clinical treatment decisions must be confirmed with culture-based susceptibility testing
        and reviewed by qualified medical professionals.
      </div>
    </div>
  );
}
