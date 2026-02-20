import Link from "next/link";
import { Task } from "@/types/task";
import { formatDate, getPriorityColor, getStatusColor } from "@/lib/utils";
import { Checkbox } from "@/components/ui/Checkbox";
import { HighlightedText } from "@/components/ui/HighlightedText";

interface TaskItemProps {
  task: Task;
  onToggleComplete: (id: string) => void;
  onDelete: (id: string) => void;
  isCompleting?: boolean;
  highlightQuery?: string;
}

export function TaskItem({
  task,
  onToggleComplete,
  onDelete,
  isCompleting,
  highlightQuery,
}: TaskItemProps) {
  const isCompleted = task.status === "completed";

  return (
    <div
      className={`group flex items-center gap-4 p-4 rounded-2xl border transition-all ${isCompleted
        ? "bg-slate-50/50 border-slate-100 opacity-80"
        : "bg-white border-slate-100 hover:border-primary-100 hover:shadow-md"
        }`}
    >
      <Checkbox
        checked={isCompleted}
        onChange={() => onToggleComplete(task.id)}
        disabled={isCompleting}
        className="w-5 h-5 rounded-lg border-2 border-slate-200 checked:bg-green-500 checked:border-green-500 transition-all"
      />
      <div className="flex-1 min-w-0">
        <Link href={`/tasks/${task.id}`}>
          <h3 className={`font-bold transition-colors group-hover:text-primary-600 truncate ${isCompleted ? "text-slate-400 line-through" : "text-slate-800"}`}>
            <HighlightedText text={task.title} query={highlightQuery} />
          </h3>
        </Link>
        <div className="flex items-center space-x-3 mt-1">
          <span className={`text-[9px] px-1.5 py-0.5 rounded-md font-black uppercase tracking-wider ${task.priority === 'high' ? 'bg-red-50 text-red-600' :
            task.priority === 'medium' ? 'bg-orange-50 text-orange-600' :
              'bg-blue-50 text-blue-600'
            }`}>
            {task.priority}
          </span>
          {task.category && (
            <span className="text-[9px] px-1.5 py-0.5 rounded-md font-black uppercase tracking-wider bg-slate-100 text-slate-500">
              {task.category.name}
            </span>
          )}
          <div className="h-1 w-1 bg-slate-200 rounded-full"></div>
          <span className="text-[10px] font-bold text-slate-400">{formatDate(task.dueDate || task.createdAt)}</span>
        </div>
      </div>
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={() => onDelete(task.id)}
          className="p-2 hover:bg-red-50 rounded-xl text-slate-400 hover:text-red-600 transition-all"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
        </button>
      </div>
    </div>
  );
}
