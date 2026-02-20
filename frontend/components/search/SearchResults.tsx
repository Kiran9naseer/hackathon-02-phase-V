"use client";

import { SearchBar } from "./SearchBar";
import { SearchFilters } from "./SearchFilters";
import { TaskList } from "@/components/tasks/TaskList";
import { SearchEmptyState } from "./SearchEmptyState";
import type { Task } from "@/types/task";

interface SearchResultsProps {
    tasks: Task[];
    total: number;
    query: string;
    isLoading: boolean;
    onToggleComplete: (id: string) => void;
    onDelete: (id: string) => void;
}

export function SearchResults({
    tasks,
    total,
    query,
    isLoading,
    onToggleComplete,
    onDelete
}: SearchResultsProps) {
    if (!isLoading && tasks.length === 0) {
        return <SearchEmptyState query={query} />;
    }

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between px-4">
                <div>
                    <span className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/20 italic">
                        Search Output
                    </span>
                    <h2 className="text-xl font-black text-white italic uppercase tracking-tighter">
                        {total} Signal{total !== 1 ? 's' : ''} Detected
                    </h2>
                </div>
            </div>

            <TaskList
                tasks={tasks}
                isLoading={isLoading}
                onToggleComplete={onToggleComplete}
                onDelete={onDelete}
                highlightQuery={query}
            />
        </div>
    );
}
