interface SaeFeature {
  feature_name: string;
  activation_strength: number;
  biological_meaning: string;
}

interface Props {
  features: SaeFeature[];
  genomicSummary: string;
}

export default function ExplanationPanel({ features, genomicSummary }: Props) {
  if (!features || features.length === 0) return null;

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4">
      <h3 className="text-sm font-medium text-gray-700 mb-1">
        What Evo 2 found in the genome
      </h3>
      <p className="text-xs text-gray-400 mb-4">
        Genomic features identified by Sparse Autoencoder (SAE) analysis of Evo 2 layer 26 embeddings
      </p>
      <div className="space-y-3">
        {features.map((f, i) => (
          <div key={i} className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-1">
              <div
                className="h-2 rounded-full bg-teal-500"
                style={{ width: `${Math.round(f.activation_strength * 64)}px`, minWidth: "8px", maxWidth: "64px" }}
              />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-700">{f.feature_name}</span>
                <span className="text-xs text-gray-400">
                  activation: {(f.activation_strength * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{f.biological_meaning}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
