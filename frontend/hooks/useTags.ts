"use client";

import { useState, useCallback } from "react";
import apiClient from "@/lib/api/client";
import type { Tag } from "@/types/task";

interface UseTagsReturn {
  tags: Tag[];
  isLoading: boolean;
  error: string | null;
  fetchTags: () => Promise<void>;
  createTag: (name: string, color?: string) => Promise<Tag>;
  deleteTag: (id: string) => Promise<void>;
}

export function useTags(): UseTagsReturn {
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTags = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<{ items: Tag[] }>("/api/v1/tags");
      setTags(response.data.items || []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch tags";
      setError(errorMessage);
      console.error("Error fetching tags:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createTag = useCallback(async (name: string, color: string = "#8FBFB3"): Promise<Tag> => {
    setError(null);
    try {
      const response = await apiClient.post<Tag>("/api/v1/tags", {
        name,
        color,
      });
      const newTag = response.data;
      setTags((prev) => [...prev, newTag]);
      return newTag;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to create tag";
      setError(errorMessage);
      throw err;
    }
  }, []);

  const deleteTag = useCallback(async (id: string) => {
    setError(null);
    try {
      await apiClient.delete(`/api/v1/tags/${id}`);
      setTags((prev) => prev.filter((tag) => tag.id !== id));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to delete tag";
      setError(errorMessage);
      throw err;
    }
  }, []);

  return {
    tags,
    isLoading,
    error,
    fetchTags,
    createTag,
    deleteTag,
  };
}
