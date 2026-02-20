export type TaskStatus = "pending" | "in_progress" | "completed" | "archived";
export type TaskPriority = "low" | "medium" | "high";
export type Priority = TaskPriority;

export interface Tag {
  id: string;
  name: string;
  color: string;
  userId: string;
  createdAt: string;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  categoryId?: string;
  category?: Category;
  tags?: Tag[];
  dueDate?: string;
  completedAt?: string;
  createdAt: string;
  updatedAt: string;
  userId: string;
  recurrenceSeriesId?: string;
}

export interface Category {
  id: string;
  name: string;
  color?: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  priority?: TaskPriority;
  categoryId?: string;
  dueDate?: string;
  tag_ids?: string[];
  is_recurring?: boolean;
  recurrence?: {
    frequency: string;
    interval: number;
    endDate?: string;
  };
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  categoryId?: string;
  dueDate?: string;
}

export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  categoryId?: string;
  search?: string;
  dueDate?: string;
  sortBy?: "createdAt" | "updatedAt" | "dueDate" | "priority";
  sortOrder?: "asc" | "desc";
  page?: number;
  limit?: number;
}

export interface RecurringTaskSeries {
  id: string;
  userId: string;
  title: string;
  description?: string;
  priority: TaskPriority;
  categoryId?: string;
  frequency: string;
  interval: number;
  startDate: string;
  endDate?: string;
  paused: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateRecurringSeriesRequest {
  title: string;
  description?: string;
  priority?: TaskPriority;
  categoryId?: string;
  frequency: string;
  interval: number;
  startDate?: string;
  endDate?: string;
}

export interface TaskResponse {
  task: Task;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  page?: number;
  limit?: number;
  totalPages?: number;
}
