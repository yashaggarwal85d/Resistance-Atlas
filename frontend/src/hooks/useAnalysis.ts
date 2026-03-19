import { useState } from "react";
import { AnalysisState } from "@/lib/types";
import { analyseSequence, analyseFile } from "@/lib/api";

export function useAnalysis() {
  const [state, setState] = useState<AnalysisState>({ status: "idle" });

  const runAnalysis = async (sequence: string, name?: string) => {
    setState({ status: "loading" });
    try {
      const data = await analyseSequence(sequence, name);
      setState({ status: "success", data });
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setState({
        status: "error",
        message: detail?.error || "Analysis failed",
        suggestion:
          detail?.suggestion ||
          "Check your sequence and try again. Contact support if the problem persists.",
      });
    }
  };

  const runFileAnalysis = async (file: File) => {
    setState({ status: "loading" });
    try {
      const data = await analyseFile(file);
      setState({ status: "success", data });
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setState({
        status: "error",
        message: detail?.error || "File analysis failed",
        suggestion:
          detail?.suggestion || "Ensure the file is a valid FASTA file.",
      });
    }
  };

  const reset = () => setState({ status: "idle" });

  return { state, runAnalysis, runFileAnalysis, reset };
}
