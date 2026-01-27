'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AnalysisSectionProps {
  title: string;
  icon: React.ReactNode;
  analysis: Record<string, any> | null;
  color: string;
}

export function AnalysisSection({ title, icon, analysis, color }: AnalysisSectionProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!analysis) return;
    await navigator.clipboard.writeText(JSON.stringify(analysis, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!analysis || analysis.error) {
    return (
      <div className={cn('rounded-lg border p-4', color)}>
        <div className="flex items-center gap-2 text-gray-500">
          {icon}
          <span className="font-medium">{title}</span>
          <span className="text-sm">- No analysis available</span>
        </div>
      </div>
    );
  }

  const renderValue = (value: any): React.ReactNode => {
    if (Array.isArray(value)) {
      return (
        <ul className="list-disc list-inside space-y-1">
          {value.map((item, i) => (
            <li key={i} className="text-gray-700 dark:text-gray-300">
              {typeof item === 'object' ? JSON.stringify(item) : String(item)}
            </li>
          ))}
        </ul>
      );
    }
    if (typeof value === 'object' && value !== null) {
      return (
        <pre className="text-sm bg-gray-50 dark:bg-gray-900 p-2 rounded overflow-x-auto">
          {JSON.stringify(value, null, 2)}
        </pre>
      );
    }
    return <span className="text-gray-700 dark:text-gray-300">{String(value)}</span>;
  };

  return (
    <div className={cn('rounded-lg border overflow-hidden', color)}>
      <div className="flex items-center justify-between p-4 hover:bg-black/5 transition-colors">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 flex-1"
        >
          {icon}
          <span className="font-medium">{title}</span>
        </button>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="p-1 hover:bg-black/10 rounded"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          </button>
          <button onClick={() => setIsExpanded(!isExpanded)}>
            {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="p-4 pt-0 space-y-3">
          {/* Summary first if exists */}
          {analysis.summary && (
            <div className="bg-white/50 dark:bg-black/20 rounded p-3">
              <p className="text-gray-800 dark:text-gray-200">{analysis.summary}</p>
            </div>
          )}

          {/* Other fields */}
          {Object.entries(analysis)
            .filter(([key]) => key !== 'summary' && key !== 'error')
            .map(([key, value]) => (
              <div key={key}>
                <h4 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1 capitalize">
                  {key.replace(/_/g, ' ')}
                </h4>
                {renderValue(value)}
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
