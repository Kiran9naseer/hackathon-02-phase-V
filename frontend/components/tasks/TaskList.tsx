"use client";

import { Task } from "@/types/task";
import { TaskCard } from "./TaskCard";
import { TaskItem } from "./TaskItem";
import { TaskCardSkeleton } from "@/components/ui/Skeleton";

interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  onToggleComplete: (id: string) => void;
  onDelete: (id: string) => void;
  viewMode?: "card" | "list";
  completingId?: string | null;
  highlightQuery?: string;
}

export function TaskList({
  tasks,
  isLoading,
  onToggleComplete,
  onDelete,
  viewMode = "card",
  completingId = null,
  highlightQuery,
}: TaskListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <TaskCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return null;
  }

  if (viewMode === "list") {
    return (
      <div className="space-y-3">
        {tasks.filter((task) => task && task.id).map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggleComplete={onToggleComplete}
            onDelete={onDelete}
            isCompleting={completingId === task.id}
            highlightQuery={highlightQuery}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {tasks.filter((task) => task && task.id).map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onToggleComplete={onToggleComplete}
          onDelete={onDelete}
          isCompleting={completingId === task.id}
          highlightQuery={highlightQuery}
        />
      ))}
    </div>
  );
}
