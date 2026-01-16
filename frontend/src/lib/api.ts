/**
 * API client for Tikodea backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Video {
  id: number;
  tiktok_url: string;
  context: string | null;
  title: string | null;
  description: string | null;
  creator: string | null;
  hashtags: string[];
  view_count: number | null;
  like_count: number | null;
  thumbnail_url: string | null;
  transcript: string | null;
  investment_analysis: Record<string, any> | null;
  product_analysis: Record<string, any> | null;
  content_analysis: Record<string, any> | null;
  knowledge_analysis: Record<string, any> | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message: string | null;
  is_favorite: boolean;
  manual_tags: string[];
  created_at: string;
  updated_at: string;
  processed_at: string | null;
}

export interface VideosResponse {
  videos: Video[];
  total: number;
  skip: number;
  limit: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export async function fetchVideos(params?: {
  skip?: number;
  limit?: number;
  favorites_only?: boolean;
  search?: string;
  tag?: string;
}): Promise<VideosResponse> {
  const searchParams = new URLSearchParams();
  if (params?.skip) searchParams.set('skip', String(params.skip));
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.favorites_only) searchParams.set('favorites_only', 'true');
  if (params?.search) searchParams.set('search', params.search);
  if (params?.tag) searchParams.set('tag', params.tag);

  const res = await fetch(`${API_BASE}/api/videos?${searchParams}`);
  if (!res.ok) throw new Error('Failed to fetch videos');
  return res.json();
}

export async function fetchVideo(id: number): Promise<Video> {
  const res = await fetch(`${API_BASE}/api/videos/${id}`);
  if (!res.ok) throw new Error('Failed to fetch video');
  return res.json();
}

export async function toggleFavorite(id: number, is_favorite: boolean): Promise<void> {
  const res = await fetch(`${API_BASE}/api/videos/${id}/favorite`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_favorite }),
  });
  if (!res.ok) throw new Error('Failed to toggle favorite');
}

export async function updateTags(id: number, tags: string[]): Promise<void> {
  const res = await fetch(`${API_BASE}/api/videos/${id}/tags`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tags }),
  });
  if (!res.ok) throw new Error('Failed to update tags');
}

export async function fetchChatHistory(videoId: number): Promise<{ messages: ChatMessage[] }> {
  const res = await fetch(`${API_BASE}/api/videos/${videoId}/chat`);
  if (!res.ok) throw new Error('Failed to fetch chat history');
  return res.json();
}

export async function sendChatMessage(videoId: number, message: string): Promise<ChatMessage> {
  const res = await fetch(`${API_BASE}/api/videos/${videoId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error('Failed to send message');
  return res.json();
}
