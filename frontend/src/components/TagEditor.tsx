'use client';

import { useState } from 'react';
import { Tag, X, Plus } from 'lucide-react';
import { updateTags } from '@/lib/api';
import { cn } from '@/lib/utils';

interface TagEditorProps {
  videoId: number;
  currentTags: string[];
  onTagsChange: () => void;
}

export function TagEditor({ videoId, currentTags, onTagsChange }: TagEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [tags, setTags] = useState<string[]>(currentTags);
  const [newTag, setNewTag] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddTag = () => {
    const trimmedTag = newTag.trim();

    // Validation
    if (!trimmedTag) {
      setError('Tag cannot be empty');
      return;
    }

    if (trimmedTag.length > 30) {
      setError('Tag must be 30 characters or less');
      return;
    }

    if (tags.includes(trimmedTag)) {
      setError('Tag already exists');
      return;
    }

    setTags([...tags, trimmedTag]);
    setNewTag('');
    setError(null);
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await updateTags(videoId, tags);
      onTagsChange();
      setIsEditing(false);
    } catch (err) {
      setError('Failed to save tags');
      console.error('Failed to save tags:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setTags(currentTags);
    setNewTag('');
    setError(null);
    setIsEditing(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  return (
    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          Manual Tags
        </h3>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="px-3 py-1 text-sm bg-primary-100 hover:bg-primary-200 text-primary-700 rounded-lg transition-colors"
          >
            Edit Tags
          </button>
        )}
      </div>

      {/* Tag Display/Edit Mode */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 bg-primary-100 text-primary-700 text-sm rounded-full flex items-center gap-1"
            >
              <Tag className="w-3 h-3" />
              {tag}
              {isEditing && (
                <button
                  onClick={() => handleRemoveTag(tag)}
                  className="ml-1 hover:text-primary-900 transition-colors"
                  aria-label={`Remove tag ${tag}`}
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </span>
          ))}
        </div>
      )}

      {tags.length === 0 && !isEditing && (
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
          No manual tags added yet.
        </p>
      )}

      {/* Add Tag Input (only in edit mode) */}
      {isEditing && (
        <div className="space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Add a tag..."
              maxLength={30}
              className={cn(
                "flex-1 px-3 py-2 text-sm border rounded-lg",
                "focus:outline-none focus:ring-2 focus:ring-primary-500",
                "dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                error ? "border-red-500" : "border-gray-300"
              )}
            />
            <button
              onClick={handleAddTag}
              disabled={!newTag.trim()}
              className={cn(
                "px-3 py-2 rounded-lg transition-colors flex items-center gap-1",
                "bg-primary-500 hover:bg-primary-600 text-white",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              <Plus className="w-4 h-4" />
              Add
            </button>
          </div>

          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={isLoading}
              className={cn(
                "px-4 py-2 text-sm rounded-lg transition-colors",
                "bg-green-500 hover:bg-green-600 text-white",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              {isLoading ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={handleCancel}
              disabled={isLoading}
              className={cn(
                "px-4 py-2 text-sm rounded-lg transition-colors",
                "bg-gray-200 hover:bg-gray-300 text-gray-700",
                "dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-300",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
