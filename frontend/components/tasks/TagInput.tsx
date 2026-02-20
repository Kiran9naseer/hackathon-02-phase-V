"use client";

import { useState, useEffect, useRef } from "react";
import { X } from "lucide-react";
import type { Tag } from "@/types/task";

interface TagInputProps {
    selectedTags: Tag[];
    onTagsChange: (tags: Tag[]) => void;
    availableTags: Tag[];
    onCreateTag?: (name: string) => Promise<Tag>;
}

export default function TagInput({
    selectedTags,
    onTagsChange,
    availableTags,
    onCreateTag,
}: TagInputProps) {
    const [inputValue, setInputValue] = useState("");
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [filteredTags, setFilteredTags] = useState<Tag[]>([]);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (inputValue.trim()) {
            const filtered = availableTags.filter(
                (tag) =>
                    tag.name.toLowerCase().includes(inputValue.toLowerCase()) &&
                    !selectedTags.some((selected) => selected.id === tag.id)
            );
            setFilteredTags(filtered);
            setShowSuggestions(true);
        } else {
            setFilteredTags([]);
            setShowSuggestions(false);
        }
    }, [inputValue, availableTags, selectedTags]);

    const handleSelectTag = (tag: Tag) => {
        onTagsChange([...selectedTags, tag]);
        setInputValue("");
        setShowSuggestions(false);
        inputRef.current?.focus();
    };

    const handleRemoveTag = (tagId: string) => {
        onTagsChange(selectedTags.filter((tag) => tag.id !== tagId));
    };

    const handleCreateTag = async () => {
        if (!inputValue.trim() || !onCreateTag) return;

        try {
            const newTag = await onCreateTag(inputValue.trim());
            onTagsChange([...selectedTags, newTag]);
            setInputValue("");
            setShowSuggestions(false);
        } catch (error) {
            console.error("Failed to create tag:", error);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            e.preventDefault();
            if (filteredTags.length > 0) {
                handleSelectTag(filteredTags[0]);
            } else if (inputValue.trim() && onCreateTag) {
                handleCreateTag();
            }
        } else if (e.key === "Backspace" && !inputValue && selectedTags.length > 0) {
            handleRemoveTag(selectedTags[selectedTags.length - 1].id);
        }
    };

    return (
        <div className="relative">
            <div className="flex flex-wrap gap-2 p-3 bg-[#0a1a1a] border border-[#1a3a3a] rounded-lg focus-within:border-[#8FBFB3] transition-colors">
                {selectedTags.map((tag) => (
                    <span
                        key={tag.id}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-sm font-medium"
                        style={{
                            backgroundColor: `${tag.color}20`,
                            color: tag.color,
                            border: `1px solid ${tag.color}40`,
                        }}
                    >
                        {tag.name}
                        <button
                            type="button"
                            onClick={() => handleRemoveTag(tag.id)}
                            className="hover:bg-black/20 rounded-full p-0.5 transition-colors"
                        >
                            <X className="w-3 h-3" />
                        </button>
                    </span>
                ))}
                <input
                    ref={inputRef}
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onFocus={() => inputValue && setShowSuggestions(true)}
                    onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                    placeholder={selectedTags.length === 0 ? "Add tags..." : ""}
                    className="flex-1 min-w-[120px] bg-transparent border-none outline-none text-white placeholder-gray-500"
                />
            </div>

            {showSuggestions && (
                <div className="absolute z-10 w-full mt-2 bg-[#0a1a1a] border border-[#1a3a3a] rounded-lg shadow-xl max-h-48 overflow-y-auto">
                    {filteredTags.length > 0 ? (
                        <ul className="py-1">
                            {filteredTags.map((tag) => (
                                <li key={tag.id}>
                                    <button
                                        type="button"
                                        onClick={() => handleSelectTag(tag)}
                                        className="w-full px-4 py-2 text-left hover:bg-[#1a3a3a] transition-colors flex items-center gap-2"
                                    >
                                        <span
                                            className="w-3 h-3 rounded-full"
                                            style={{ backgroundColor: tag.color }}
                                        />
                                        <span className="text-white">{tag.name}</span>
                                    </button>
                                </li>
                            ))}
                        </ul>
                    ) : inputValue.trim() && onCreateTag ? (
                        <div className="py-2 px-4">
                            <button
                                type="button"
                                onClick={handleCreateTag}
                                className="w-full text-left text-[#8FBFB3] hover:text-[#a0cfbf] transition-colors"
                            >
                                Create tag &quot;{inputValue}&quot;
                            </button>
                        </div>
                    ) : null}
                </div>
            )}
        </div>
    );
}
