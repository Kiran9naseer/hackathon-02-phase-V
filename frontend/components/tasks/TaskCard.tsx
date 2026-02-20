"use client";

import Link from "next/link";
import { Task, Priority } from "@/types/task";
import { formatDate } from "@/lib/utils";
import { Checkbox } from "@/components/ui/Checkbox";
import { Trash2 } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { PriorityBadge } from './PriorityBadge';
import { HighlightedText } from "@/components/ui/HighlightedText";
import { RecurrenceBadge } from "./RecurrenceBadge";

interface TaskCardProps {
  task: Task;
  onToggleComplete: (id: string) => void;
  onDelete: (id: string) => void;
  isCompleting?: boolean;
  highlightQuery?: string;
}

export function TaskCard({
  task,
  onToggleComplete,
  onDelete,
  isCompleting,
  highlightQuery,
}: TaskCardProps) {
  const isCompleted = task.status === "completed";
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const isDark = theme === 'dark';
  const isOverdue = !isCompleted && task.dueDate && new Date(task.dueDate) < new Date(new Date().setHours(0, 0, 0, 0));

  return (
    <div
      className={`glass-card p-8 group relative overflow-hidden transition-all duration-700 ${isCompleted ? 'opacity-40 grayscale-[0.5]' :
        isOverdue ? 'border-red-500/50 shadow-[0_0_20px_rgba(239,68,68,0.1)]' : ''
        }`}
    >
      {/* Card Mist Background */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary-500/5 rounded-full blur-3xl -z-10 group-hover:bg-primary-500/10 transition-all duration-700"></div>

      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center gap-2">
          <PriorityBadge priority={task.priority as Priority} size="sm" />
          {task.recurrenceSeriesId && <RecurrenceBadge />}
        </div>
        <Checkbox
          checked={isCompleted}
          onChange={() => onToggleComplete(task.id)}
          disabled={isCompleting}
          className="w-6 h-6 rounded-full border-primary-500/40 checked:bg-primary-500 checked:border-primary-500 transition-all duration-500"
        />
      </div>

      <Link href={`/tasks/${task.id}`} className="block mb-4">
        <h3
          className={`font-black text-2xl tracking-tighter italic uppercase transition-all duration-500 group-hover:text-primary-400 ${isCompleted ? 'text-primary-50/20 line-through' : 'text-white'
            }`}
        >
          <HighlightedText text={task.title} query={highlightQuery} />
        </h3>
      </Link>

      {task.description && (
        <p className={`text-md line-clamp-2 mb-8 font-medium leading-relaxed tracking-tight ${isCompleted ? 'text-primary-50/10' : 'text-primary-50/40'
          }`}>
          <HighlightedText text={task.description} query={highlightQuery} />
        </p>
      )}

      {/* Tags Display */}
      {task.tags && task.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-6">
          {task.tags.map((tag) => (
            <span
              key={tag.id}
              className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider transition-all duration-300 hover:scale-105 cursor-pointer"
              style={{
                backgroundColor: `${tag.color}15`,
                color: tag.color,
                border: `1px solid ${tag.color}40`,
                boxShadow: `0 0 10px ${tag.color}10`,
              }}
            >
              {tag.name}
            </span>
          ))}
        </div>
      )}

      {/* Progress Matrix */}
      <div className="mb-8 p-4 rounded-2xl bg-primary-500/5 border border-primary-500/10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[9px] font-black uppercase tracking-[0.2em] text-primary-50/20 italic">
            Synchronization
          </span>
          <span className={`text-[10px] font-black italic ${isOverdue ? 'text-red-500' : 'text-primary-500'}`}>
            {isCompleted ? '100% COMPLETE' : isOverdue ? 'PROTOCOL OVERDUE' : 'PENDING'}
          </span>
        </div>
        <div className="h-1.5 w-full rounded-full bg-primary-950 overflow-hidden">
          <div
            className={`h-full transition-all duration-1000 ${isCompleted ? 'bg-primary-500' : 'bg-primary-500/20'
              }`}
            style={{ width: isCompleted ? '100%' : '15%' }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between pt-6 border-t border-primary-500/10 mt-auto">
        <div className="flex items-center space-x-3 text-primary-50/30">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-[10px] font-black italic uppercase tracking-widest">
            {formatDate(task.dueDate || task.createdAt)}
          </span>
        </div>

        <button
          onClick={() => onDelete(task.id)}
          className="p-3 rounded-full hover:bg-red-500/10 text-primary-50/20 hover:text-red-500 transition-all duration-500 opacity-0 group-hover:opacity-100"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {isCompleting && (
        <div className="absolute inset-0 flex items-center justify-center bg-surface-dark/80 backdrop-blur-sm z-10 transition-all">
          <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
}
