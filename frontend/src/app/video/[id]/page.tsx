'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Heart,
  ExternalLink,
  Eye,
  ThumbsUp,
  Tag,
  Loader2,
  TrendingUp,
  Package,
  Film,
  BookOpen,
} from 'lucide-react';
import { fetchVideo, toggleFavorite, Video } from '@/lib/api';
import { formatDate, formatNumber, cn } from '@/lib/utils';
import { AnalysisSection } from '@/components/AnalysisSection';
import { ChatInterface } from '@/components/ChatInterface';
import { ExportButtons } from '@/components/ExportButtons';
import { TagEditor } from '@/components/TagEditor';

export default function VideoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const videoId = Number(params.id);

  const [video, setVideo] = useState<Video | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchVideo(videoId)
      .then(setVideo)
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [videoId]);

  const handleFavorite = async () => {
    if (!video) return;
    try {
      await toggleFavorite(video.id, !video.is_favorite);
      setVideo({ ...video, is_favorite: !video.is_favorite });
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const handleTagsChange = async () => {
    try {
      const updatedVideo = await fetchVideo(videoId);
      setVideo(updatedVideo);
    } catch (error) {
      console.error('Failed to refresh video:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  if (error || !video) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-red-500">{error || 'Video not found'}</p>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center gap-2 sm:gap-4">
            <button
              onClick={() => router.back()}
              className="p-2 min-w-[44px] min-h-[44px] flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors flex-shrink-0"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-base sm:text-xl font-semibold truncate flex-1 min-w-0">
              {video.title || 'Untitled Video'}
            </h1>
            <button
              onClick={handleFavorite}
              className={cn(
                'p-2 min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg transition-colors flex-shrink-0',
                video.is_favorite
                  ? 'text-red-500 bg-red-50 dark:bg-red-900/20'
                  : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
              )}
            >
              <Heart className={cn('w-5 h-5', video.is_favorite && 'fill-current')} />
            </button>
            <a
              href={video.tiktok_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 min-w-[44px] min-h-[44px] flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors flex-shrink-0"
            >
              <ExternalLink className="w-5 h-5" />
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Video Info */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            {video.thumbnail_url && (
              <img
                src={video.thumbnail_url}
                alt={video.title || 'Video thumbnail'}
                className="w-full sm:w-32 h-48 sm:h-32 object-cover rounded-lg flex-shrink-0"
              />
            )}
            <div className="flex-1 min-w-0">
              {video.creator && (
                <p className="text-gray-600 dark:text-gray-400">@{video.creator}</p>
              )}
              {video.description && (
                <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">
                  {video.description}
                </p>
              )}
              <div className="flex flex-wrap items-center gap-3 sm:gap-4 mt-3 text-sm text-gray-500">
                {video.view_count !== null && (
                  <span className="flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    {formatNumber(video.view_count)}
                  </span>
                )}
                {video.like_count !== null && (
                  <span className="flex items-center gap-1">
                    <ThumbsUp className="w-4 h-4" />
                    {formatNumber(video.like_count)}
                  </span>
                )}
                <span>{formatDate(video.created_at)}</span>
              </div>
            </div>
          </div>

          {/* Tags */}
          {(video.hashtags.length > 0 || video.manual_tags.length > 0) && (
            <div className="flex flex-wrap gap-2 mt-4">
              {video.hashtags.map((tag) => (
                <span
                  key={`h-${tag}`}
                  className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-sm rounded-full"
                >
                  #{tag}
                </span>
              ))}
              {video.manual_tags.map((tag) => (
                <span
                  key={`m-${tag}`}
                  className="px-2 py-1 bg-primary-100 text-primary-700 text-sm rounded-full flex items-center gap-1"
                >
                  <Tag className="w-3 h-3" />
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Tag Editor */}
          <TagEditor
            videoId={video.id}
            currentTags={video.manual_tags}
            onTagsChange={handleTagsChange}
          />

          {/* Context */}
          {video.context && (
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <strong>Context:</strong> {video.context}
              </p>
            </div>
          )}
        </div>

        {/* Transcript */}
        {video.transcript && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
            <h2 className="font-semibold mb-2">Transcript</h2>
            <p className="text-gray-700 dark:text-gray-300 text-sm whitespace-pre-wrap">
              {video.transcript}
            </p>
          </div>
        )}

        {/* Analysis Sections */}
        <div className="space-y-4">
          <h2 className="font-semibold text-lg">Analysis</h2>

          <AnalysisSection
            title="Investment Lens"
            icon={<TrendingUp className="w-5 h-5" />}
            analysis={video.investment_analysis}
            color="border-green-200 bg-green-50 dark:bg-green-900/20"
          />

          <AnalysisSection
            title="Product Lens"
            icon={<Package className="w-5 h-5" />}
            analysis={video.product_analysis}
            color="border-blue-200 bg-blue-50 dark:bg-blue-900/20"
          />

          <AnalysisSection
            title="Content Lens"
            icon={<Film className="w-5 h-5" />}
            analysis={video.content_analysis}
            color="border-purple-200 bg-purple-50 dark:bg-purple-900/20"
          />

          <AnalysisSection
            title="Knowledge Lens"
            icon={<BookOpen className="w-5 h-5" />}
            analysis={video.knowledge_analysis}
            color="border-orange-200 bg-orange-50 dark:bg-orange-900/20"
          />
        </div>

        {/* Export */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
          <h2 className="font-semibold mb-3">Export</h2>
          <ExportButtons video={video} />
        </div>

        {/* Research Chat */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
          <h2 className="font-semibold mb-3">Research Chat</h2>
          <ChatInterface videoId={video.id} />
        </div>
      </main>
    </div>
  );
}
