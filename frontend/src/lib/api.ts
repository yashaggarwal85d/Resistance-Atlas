import axios from "axios";
import { AnalysisResult } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyseSequence(
  sequence: string,
  sequenceName?: string
): Promise<AnalysisResult> {
  const response = await axios.post(
    `${API_BASE}/api/analyse`,
    { sequence, sequence_name: sequenceName },
    { timeout: 180_000 } // 3 min timeout for long sequences
  );
  return response.data;
}

export async function analyseFile(file: File): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("sequence_name", file.name);

  const response = await axios.post(
    `${API_BASE}/api/analyse/file`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 180_000,
    }
  );
  return response.data;
}

export async function checkHealth(): Promise<boolean> {
  try {
    await axios.get(`${API_BASE}/api/health`, { timeout: 5000 });
    return true;
  } catch {
    return false;
  }
}
