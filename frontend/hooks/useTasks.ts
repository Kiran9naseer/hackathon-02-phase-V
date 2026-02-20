import { useState, useCallback } from "react";
import { taskApi } from "@/lib/api/tasks";
import apiClient from "@/lib/api/client";
import { useSession } from "@/lib/auth/provider";
import type { Task, CreateTaskRequest, UpdateTaskRequest, TaskFilters } from "@/types/task";

interface UseTasksReturn {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  fetchTasks: (filters?: TaskFilters) => Promise<void>;
  createTask: (data: CreateTaskRequest) => Promise<Task>;
  updateTask: (id: string, data: UpdateTaskRequest) => Promise<Task>;
  deleteTask: (id: string) => Promise<void>;
  completeTask: (id: string) => Promise<Task>;
  setTasks: (tasks: Task[]) => void;
  clearError: () => void;
}

export function useTasks(): UseTasksReturn {
  const { isAuthenticated } = useSession();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async (filters?: TaskFilters): Promise<void> => {
    if (!isAuthenticated) {
      console.log("Skipping fetchTasks: User not authenticated");
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await taskApi.getAll(filters);
      // Ensure response.tasks exists, otherwise default to empty array to prevent map error
      setTasks(response?.tasks || []);
    } catch (err: any) {
      // If it's a 401 during logout transition, we might want to be silent
      // But for now, just set the error state and DON'T throw
      const message = err.response?.data?.detail || err.message || "Failed to fetch tasks";
      setError(message);
      console.error("fetchTasks failed:", err);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  const createTask = useCallback(async (data: CreateTaskRequest): Promise<Task> => {
    setError(null);
    try {
      if (data.is_recurring && data.recurrence) {
        // Handle recurring task creation via series endpoint
        const response = await apiClient.post("/api/v1/recurring/", {
          title: data.title,
          description: data.description,
          priority: data.priority,
          category_id: data.categoryId,
          frequency: data.recurrence.frequency,
          interval: data.recurrence.interval,
          end_date: data.recurrence.endDate
        });
        
        // After creating series, fetch tasks to get the first instance
        await fetchTasks();
        // Return a dummy task or the first one from list (slightly hacky for return type)
        return {} as Task; 
      } else {
        const task = await taskApi.create(data);
        setTasks((prev) => [task, ...prev]);
        return task;
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create task";
      setError(message);
      throw err;
    }
  }, [fetchTasks]);

  const updateTask = useCallback(async (id: string, data: UpdateTaskRequest): Promise<Task> => {
    setError(null);
    try {
      const task = await taskApi.update(id, data);
      setTasks((prev) => prev.map((t) => (t.id === id ? task : t)));
      return task;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to update task";
      setError(message);
      throw err;
    }
  }, []);

  const deleteTask = useCallback(async (id: string): Promise<void> => {
    setError(null);
    try {
      await taskApi.delete(id);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to delete task";
      setError(message);
      throw err;
    }
  }, []);

  const completeTask = useCallback(async (id: string): Promise<Task> => {
    setError(null);
    try {
      const task = await taskApi.complete(id);
      setTasks((prev) => prev.map((t) => (t.id === id ? task : t)));
      return task;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to complete task";
      setError(message);
      throw err;
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    tasks,
    isLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    completeTask,
    setTasks,
    clearError,
  };
}
