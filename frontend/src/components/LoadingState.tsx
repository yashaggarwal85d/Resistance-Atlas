import { Dna } from "lucide-react";

export default function LoadingState() {
  const steps = [
    "Validating DNA sequence...",
    "Sending to Evo 2 (NVIDIA API)...",
    "Extracting genomic embeddings...",
    "Running resistance classifier...",
    "Generating report...",
  ];

  return (
    <div className="w-full max-w-3xl mx-auto text-center py-12">
      <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-teal-50 mb-6">
        <Dna className="w-7 h-7 text-teal-600 animate-spin" style={{ animationDuration: "3s" }} />
      </div>
      <h2 className="text-lg font-medium text-gray-900 mb-2">Analysing your sequence</h2>
      <p className="text-sm text-gray-500 mb-8 max-w-sm mx-auto">
        Evo 2 is reading your genome sequence in full context. This can take 30–90 seconds.
      </p>
      <div className="space-y-2 text-left max-w-xs mx-auto">
        {steps.map((step, i) => (
          <div key={i} className="flex items-center gap-2 text-sm text-gray-500">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-400 flex-shrink-0" />
            {step}
          </div>
        ))}
      </div>
    </div>
  );
}
