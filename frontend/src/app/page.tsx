'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Heart, RefreshCw, Loader2 } from 'lucide-react';
import { fetchVideos, Video } from '@/lib/api';
import { VideoCard } from '@/components/VideoCard';
import { cn } from '@/lib/utils';

export default function HomePage() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  const loadVideos = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchVideos({
        search: searchQuery || undefined,
        favorites_only: favoritesOnly,
        tag: selectedTag || undefined,
        limit: 50,
      });
      setVideos(data.videos);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to load videos:', error);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, favoritesOnly, selectedTag]);

  useEffect(() => {
    loadVideos();
  }, [loadVideos]);

  // Collect all unique tags
  const allTags = Array.from(
    new Set(videos.flatMap((v) => [...v.hashtags, ...v.manual_tags]))
  ).sort();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-primary-600">Tikodea</h1>
            <button
              onClick={loadVideos}
              disabled={isLoading}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <RefreshCw className={cn('w-5 h-5', isLoading && 'animate-spin')} />
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search videos..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600"
            />
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2 mt-3 overflow-x-auto pb-2">
            <button
              onClick={() => setFavoritesOnly(!favoritesOnly)}
              className={cn(
                'flex items-center gap-1 px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors',
                favoritesOnly
                  ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200'
                  : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200'
              )}
            >
              <Heart className={cn('w-4 h-4', favoritesOnly && 'fill-current')} />
              Favorites
            </button>

            {selectedTag && (
              <button
                onClick={() => setSelectedTag(null)}
                className="px-3 py-1.5 bg-primary-100 text-primary-700 rounded-full text-sm flex items-center gap-1"
              >
                #{selectedTag}
                <span className="text-xs">×</span>
              </button>
            )}

            {allTags.slice(0, 5).map((tag) => (
              <button
                key={tag}
                onClick={() => setSelectedTag(tag === selectedTag ? null : tag)}
                className={cn(
                  'px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors',
                  tag === selectedTag
                    ? 'bg-primary-100 text-primary-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
                )}
              >
                #{tag}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
          </div>
        ) : videos.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400 mb-2">No videos found</p>
            <p className="text-sm text-gray-400 dark:text-gray-500">
              Send a TikTok URL to your Telegram bot to get started
            </p>
          </div>
        ) : (
          <>
            <p className="text-sm text-gray-500 mb-4">{total} video{total !== 1 ? 's' : ''}</p>
            <div className="space-y-4">
              {videos.map((video) => (
                <VideoCard key={video.id} video={video} onFavoriteChange={loadVideos} />
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
