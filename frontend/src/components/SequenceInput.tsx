"use client";
import { useState, useRef, DragEvent } from "react";
import { Upload, FlaskConical, ChevronRight } from "lucide-react";
import clsx from "clsx";

interface Props {
  onAnalyse: (sequence: string, name?: string) => void;
  onFileAnalyse: (file: File) => void;
  isLoading: boolean;
}

const SAMPLE_SEQUENCE = `>Klebsiella_pneumoniae_NDM1_example
ATGGAGAAAAAAATCACTGGATATACCACCGTTGATATATCCCAATGGCATCGTAAAGAACATTTTGAGGCATTTCAGTCAGTTGCTCAATGTACCTATAA
CCAGACCGTTCAGCTGGATATTACGGCCTTTTTAAAGACCGTAAAGAAAAATAAGCACAAGTTTTATCCGGCCTTTATTCACATTCTTGCCCGCCTGATG
AATGCTCATCCGGAATTCGTATGGCAATGAAAGACGGTGAGCTGGTGATATGGGATAGTGTTCACCCTTGTTACACCGTTTTCCATGAGCAAACTGAAAC`;

export default function SequenceInput({ onAnalyse, onFileAnalyse, isLoading }: Props) {
  const [sequence, setSequence] = useState("");
  const [sequenceName, setSequenceName] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    if (!sequence.trim()) return;
    onAnalyse(sequence.trim(), sequenceName || undefined);
  };

  const handleFile = (file: File) => {
    if (!file) return;
    onFileAnalyse(file);
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-4">
      {/* Name input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Sample name <span className="text-gray-400 font-normal">(optional)</span>
        </label>
        <input
          type="text"
          value={sequenceName}
          onChange={(e) => setSequenceName(e.target.value)}
          placeholder="e.g. Patient isolate 2024-03-19"
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
        />
      </div>

      {/* Sequence textarea */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          DNA sequence{" "}
          <span className="text-gray-400 font-normal">
            (paste raw sequence or FASTA format)
          </span>
        </label>
        <textarea
          value={sequence}
          onChange={(e) => setSequence(e.target.value)}
          placeholder={`Paste your DNA sequence here...\n\nExamples:\n• Raw: ATGGAGAAAATCACT...\n• FASTA: >sample_name\n  ATGGAGAAAATCACT...`}
          rows={8}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent resize-y"
        />
        <div className="flex justify-between mt-1">
          <span className="text-xs text-gray-400">
            {sequence.length > 0 ? `${sequence.replace(/[^ATGCNatgcn]/g, "").length.toLocaleString()} bases` : "Min 100 bases"}
          </span>
          <button
            onClick={() => setSequence(SAMPLE_SEQUENCE)}
            className="text-xs text-teal-600 hover:text-teal-700 underline"
          >
            Load sample sequence
          </button>
        </div>
      </div>

      {/* File drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={clsx(
          "border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors",
          isDragging ? "border-teal-400 bg-teal-50" : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
        )}
      >
        <Upload className="w-5 h-5 text-gray-400 mx-auto mb-2" />
        <p className="text-sm text-gray-500">
          Drop a <span className="font-medium">.fasta</span> file here, or{" "}
          <span className="text-teal-600 underline">browse</span>
        </p>
        <p className="text-xs text-gray-400 mt-1">Supports .fasta .fa .fna .txt</p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".fasta,.fa,.fna,.txt"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
      </div>

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={!sequence.trim() || isLoading}
        className={clsx(
          "w-full flex items-center justify-center gap-2 py-3 px-6 rounded-lg font-medium transition-all",
          sequence.trim() && !isLoading
            ? "bg-teal-600 text-white hover:bg-teal-700 active:scale-[0.99]"
            : "bg-gray-100 text-gray-400 cursor-not-allowed"
        )}
      >
        <FlaskConical className="w-4 h-4" />
        {isLoading ? "Analysing with Evo 2..." : "Analyse resistance profile"}
        {!isLoading && <ChevronRight className="w-4 h-4" />}
      </button>
    </div>
  );
}
