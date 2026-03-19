"use client";
import { useAnalysis } from "@/hooks/useAnalysis";
import SequenceInput from "@/components/SequenceInput";
import ResultsDashboard from "@/components/ResultsDashboard";
import LoadingState from "@/components/LoadingState";
import ErrorState from "@/components/ErrorState";
import { Dna, Github } from "lucide-react";

export default function Home() {
  const { state, runAnalysis, runFileAnalysis, reset } = useAnalysis();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Nav */}
      <nav className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Dna className="w-5 h-5 text-teal-600" />
            <span className="font-semibold text-gray-900">ResistanceAtlas</span>
            <span className="text-xs bg-teal-50 text-teal-700 px-2 py-0.5 rounded-full border border-teal-100">
              Powered by Evo 2
            </span>
          </div>
          <a
            href="https://github.com/yourusername/resistanceatlas"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <Github className="w-5 h-5" />
          </a>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 py-10">
        {/* Hero — only shown before analysis */}
        {state.status === "idle" && (
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 text-xs text-teal-700 bg-teal-50 border border-teal-100 px-3 py-1.5 rounded-full mb-5">
              <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-pulse" />
              Open research — works on any bacterial species
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-3">
              Antimicrobial resistance profiling<br className="hidden sm:block" /> in minutes
            </h1>
            <p className="text-gray-500 max-w-xl mx-auto text-sm leading-relaxed">
              Paste a bacterial genome sequence. ResistanceAtlas uses Evo 2 — a foundation model
              trained on 9 trillion base pairs — to predict resistance to 8 antibiotics,
              including carbapenems. Works on novel species that existing tools have never seen.
            </p>
            <div className="flex items-center justify-center gap-6 mt-6 text-xs text-gray-400">
              <span>9 trillion base pairs of training data</span>
              <span>·</span>
              <span>1M token context window</span>
              <span>·</span>
              <span>Zero-shot cross-species prediction</span>
            </div>
          </div>
        )}

        {/* Main content */}
        {state.status === "idle" && (
          <SequenceInput
            onAnalyse={runAnalysis}
            onFileAnalyse={runFileAnalysis}
            isLoading={false}
          />
        )}
        {state.status === "loading" && <LoadingState />}
        {state.status === "error" && (
          <ErrorState
            message={state.message}
            suggestion={state.suggestion}
            onReset={reset}
          />
        )}
        {state.status === "success" && (
          <ResultsDashboard result={state.data} onReset={reset} />
        )}
      </main>

      {/* Footer */}
      <footer className="max-w-4xl mx-auto px-4 py-8 mt-8 border-t border-gray-100">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>ResistanceAtlas — research use only. Not for clinical decision making.</span>
          <span>Built on Evo 2 · Arc Institute · NVIDIA NIM</span>
        </div>
      </footer>
    </div>
  );
}
