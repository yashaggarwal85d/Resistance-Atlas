import { AntibioticResult } from "@/lib/types";
import clsx from "clsx";

interface Props {
  result: AntibioticResult;
}

export default function AntibioticCard({ result }: Props) {
  const isResistant = result.prediction === "Resistant";
  const confidencePct = Math.round(result.confidence * 100);

  return (
    <div
      className={clsx(
        "rounded-xl border p-4 transition-all",
        isResistant
          ? "border-red-100 bg-red-50"
          : "border-emerald-100 bg-emerald-50"
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-medium text-gray-900 text-sm">{result.antibiotic}</h3>
            <span className="text-xs text-gray-400 bg-white border border-gray-100 px-2 py-0.5 rounded-full">
              {result.antibiotic_class}
            </span>
          </div>
          <p className="text-xs text-gray-600 mt-1.5 leading-relaxed">
            {result.explanation}
          </p>
        </div>
        <div className="flex-shrink-0 text-right">
          <div
            className={clsx(
              "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold",
              isResistant
                ? "bg-red-100 text-red-700"
                : "bg-emerald-100 text-emerald-700"
            )}
          >
            {result.prediction}
          </div>
          <div className="text-xs text-gray-400 mt-1">{confidencePct}% confidence</div>
        </div>
      </div>
    </div>
  );
}
