"use client";

import { useState, useCallback, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { useTags } from "@/hooks/useTags";
import type { TaskStatus, TaskPriority, Tag } from "@/types/task";

interface TaskFilterProps {
  onFilterChange: (filters: {
    search?: string;
    status?: TaskStatus;
    priority?: TaskPriority;
    sortBy?: string;
    dueDate?: string;
    tagIds?: string[];
  }) => void;
  onClearFilters: () => void;
}

export function TaskFilter({ onFilterChange, onClearFilters }: TaskFilterProps) {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<string>("");
  const [priority, setPriority] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("");
  const [dueDate, setDueDate] = useState<string>("");
  const [selectedTagIds, setSelectedTagIds] = useState<string[]>([]);
  const { tags, fetchTags } = useTags();

  useEffect(() => {
    fetchTags();
  }, [fetchTags]);

  const updateFilters = useCallback(
    (newFilters: Partial<{ search: string; status: string; priority: string; sortBy: string; dueDate: string; tagIds: string[] }>) => {
      const filters = {
        search,
        status,
        priority,
        sortBy,
        dueDate,
        tagIds: selectedTagIds,
        ...newFilters,
      };

      onFilterChange({
        search: filters.search || undefined,
        status: (filters.status as TaskStatus) || undefined,
        priority: (filters.priority as TaskPriority) || undefined,
        sortBy: (filters.sortBy as any) || undefined,
        dueDate: filters.dueDate || undefined,
        tagIds: filters.tagIds.length > 0 ? filters.tagIds : undefined,
      });
    },
    [search, status, priority, sortBy, dueDate, selectedTagIds, onFilterChange]
  );

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearch(value);
    updateFilters({ search: value });
  };

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setStatus(value);
    updateFilters({ status: value });
  };

  const handlePriorityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setPriority(value);
    updateFilters({ priority: value });
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setSortBy(value);
    updateFilters({ sortBy: value });
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setDueDate(value);
    updateFilters({ dueDate: value });
  };

  const handleTagToggle = (tagId: string) => {
    const newTagIds = selectedTagIds.includes(tagId)
      ? selectedTagIds.filter(id => id !== tagId)
      : [...selectedTagIds, tagId];
    setSelectedTagIds(newTagIds);
    updateFilters({ tagIds: newTagIds });
  };

  const handleClearFilters = useCallback(() => {
    setSearch("");
    setStatus("");
    setPriority("");
    setSortBy("");
    setDueDate("");
    setSelectedTagIds([]);
    onClearFilters();
  }, [onClearFilters]);

  const hasActiveFilters = search || status || priority || sortBy || dueDate || selectedTagIds.length > 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="col-span-1 sm:col-span-2 lg:col-span-1">
          <label htmlFor="search" className="sr-only">
            Search tasks
          </label>
          <Input
            id="search"
            type="search"
            placeholder="Search..."
            value={search}
            onChange={handleSearchChange}
          />
        </div>
        <div>
          <Select
            id="status"
            value={status}
            onChange={handleStatusChange}
            options={[
              { value: "", label: "Status" },
              { value: "pending", label: "Pending" },
              { value: "in_progress", label: "In Progress" },
              { value: "completed", label: "Completed" },
            ]}
          />
        </div>
        <div>
          <Select
            id="priority"
            value={priority}
            onChange={handlePriorityChange}
            options={[
              { value: "", label: "Priority" },
              { value: "low", label: "Low" },
              { value: "medium", label: "Medium" },
              { value: "high", label: "High" },
            ]}
          />
        </div>
        <div>
          <Select
            id="sort"
            value={sortBy}
            onChange={handleSortChange}
            options={[
              { value: "", label: "Sort By" },
              { value: "dueDate", label: "Due Date" },
              { value: "priority", label: "Priority" },
              { value: "createdAt", label: "Created Date" },
              { value: "title", label: "Alphabetical" },
            ]}
          />
        </div>
        <div>
          <Input
            id="dueDate"
            type="date"
            value={dueDate}
            onChange={handleDateChange}
            className="w-full"
          />
        </div>
      </div>

      {/* Tag Filter */}
      {tags.length > 0 && (
        <div className="mt-4">
          <label className="text-xs font-semibold text-gray-600 mb-2 block">Filter by Tags:</label>
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <button
                key={tag.id}
                type="button"
                onClick={() => handleTagToggle(tag.id)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${selectedTagIds.includes(tag.id)
                  ? 'ring-2 ring-offset-1'
                  : 'opacity-60 hover:opacity-100'
                  }`}
                style={{
                  backgroundColor: `${tag.color}20`,
                  color: tag.color,
                  border: `1px solid ${tag.color}40`,
                }}
              >
                {tag.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {hasActiveFilters && (
        <div className="mt-4 flex justify-end">
          <Button variant="ghost" size="sm" onClick={handleClearFilters}>
            Clear filters
          </Button>
        </div>
      )}
    </div>
  );
}
