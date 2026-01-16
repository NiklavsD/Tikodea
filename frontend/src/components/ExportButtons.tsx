'use client';

import { useState } from 'react';
import { Download, Copy, Check, FileCode } from 'lucide-react';
import { Video } from '@/lib/api';
import { cn } from '@/lib/utils';

interface ExportButtonsProps {
  video: Video;
}

export function ExportButtons({ video }: ExportButtonsProps) {
  const [copiedAll, setCopiedAll] = useState(false);

  const generateMarkdown = (): string => {
    const sections = [
      `# ${video.title || 'Untitled Video'}`,
      '',
      `**Source:** ${video.tiktok_url}`,
      `**Creator:** @${video.creator || 'Unknown'}`,
      `**Processed:** ${video.processed_at || video.created_at}`,
      video.context ? `**Context:** ${video.context}` : null,
      '',
      '## Metadata',
      '',
      `- Views: ${video.view_count?.toLocaleString() || 'N/A'}`,
      `- Likes: ${video.like_count?.toLocaleString() || 'N/A'}`,
      `- Hashtags: ${video.hashtags.map((h) => `#${h}`).join(' ') || 'None'}`,
      '',
      '## Transcript',
      '',
      video.transcript || '_No transcript available_',
      '',
    ];

    if (video.investment_analysis && !video.investment_analysis.error) {
      sections.push(
        '## Investment Analysis',
        '',
        `**Summary:** ${video.investment_analysis.summary || 'N/A'}`,
        '',
        '```json',
        JSON.stringify(video.investment_analysis, null, 2),
        '```',
        ''
      );
    }

    if (video.product_analysis && !video.product_analysis.error) {
      sections.push(
        '## Product Analysis',
        '',
        `**Summary:** ${video.product_analysis.summary || 'N/A'}`,
        '',
        '```json',
        JSON.stringify(video.product_analysis, null, 2),
        '```',
        ''
      );
    }

    if (video.content_analysis && !video.content_analysis.error) {
      sections.push(
        '## Content Analysis',
        '',
        `**Summary:** ${video.content_analysis.summary || 'N/A'}`,
        '',
        '```json',
        JSON.stringify(video.content_analysis, null, 2),
        '```',
        ''
      );
    }

    if (video.knowledge_analysis && !video.knowledge_analysis.error) {
      sections.push(
        '## Knowledge Analysis',
        '',
        `**Summary:** ${video.knowledge_analysis.summary || 'N/A'}`,
        '',
        '```json',
        JSON.stringify(video.knowledge_analysis, null, 2),
        '```',
        ''
      );
    }

    return sections.filter(Boolean).join('\n');
  };

  const generateClaudeCodePlan = (): string => {
    const insights = [];

    if (video.product_analysis?.problem_solved) {
      insights.push(`- Problem: ${video.product_analysis.problem_solved}`);
    }
    if (video.product_analysis?.solution_approach) {
      insights.push(`- Solution: ${video.product_analysis.solution_approach}`);
    }
    if (video.knowledge_analysis?.actionable_insights) {
      const actionable = video.knowledge_analysis.actionable_insights;
      if (Array.isArray(actionable)) {
        actionable.forEach((item: string) => insights.push(`- ${item}`));
      } else {
        insights.push(`- ${actionable}`);
      }
    }

    return `# Implementation Plan

## Source
- TikTok: ${video.tiktok_url}
- Context: ${video.context || 'General research'}

## Key Insights

${insights.join('\n') || '- No specific insights extracted'}

## Product Summary

${video.product_analysis?.summary || 'No product analysis available'}

## Suggested Next Steps

1. Research market and competition
2. Define MVP scope
3. Create technical specification
4. Build prototype

## Notes

${video.knowledge_analysis?.summary || 'See full analysis in dashboard'}

---
*Generated from Tikodea on ${new Date().toISOString().split('T')[0]}*
`;
  };

  const handleCopyAll = async () => {
    await navigator.clipboard.writeText(generateMarkdown());
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 2000);
  };

  const handleDownloadMarkdown = () => {
    const content = generateMarkdown();
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tikodea-${video.id}-${video.title?.slice(0, 30).replace(/[^a-z0-9]/gi, '-') || 'export'}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadClaudePlan = () => {
    const content = generateClaudeCodePlan();
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `plan-${video.id}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={handleCopyAll}
        className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm"
      >
        {copiedAll ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
        {copiedAll ? 'Copied!' : 'Copy All'}
      </button>

      <button
        onClick={handleDownloadMarkdown}
        className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm"
      >
        <Download className="w-4 h-4" />
        Export Markdown
      </button>

      <button
        onClick={handleDownloadClaudePlan}
        className="flex items-center gap-2 px-3 py-2 bg-primary-100 hover:bg-primary-200 text-primary-700 rounded-lg transition-colors text-sm"
      >
        <FileCode className="w-4 h-4" />
        Claude Code Plan
      </button>
    </div>
  );
}
