"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useCategories } from "@/hooks/useCategories";
import { useTags } from "@/hooks/useTags";
import { createTaskSchema, type CreateTaskSchema } from "@/lib/validation/schemas";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Select } from "@/components/ui/Select";
import TagInput from "@/components/tasks/TagInput";
import { RecurringSettings } from "@/components/tasks/RecurringSettings";
import { ReminderConfig } from "@/components/tasks/ReminderConfig";
import Switch from "@/components/ui/Switch";
import type { Task, CreateTaskRequest, UpdateTaskRequest, Tag } from "@/types/task";

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: CreateTaskRequest | UpdateTaskRequest) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

export function TaskForm({ task, onSubmit, onCancel, isLoading }: TaskFormProps) {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const { categories, fetchCategories } = useCategories();
  const { tags: availableTags, fetchTags, createTag } = useTags();
  const [selectedTags, setSelectedTags] = useState<Tag[]>(task?.tags || []);
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurringSettings, setRecurringSettings] = useState({
    frequency: "daily",
    interval: 1,
    endDate: undefined as string | undefined
  });
  const [reminderOffsets, setReminderOffsets] = useState<number[]>([]);
  const [hasReminder, setHasReminder] = useState(false);

  useEffect(() => {
    fetchCategories();
    fetchTags();
  }, [fetchCategories, fetchTags]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateTaskSchema>({
    resolver: zodResolver(createTaskSchema),
    defaultValues: task
      ? {
        title: task.title,
        description: task.description || "",
        priority: task.priority,
        categoryId: task.categoryId || "",
        dueDate: task.dueDate ? task.dueDate.split("T")[0] : "",
      }
      : {
        priority: "medium",
        categoryId: "",
      },
  });

  const onFormSubmit = async (data: CreateTaskSchema) => {
    setSubmitError(null);
    try {
      const submitData: any = {
        title: data.title,
        description: data.description || undefined,
        priority: data.priority,
        categoryId: data.categoryId || undefined,
        dueDate: data.dueDate || undefined,
        tag_ids: selectedTags.map(tag => tag.id),
        is_recurring: isRecurring,
        recurrence: isRecurring ? recurringSettings : undefined,
        reminder_config: hasReminder ? { offsets: reminderOffsets, type: 'in_app' } : undefined
      };
      await onSubmit(submitData);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to save task");
    }
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6" noValidate>
      {submitError && (
        <div
          className="p-4 text-xs font-black uppercase tracking-widest border border-red-500/20 bg-red-500/5 text-red-500 rounded-xl animate-pulse italic"
          role="alert"
        >
          !! Error: {submitError}
        </div>
      )}

      <div className="space-y-1.5">
        <Label htmlFor="title" className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 ml-1 italic">Task Title *</Label>
        <Input
          id="title"
          type="text"
          placeholder="e.g. Design System Overhaul"
          className="premium-input w-full"
          disabled={isLoading}
          {...register("title")}
          aria-invalid={errors.title ? "true" : "false"}
        />
        {errors.title && (
          <p className="text-[10px] text-red-500 font-bold ml-1 italic uppercase tracking-wider" role="alert">
            {errors.title.message}
          </p>
        )}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="description" className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 ml-1 italic">Notes & Context</Label>
        <textarea
          id="description"
          className="premium-input w-full min-h-[120px] resize-none !bg-surface-dark/40"
          placeholder="What are the key details for this task?"
          disabled={isLoading}
          {...register("description")}
        />
        {errors.description && (
          <p className="text-[10px] text-red-500 font-bold ml-1 italic uppercase tracking-wider" role="alert">
            {errors.description.message}
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div className="space-y-1.5">
          <Label htmlFor="priority" className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 ml-1 italic">Priority Level</Label>
          <Select
            id="priority"
            className="premium-input w-full appearance-none"
            options={[
              { value: "low", label: "Low Priority" },
              { value: "medium", label: "Medium Priority" },
              { value: "high", label: "High Priority" },
            ]}
            disabled={isLoading}
            {...register("priority")}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="categoryId" className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 ml-1 italic">Category</Label>
          <Select
            id="categoryId"
            className="premium-input w-full appearance-none"
            options={[
              { value: "", label: "No Category" },
              ...categories.map(c => ({ value: c.id, label: c.name }))
            ]}
            disabled={isLoading}
            {...register("categoryId")}
          />
        </div>

        <div className="space-y-1.5 sm:col-span-2">
          <Label htmlFor="dueDate" className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 ml-1 italic">Target Date</Label>
          <Input
            id="dueDate"
            type="date"
            className="premium-input w-full [color-scheme:dark]"
            disabled={isLoading}
            {...register("dueDate")}
          />
        </div>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="tags" className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 ml-1 italic">Tags</Label>
        <TagInput
          selectedTags={selectedTags}
          onTagsChange={(tags) => setSelectedTags(tags)}
          availableTags={availableTags}
          onCreateTag={createTag}
        />
      </div>

      {!task && (
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-primary-500/5 rounded-xl border border-primary-500/10">
            <div className="flex flex-col">
              <span className="text-xs font-black uppercase text-white italic tracking-tighter">Due Date Reminder</span>
              <span className="text-[10px] text-primary-50/20 font-medium italic">Receive a notification before deadline</span>
            </div>
            <Switch
              checked={hasReminder}
              onCheckedChange={setHasReminder}
            />
          </div>

          {hasReminder && (
            <ReminderConfig
              offsets={reminderOffsets}
              onChange={setReminderOffsets}
            />
          )}

          <div className="flex items-center justify-between p-4 bg-primary-500/5 rounded-xl border border-primary-500/10">
            <div className="flex flex-col">
              <span className="text-xs font-black uppercase text-white italic tracking-tighter">Enable Recurrence</span>
              <span className="text-[10px] text-primary-50/20 font-medium italic">Automate this directive periodically</span>
            </div>
            <Switch
              checked={isRecurring}
              onCheckedChange={setIsRecurring}
            />
          </div>

          {isRecurring && (
            <RecurringSettings
              frequency={recurringSettings.frequency}
              interval={recurringSettings.interval}
              endDate={recurringSettings.endDate}
              onChange={(s) => setRecurringSettings({
                frequency: s.frequency,
                interval: s.interval,
                endDate: s.endDate
              })}
            />
          )}
        </div>
      )}

      <div className="flex justify-end gap-3 pt-6 border-t border-primary-500/10">
        {onCancel && (
          <Button
            type="button"
            variant="ghost"
            onClick={onCancel}
            className="hover:bg-primary-500/10 rounded-xl text-primary-400 font-black uppercase tracking-widest text-[10px] italic"
            disabled={isLoading}
          >
            Abort
          </Button>
        )}
        <Button type="submit" className="premium-button bg-primary-600 text-white hover:bg-primary-500 px-12 italic" disabled={isLoading}>
          {isLoading
            ? (
              <div className="flex items-center space-x-2">
                <span className="w-1 h-1 bg-white rounded-full animate-bounce"></span>
                <span className="w-1 h-1 bg-white rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-1 h-1 bg-white rounded-full animate-bounce [animation-delay:-0.3s]"></span>
              </div>
            )
            : task
              ? "Sync Changes"
              : "Launch Task"}
        </Button>
      </div>
    </form>
  );
}
