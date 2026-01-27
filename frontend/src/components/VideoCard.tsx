'use client';

import { Heart, ExternalLink, Eye, ThumbsUp } from 'lucide-react';
import Link from 'next/link';
import { Video, toggleFavorite } from '@/lib/api';
import { formatDate, formatNumber, cn } from '@/lib/utils';
import { useState } from 'react';

interface VideoCardProps {
  video: Video;
  onFavoriteChange?: () => void;
}

export function VideoCard({ video, onFavoriteChange }: VideoCardProps) {
  const [isFavorite, setIsFavorite] = useState(video.is_favorite);
  const [isLoading, setIsLoading] = useState(false);

  const handleFavorite = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsLoading(true);
    try {
      await toggleFavorite(video.id, !isFavorite);
      setIsFavorite(!isFavorite);
      onFavoriteChange?.();
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    processing: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  };

  return (
    <Link href={`/video/${video.id}`}>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-4 cursor-pointer">
        <div className="flex gap-3 sm:gap-4">
          {/* Thumbnail */}
          {video.thumbnail_url ? (
            <img
              src={video.thumbnail_url}
              alt={video.title || 'Video thumbnail'}
              className="w-20 h-20 sm:w-24 sm:h-24 object-cover rounded-lg flex-shrink-0"
            />
          ) : (
            <div className="w-20 h-20 sm:w-24 sm:h-24 bg-gray-200 dark:bg-gray-700 rounded-lg flex-shrink-0 flex items-center justify-center">
              <span className="text-gray-400 text-xs">No image</span>
            </div>
          )}

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold text-gray-900 dark:text-white truncate flex-1">
                {video.title || 'Untitled Video'}
              </h3>
              <button
                onClick={handleFavorite}
                disabled={isLoading}
                className={cn(
                  'p-1.5 min-w-[40px] min-h-[40px] flex items-center justify-center rounded-full transition-colors flex-shrink-0',
                  isFavorite
                    ? 'text-red-500 hover:text-red-600'
                    : 'text-gray-400 hover:text-gray-600'
                )}
              >
                <Heart className={cn('w-5 h-5', isFavorite && 'fill-current')} />
              </button>
            </div>

            {video.creator && (
              <p className="text-sm text-gray-500 dark:text-gray-400">@{video.creator}</p>
            )}

            <div className="flex flex-wrap items-center gap-3 sm:gap-4 mt-2 text-sm text-gray-500">
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
              <span className="whitespace-nowrap">{formatDate(video.created_at)}</span>
            </div>

            {/* Tags */}
            {(video.hashtags.length > 0 || video.manual_tags.length > 0) && (
              <div className="flex flex-wrap gap-1 mt-2">
                {video.hashtags.slice(0, 3).map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs rounded-full"
                  >
                    #{tag}
                  </span>
                ))}
                {video.hashtags.length > 3 && (
                  <span className="text-xs text-gray-400">+{video.hashtags.length - 3}</span>
                )}
              </div>
            )}

            {/* Status badge */}
            <div className="flex items-center justify-between mt-2">
              <span
                className={cn(
                  'px-2 py-0.5 text-xs rounded-full',
                  statusColors[video.status]
                )}
              >
                {video.status}
              </span>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  window.open(video.tiktok_url, '_blank', 'noopener,noreferrer');
                }}
                className="text-gray-400 hover:text-primary-500 transition-colors p-2 min-w-[40px] min-h-[40px] flex items-center justify-center -mr-2"
              >
                <ExternalLink className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
