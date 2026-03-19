import { AlertCircle } from "lucide-react";

interface Props {
  message: string;
  suggestion: string;
  onReset: () => void;
}

export default function ErrorState({ message, suggestion, onReset }: Props) {
  return (
    <div className="w-full max-w-3xl mx-auto text-center py-12">
      <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-red-50 mb-6">
        <AlertCircle className="w-7 h-7 text-red-500" />
      </div>
      <h2 className="text-lg font-medium text-gray-900 mb-2">{message}</h2>
      <p className="text-sm text-gray-500 mb-6 max-w-sm mx-auto">{suggestion}</p>
      <button
        onClick={onReset}
        className="px-5 py-2.5 bg-gray-900 text-white text-sm rounded-lg hover:bg-gray-800 transition-colors"
      >
        Try again
      </button>
    </div>
  );
}
