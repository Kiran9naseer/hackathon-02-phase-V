import logging
import re
import os
import json
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.services.task_service import TaskService
from app.dependencies.database import SessionLocal

logger = logging.getLogger(__name__)

# ─── Gemini Setup ──────────────────────────────────────────────────────────────
# Do NOT cache None — allow retry on each request if loading failed
_gemini_model = None
_gemini_model_loaded = False

def _get_gemini_model():
    """Lazy-load Gemini model. Returns None if API key is not set or model fails."""
    global _gemini_model, _gemini_model_loaded
    
    # Return cached successful model
    if _gemini_model_loaded and _gemini_model is not None:
        return _gemini_model
    
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        logger.warning("GEMINI_API_KEY not set, chatbot will use rule-based fallback.")
        return None
    
    # Try models in order of preference
    model_candidates = [
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-1.5-flash",
    ]
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        for model_name in model_candidates:
            try:
                # Initialize model without a validation ping to save quota
                candidate = genai.GenerativeModel(model_name)
                _gemini_model = candidate
                _gemini_model_loaded = True
                logger.info(f"Gemini AI model '{model_name}' configured successfully.")
                return _gemini_model
            except Exception as model_err:
                logger.warning(f"Failed to create model '{model_name}': {model_err}")
                continue
                
        logger.error("Could not initialize any Gemini model candidates.")
        return None
            
    except Exception as e:
        logger.warning(f"Failed to configure Gemini SDK: {e}")
        return None


GEMINI_SYSTEM_PROMPT = """You are a smart task management assistant. Analyze the user's message and respond in JSON.

Rules:
1. Determine the intent: "add_task", "list_tasks", "complete_task", "delete_task", "web_search", "get_weather", or "chat"
2. For "add_task": extract the task title from the message
3. For "complete_task" or "delete_task": extract the task title/reference
4. For "web_search": extract the search query
5. For "get_weather": extract the city/location
6. For "list_tasks" or "chat": just respond naturally

ALWAYS respond with valid JSON in this exact format:
{
  "intent": "add_task" | "list_tasks" | "complete_task" | "delete_task" | "web_search" | "get_weather" | "chat",
  "task_title": "<extracted title/query/location if applicable, else null>",
  "response": "<your natural, friendly response in the same language the user used>"
}

Examples:
- User: "add task buy milk" → {"intent": "add_task", "task_title": "buy milk", "response": "✅ I've added 'buy milk' to your tasks!"}
- User: "search latest tech news" → {"intent": "web_search", "task_title": "latest tech news", "response": "Searching for latest tech news..."}
- User: "Karachi ka mousam kaisa hai?" → {"intent": "get_weather", "task_title": "Karachi", "response": "Karachi ka mousam check kar raha hoon..."}
- User: "hello" → {"intent": "chat", "task_title": null, "response": "Hello! I'm your task assistant. How can I help you today?"}
"""


async def _call_gemini(message: str, history: List[Dict[str, str]]) -> Optional[Dict]:
    """Call Gemini API and parse the JSON response."""
    model = _get_gemini_model()
    if not model:
        return None
    
    try:
        # Build context from history (last 6 messages)
        context = ""
        for h in history[-6:]:
            role = h.get("role", "user")
            content = h.get("content", "")
            context += f"{role}: {content}\n"
        
        prompt = f"{GEMINI_SYSTEM_PROMPT}\n\nConversation history:\n{context}\nUser: {message}"
        
        response = model.generate_content(prompt)
        raw = response.text.strip()
        
        # Strip markdown code blocks if present
        if raw.startswith("```"):
            raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()
        
        parsed = json.loads(raw)
        return parsed
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Gemini API call failed: {error_msg}")
        
        # Reset loaded state so we retry configuration on next attempt
        global _gemini_model_loaded
        _gemini_model_loaded = False
        
        # Determine error type for fallback warning
        warning = None
        if "401" in error_msg or "API_KEY_INVALID" in error_msg:
            warning = "⚠️ AI Warning: Invalid GEMINI_API_KEY. Falling back to simple mode."
        elif "429" in error_msg or "QUOTA_EXCEEDED" in error_msg:
            warning = "⚠️ AI Warning: Gemini quota exceeded. Falling back to simple mode."
        
        if warning:
            return {"is_fallback": True, "error_warning": warning}
        
        return None


# ─── Rule-based fallback ────────────────────────────────────────────────────────
def _rule_based_intent(message: str) -> Dict:
    """Simple regex-based intent detection as fallback."""
    message_lc = message.lower()
    
    add_match = re.search(
        r"(?:add|create|remember|new|remind)(?:\s+(?:a|the))?(?:\s+task)?(?:\s+to)?\s+(.+)",
        message_lc, re.IGNORECASE
    )
    if add_match:
        title = add_match.group(1).strip()
        if title.lower().startswith("to "):
            title = title[3:].strip()
        return {"intent": "add_task", "task_title": title, "response": None}
    
    if any(k in message_lc for k in ["list", "show", "what", "tasks", "get", "dikhao", "dekho"]):
        return {"intent": "list_tasks", "task_title": None, "response": None}
    
    return {"intent": "chat", "task_title": None, "response": None}


