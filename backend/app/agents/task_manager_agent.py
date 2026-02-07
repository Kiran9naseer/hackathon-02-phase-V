import logging
import re
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.services.task_service import TaskService
from app.dependencies.database import SessionLocal

logger = logging.getLogger(__name__)

class TaskManagerAgent:
    """
    Agent responsible for understanding user intent and managing tasks.
    In this implementation, it uses rule-based logic to simulate an AI's tool-calling behavior.
    """

    @staticmethod
    async def process_message(
        db: Session,
        message: str, 
        history: List[Dict[str, str]], 
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Process user message, determine intent, execute actions via TaskService,
        and return a decision dictionary.
        """
        message_lc = message.lower()
        decision = {
            "response": "",
            "tool_calls": [],
            "action": None,
            "parameters": {},
            "requires_action_agent": False
        }

        # Use TaskService instance
        task_service = TaskService(db, user_id)

        try:
            # Simple Intent Recognition with improved patterns
            
            # 1. ADD TASK
            # Patterns like "add task buy milk", "remember to call mom", "create task: project"
            add_match = re.search(r"(?:add|create|remember|new|remind)(?:\s+(?:a|the))?(?:\s+task)?(?:\s+to)?\s+(.+)", message_lc, re.IGNORECASE)
            
            if add_match:
                title = add_match.group(1).strip()
                # Clean up "to" if it's still at the start
                if title.lower().startswith("to "):
                    title = title[3:].strip()
                
                # Mock tool call structure for frontend compatibility
                tool_call = {
                    "id": "tc_add_" + str(user_id)[:8],
                    "name": "add_task",
                    "input": {"title": title},
                    "status": "completed"
                }
                
                try:
                    from app.schemas.task_schema import TaskCreate
                    from app.models.task import TaskPriority, TaskStatus
                    
                    task_data = TaskCreate(
                        title=title,
                        priority=TaskPriority.MEDIUM,
                        status=TaskStatus.PENDING
                    )
                    new_task = task_service.create(task_data)
                    
                    tool_call["result"] = {"id": str(new_task.id), "title": new_task.title}
                    decision["response"] = f"✅ Success! I've added the task: '{new_task.title}'"
                except Exception as e:
                    logger.error(f"Failed to add task: {e}")
                    tool_call["status"] = "failed"
                    tool_call["result"] = {"error": str(e)}
                    decision["response"] = "I'm sorry, I encountered an error while trying to add that task."

                decision["tool_calls"].append(tool_call)
                decision["action"] = "add_task"
                decision["parameters"] = {"title": title}
                decision["requires_action_agent"] = True

            # 2. LIST TASKS
            elif any(k in message_lc for k in ["list", "show", "what", "tasks", "get"]):
                try:
                    tasks_info = task_service.list(limit=5)
                    tasks = tasks_info.get("tasks", [])
                    
                    tool_call = {
                        "id": "tc_list_" + str(user_id)[:8],
                        "name": "list_tasks",
                        "input": {},
                        "status": "completed",
                        "result": {"count": len(tasks)}
                    }
                    
                    if tasks:
                        task_list = "\n".join([f"• {t.title} [{t.status}]" for t in tasks])
                        decision["response"] = f"Here are your latest tasks:\n{task_list}"
                    else:
                        decision["response"] = "You don't have any tasks in your list yet."
                    
                    decision["tool_calls"].append(tool_call)
                    decision["action"] = "list_tasks"
                    decision["requires_action_agent"] = True
                except Exception as e:
                    logger.error(f"Failed to list tasks: {e}")
                    decision["response"] = "I had some trouble retrieving your tasks. Please try again."

            # 3. FALLBACK / CHAT
            else:
                decision["response"] = "I'm your Todo Assistant! You can tell me things like 'add task buy bread' or 'show my tasks'."
                decision["action"] = "chat"
                decision["requires_action_agent"] = False

        except Exception as e:
            logger.error(f"Unexpected error in TaskManagerAgent: {e}")
            decision["response"] = "Oops, something went wrong on my end."

        return decision
