import json
import os
from datetime import date, datetime

from config import client, OPENAI_MODEL
from skills import FUNCTION_DEFINITIONS, execute_skill
import storage

DEBUG_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "debug.log")
RULES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules.md")


def _debug(msg: str):
    with open(DEBUG_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")


def _load_system_prompt() -> str:
    """从 rules.md 热加载系统提示，{{today}} 替换为当前日期"""
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "你是 FlowMate，一个工作日志助手。今天的日期是 {{today}}。"
    return content.replace("{{today}}", date.today().isoformat())


class WorkAgent:
    def __init__(self):
        self.messages = [{"role": "system", "content": _load_system_prompt()}]

    def chat(self, user_message: str) -> str:
        # 记录用户消息
        storage.append_conversation("user", user_message)

        self.messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=self.messages,
            tools=FUNCTION_DEFINITIONS,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            self.messages.append(msg)

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                _debug(f"CALL {name}({json.dumps(args, ensure_ascii=False)})")
                result = execute_skill(name, args)
                _debug(f"RESULT {name}: {result[:200]}")
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            final_response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=self.messages,
            )
            final_msg = final_response.choices[0].message
            self.messages.append(final_msg)
            reply = final_msg.content or ""
            storage.append_conversation("assistant", reply)
            return reply

        reply = msg.content or ""
        self.messages.append(msg)
        storage.append_conversation("assistant", reply)
        return reply

    def reset(self):
        self.messages = [{"role": "system", "content": _load_system_prompt()}]
