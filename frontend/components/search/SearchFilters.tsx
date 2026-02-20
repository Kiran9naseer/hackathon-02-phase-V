"use client";

import { useState, useCallback } from "react";
import { Label } from "@/components/ui/Label";
import { Select } from "@/components/ui/Select";
import { Input } from "@/components/ui/Input";
import { useTags } from "@/hooks/useTags";
import { useCategories } from "@/hooks/useCategories";
import type { TaskStatus, TaskPriority } from "@/types/task";

interface SearchFiltersProps {
    onFilterChange: (filters: any) => void;
    initialFilters?: any;
}

export function SearchFilters({ onFilterChange, initialFilters = {} }: SearchFiltersProps) {
    const [filters, setFilters] = useState({
        status: initialFilters.status || "",
        priority: initialFilters.priority || "",
        tagIds: initialFilters.tagIds || [],
        categoryId: initialFilters.categoryId || "",
        startDate: initialFilters.startDate || "",
        endDate: initialFilters.endDate || "",
    });

    const { tags } = useTags();
    const { categories } = useCategories();

    const handleUpdate = (updates: any) => {
        const newFilters = { ...filters, ...updates };
        setFilters(newFilters);
        onFilterChange(newFilters);
    };

    const toggleTag = (tagId: string) => {
        const newTagIds = filters.tagIds.includes(tagId)
            ? filters.tagIds.filter((id: string) => id !== tagId)
            : [...filters.tagIds, tagId];
        handleUpdate({ tagIds: newTagIds });
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Status Filter */}
            <div className="space-y-3">
                <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 italic">Status Lifecycle</Label>
                <Select
                    value={filters.status}
                    onChange={(e) => handleUpdate({ status: e.target.value })}
                    options={[
                        { value: "", label: "All Sectors" },
                        { value: "pending", label: "Pending Analysis" },
                        { value: "in_progress", label: "Active Ops" },
                        { value: "completed", label: "Mission Success" },
                    ]}
                    className="premium-input w-full"
                />
            </div>

            {/* Priority Filter */}
            <div className="space-y-3">
                <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 italic">Threat Level</Label>
                <Select
                    value={filters.priority}
                    onChange={(e) => handleUpdate({ priority: e.target.value })}
                    options={[
                        { value: "", label: "Neutral" },
                        { value: "low", label: "Low Impact" },
                        { value: "medium", label: "Normal Param" },
                        { value: "high", label: "Critical Priority" },
                    ]}
                    className="premium-input w-full"
                />
            </div>

            {/* Date Range Filter */}
            <div className="space-y-3">
                <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 italic">Temporal Range</Label>
                <div className="grid grid-cols-1 gap-2">
                    <Input
                        type="date"
                        placeholder="From"
                        value={filters.startDate}
                        onChange={(e) => handleUpdate({ startDate: e.target.value })}
                        className="premium-input text-[10px] [color-scheme:dark]"
                    />
                    <Input
                        type="date"
                        placeholder="To"
                        value={filters.endDate}
                        onChange={(e) => handleUpdate({ endDate: e.target.value })}
                        className="premium-input text-[10px] [color-scheme:dark]"
                    />
                </div>
            </div>

            {/* Tags Filter */}
            <div className="space-y-3">
                <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 italic">Signal Markers (Tags)</Label>
                <div className="flex flex-wrap gap-2">
                    {tags.map((tag) => (
                        <button
                            key={tag.id}
                            onClick={() => toggleTag(tag.id)}
                            className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest transition-all duration-300 border ${filters.tagIds.includes(tag.id)
                                    ? 'bg-primary-500/20 text-white border-primary-500/50 shadow-mist'
                                    : 'bg-primary-500/5 text-primary-50/20 border-primary-500/10 hover:border-primary-500/30'
                                }`}
                            style={filters.tagIds.includes(tag.id) ? { borderColor: tag.color, color: tag.color } : {}}
                        >
                            {tag.name}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
