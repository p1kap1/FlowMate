"""Boss直聘爬虫 —— 从四个模块获取投递数据并记录到 applications.json

使用前请先配置 cookie：
  1. 用 Chrome 登录 bosszhipin.com
  2. F12 → Application → Cookies → 复制所有 cookie
  3. 粘贴到 .env 文件中：BROWSER_COOKIE="你的cookie字符串"
"""

import json
import os
from datetime import date

import requests

from config import DATA_DIR, OPENAI_BASE_URL
from storage import _load_jobs, _save_jobs, add_application

BOSS_API = "https://www.zhipin.com"

# 四个模块的 API 路径及对应状态
# 沟通过(tab=1) / 已投递(tab=2) / 面试(tab=3) / 感兴趣(tab=4)
ENDPOINTS = [
    ("沟通过", f"{BOSS_API}/wapi/zpgeek/chat/geek/list.json", {"page": 1, "pageSize": 50}),
    ("已投递", f"{BOSS_API}/wapi/zpgeek/expectation/list.json", {"page": 1, "pageSize": 50}),
    ("面试",   f"{BOSS_API}/wapi/zpgeek/recommend/job/list.json", {"tab": 3, "page": 1, "pageSize": 50}),
    ("感兴趣", f"{BOSS_API}/wapi/zpgeek/desire/list.json", {"page": 1, "pageSize": 50}),
]


def _headers():
    cookie = os.getenv("BROWSER_COOKIE", "")
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": cookie,
        "Referer": "https://www.zhipin.com/web/geek/recommend",
        "Accept": "application/json",
    }


def _fetch_list(endpoint: str, params: dict = None) -> dict:
    """请求 API 并返回 JSON"""
    resp = requests.get(
        endpoint,
        headers=_headers(),
        params=params or {},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"API 错误: {data.get('code')} - {data.get('message', '')}")
    return data


def _parse_jobs(data: dict, status: str) -> list[dict]:
    """从 API 返回的 JSON 中提取公司、岗位信息"""
    results = []
    zp_data = data.get("zpData", {})

    for item in zp_data.get("list", []) or []:
        company = item.get("brandName") or item.get("brandName", "")
        position = item.get("jobName") or item.get("name", "")

        if not company:
            enc_brand = item.get("encryptBrandId") or item.get("encBrandId")
            brand_info = zp_data.get("brandList", {}).get(enc_brand, {})
            company = brand_info.get("brandName", "")

        if not position:
            position = item.get("expectName", "") or item.get("jobTitle", "")

        if company:
            results.append({
                "company": company.strip(),
                "position": position.strip(),
                "status": status,
            })

    platform = item.get("expectName", "")
    if not results:
        for item in zp_data.get("chatList", []) or []:
            company = item.get("brandName", "")
            position = item.get("jobName", "")
            if company:
                results.append({
                    "company": company.strip(),
                    "position": position.strip(),
                    "status": status,
                })

    return results


def fetch_all() -> list[dict]:
    """获取四个模块的全部记录并写入 applications.json"""
    today = date.today().isoformat()
    existing = _load_jobs()
    existing_keys = {(j["company"], j["position"]) for j in existing}

    new_count = 0
    for status, url in ENDPOINTS.items():
        try:
            data = _fetch_list(url)
        except Exception as e:
            print(f"  ⚠ {status} 获取失败: {e}")
            continue

        jobs = _parse_jobs(data, status)
        for job in jobs:
            key = (job["company"], job["position"])
            if key in existing_keys:
                continue  # skip duplicates
            existing_keys.add(key)
            add_application(
                company=job["company"],
                position=job["position"],
                date_str=today,
                status=job["status"],
                platform="Boss直聘",
            )
            new_count += 1

    return {
        "new": new_count,
        "total": len(_load_jobs()),
        "date": today,
    }


if __name__ == "__main__":
    result = fetch_all()
    print(f"同步完成: 新增 {result['new']} 条, 共 {result['total']} 条")
