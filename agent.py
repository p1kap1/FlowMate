import json

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL
from skills import FUNCTION_DEFINITIONS, execute_skill

_client_kwargs = {"api_key": OPENAI_API_KEY}
if OPENAI_BASE_URL:
    _client_kwargs["base_url"] = OPENAI_BASE_URL

client = OpenAI(**_client_kwargs)

SYSTEM_PROMPT = """你是一个工作记录助手。你可以帮助用户完成以下任务：
1. 添加工作记录（日期、描述、耗时、分类）
2. 按日期列出工作记录
3. 汇总指定日期范围内的工作记录
4. 生成周报
5. 分析时间分配
6. 基于记录给出改进建议
7. 按关键词搜索记录

当用户请求这些操作时，请调用对应的函数。对于添加记录，如果用户没有指定日期，默认使用今天。
回应请使用中文，简洁明了。"""


class WorkAgent:
    def __init__(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def chat(self, user_message: str) -> str:
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
                result = execute_skill(name, args)
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
            return final_msg.content or ""

        self.messages.append(msg)
        return msg.content or ""

    def reset(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
