"use client";

import { useEffect, useState } from "react";
import { useTags } from "@/hooks/useTags";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Trash2, Plus, Edit2, X } from "lucide-react";
import type { Tag } from "@/types/task";

export default function TagsPage() {
    const { tags, fetchTags, createTag, deleteTag, isLoading, error } = useTags();
    const [isCreating, setIsCreating] = useState(false);
    const [newTagName, setNewTagName] = useState("");
    const [newTagColor, setNewTagColor] = useState("#8FBFB3");

    useEffect(() => {
        fetchTags();
    }, [fetchTags]);

    const handleCreateTag = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newTagName.trim()) return;

        try {
            await createTag(newTagName.trim(), newTagColor);
            setNewTagName("");
            setNewTagColor("#8FBFB3");
            setIsCreating(false);
        } catch (err) {
            console.error("Failed to create tag:", err);
        }
    };

    const handleDeleteTag = async (tagId: string) => {
        if (!confirm("Are you sure you want to delete this tag? It will be removed from all tasks.")) {
            return;
        }

        try {
            await deleteTag(tagId);
        } catch (err) {
            console.error("Failed to delete tag:", err);
        }
    };

    const colorPresets = [
        "#8FBFB3", // Mist Green (default)
        "#FF6B6B", // Red
        "#4ECDC4", // Teal
        "#FFE66D", // Yellow
        "#A8E6CF", // Light Green
        "#FF8B94", // Pink
        "#C7CEEA", // Lavender
        "#FFDAC1", // Peach
    ];

    return (
        <div className="min-h-screen bg-surface-dark p-6">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-black text-white tracking-tighter italic uppercase mb-2">
                        Tag Management.
                    </h1>
                    <p className="text-primary-100/30 text-sm font-black uppercase tracking-widest italic">
                        Organize your tasks with custom tags
                    </p>
                </div>

                {/* Create Tag Section */}
                <div className="glass-card p-6 mb-6">
                    {!isCreating ? (
                        <Button
                            onClick={() => setIsCreating(true)}
                            className="premium-button bg-primary-600 hover:bg-primary-500 w-full sm:w-auto"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Create New Tag
                        </Button>
                    ) : (
                        <form onSubmit={handleCreateTag} className="space-y-4">
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="tagName" className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 ml-1 italic">
                                        Tag Name *
                                    </Label>
                                    <Input
                                        id="tagName"
                                        type="text"
                                        value={newTagName}
                                        onChange={(e) => setNewTagName(e.target.value)}
                                        placeholder="e.g. Urgent, Work, Personal"
                                        className="premium-input"
                                        maxLength={50}
                                        required
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="tagColor" className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 ml-1 italic">
                                        Color
                                    </Label>
                                    <div className="flex gap-2">
                                        <Input
                                            id="tagColor"
                                            type="color"
                                            value={newTagColor}
                                            onChange={(e) => setNewTagColor(e.target.value)}
                                            className="w-16 h-10 cursor-pointer"
                                        />
                                        <div className="flex flex-wrap gap-1">
                                            {colorPresets.map((color) => (
                                                <button
                                                    key={color}
                                                    type="button"
                                                    onClick={() => setNewTagColor(color)}
                                                    className={`w-8 h-8 rounded-full border-2 transition-all ${newTagColor === color ? 'border-white scale-110' : 'border-transparent hover:scale-105'
                                                        }`}
                                                    style={{ backgroundColor: color }}
                                                    title={color}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <Button
                                    type="submit"
                                    className="premium-button bg-primary-600 hover:bg-primary-500"
                                    disabled={!newTagName.trim()}
                                >
                                    <Plus className="w-4 h-4 mr-2" />
                                    Create Tag
                                </Button>
                                <Button
                                    type="button"
                                    variant="ghost"
                                    onClick={() => {
                                        setIsCreating(false);
                                        setNewTagName("");
                                        setNewTagColor("#8FBFB3");
                                    }}
                                    className="hover:bg-primary-500/10"
                                >
                                    <X className="w-4 h-4 mr-2" />
                                    Cancel
                                </Button>
                            </div>
                        </form>
                    )}
                </div>

                {/* Error Display */}
                {error && (
                    <div className="glass-card p-4 mb-6 border-red-500/20 bg-red-500/5">
                        <p className="text-red-500 text-sm font-bold">Error: {error}</p>
                    </div>
                )}

                {/* Tags List */}
                <div className="glass-card p-6">
                    <h2 className="text-2xl font-black text-white tracking-tighter italic uppercase mb-4">
                        Your Tags ({tags.length})
                    </h2>

                    {isLoading && tags.length === 0 ? (
                        <div className="flex justify-center py-12">
                            <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
                        </div>
                    ) : tags.length === 0 ? (
                        <div className="text-center py-12">
                            <p className="text-primary-100/30 text-sm font-medium italic">
                                No tags yet. Create your first tag to get started!
                            </p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            {tags.map((tag) => (
                                <div
                                    key={tag.id}
                                    className="group relative p-4 rounded-xl border transition-all hover:scale-105"
                                    style={{
                                        backgroundColor: `${tag.color}10`,
                                        borderColor: `${tag.color}40`,
                                    }}
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div
                                                className="w-4 h-4 rounded-full"
                                                style={{ backgroundColor: tag.color }}
                                            />
                                            <span
                                                className="font-bold text-lg"
                                                style={{ color: tag.color }}
                                            >
                                                {tag.name}
                                            </span>
                                        </div>

                                        <button
                                            onClick={() => handleDeleteTag(tag.id)}
                                            className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-red-500/20 rounded-lg text-red-500"
                                            title="Delete tag"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>

                                    <div className="mt-2 text-xs text-primary-100/30 font-medium italic">
                                        Created: {new Date(tag.createdAt).toLocaleDateString()}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
