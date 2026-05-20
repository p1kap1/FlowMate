import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")

_client_kwargs = {"api_key": OPENAI_API_KEY}
if OPENAI_BASE_URL:
    _client_kwargs["base_url"] = OPENAI_BASE_URL
client = OpenAI(**_client_kwargs)