class TaskManagerAgent:
    """
    Agent responsible for understanding user intent and managing tasks.
    Uses Gemini AI when available, falls back to rule-based logic.
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
        decision = {
            "response": "",
            "tool_calls": [],
            "action": None,
            "parameters": {},
            "requires_action_agent": False
        }

        task_service = TaskService(db, user_id)

        try:
            # ── 1. Get intent (Gemini first, then rule-based fallback) ──────────
            gemini_result = await _call_gemini(message, history)
            
            error_warning = None
            if gemini_result and gemini_result.get("is_fallback"):
                error_warning = gemini_result.get("error_warning")
                gemini_result = None

            if gemini_result and "intent" in gemini_result:
                intent = gemini_result.get("intent", "chat")
                task_title = gemini_result.get("task_title")
                ai_response = gemini_result.get("response", "")
                logger.info(f"Gemini intent: {intent}, title: {task_title}")
            else:
                # Fallback to rule-based
                fallback = _rule_based_intent(message)
                intent = fallback["intent"]
                task_title = fallback["task_title"]
                # Start response with warning if present
                ai_response = f"{error_warning}\n\n" if error_warning else None
                logger.info(f"Rule-based intent: {intent}")

            # ── 2. Execute action based on intent ───────────────────────────────
            if intent == "add_task" and task_title:
                tool_call = {
                    "id": "tc_add_" + str(user_id)[:8],
                    "name": "add_task",
                    "input": {"title": task_title},
                    "status": "completed"
                }
                try:
                    from app.schemas.task_schema import TaskCreate
                    from app.models.task import TaskPriority, TaskStatus

                    task_data = TaskCreate(
                        title=task_title,
                        priority=TaskPriority.MEDIUM,
                        status=TaskStatus.PENDING
                    )
                    new_task = task_service.create(task_data)
                    tool_call["result"] = {"id": str(new_task.id), "title": new_task.title}
                    msg = f"✅ Task added: '{new_task.title}'"
                    decision["response"] = f"{ai_response}{msg}" if ai_response else msg
                except Exception as e:
                    logger.error(f"Failed to add task: {e}")
                    tool_call["status"] = "failed"
                    tool_call["result"] = {"error": str(e)}
                    decision["response"] = "I'm sorry, I encountered an error while adding that task."

                decision["tool_calls"].append(tool_call)
                decision["action"] = "add_task"
                decision["parameters"] = {"title": task_title}
                decision["requires_action_agent"] = True

            elif intent == "web_search" and task_title:
                try:
                    from app.services.external_api_service import ExternalApiService
                    search_results = await ExternalApiService.search_web(task_title)
                    decision["response"] = f"{ai_response}\n\n{search_results}" if ai_response else search_results
                    decision["action"] = "web_search"
                except Exception as e:
                    logger.error(f"Web search failed: {e}")
                    decision["response"] = "I had trouble searching the web. Please try again later."

            elif intent == "get_weather" and task_title:
                try:
                    from app.services.external_api_service import ExternalApiService
                    weather_info = await ExternalApiService.get_weather(task_title)
                    decision["response"] = f"{ai_response}\n\n{weather_info}" if ai_response else weather_info
                    decision["action"] = "get_weather"
                except Exception as e:
                    logger.error(f"Weather fetch failed: {e}")
                    decision["response"] = "I couldn't get the weather info right now."

            elif intent == "list_tasks":
                try:
                    tasks_info = task_service.list(limit=10)
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
                        msg = f"Here are your tasks:\n{task_list}"
                        decision["response"] = f"{ai_response}{msg}" if ai_response else msg
                    else:
                        msg = "You don't have any tasks yet. Add one by saying 'add task <title>'!"
                        decision["response"] = f"{ai_response}{msg}" if ai_response else msg

                    decision["tool_calls"].append(tool_call)
                    decision["action"] = "list_tasks"
                    decision["requires_action_agent"] = True
                except Exception as e:
                    logger.error(f"Failed to list tasks: {e}")
                    decision["response"] = "I had trouble retrieving your tasks. Please try again."

            else:
                # General chat or unrecognized intent
                msg = (
                    "I'm your Todo Assistant! You can:\n"
                    "• Add tasks: 'add task buy groceries'\n"
                    "• View tasks: 'show my tasks'"
                )
                decision["response"] = f"{ai_response}{msg}" if ai_response else msg
                decision["action"] = "chat"
                decision["requires_action_agent"] = False

        except Exception as e:
            logger.error(f"Unexpected error in TaskManagerAgent: {e}")
            decision["response"] = "Oops, something went wrong. Please try again."

        return decision
