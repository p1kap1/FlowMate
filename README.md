# WorkMate Agent

基于 **FastAPI + Chainlit** 的个人工作智能助理，集成了 DeepSeek Function Calling、Boss直聘求职数据同步、日报自动生成、开发简报、文件上传等能力。

## 功能一览

### 📮 求职管理
| 指令 | 功能 |
|------|------|
| `同步投递` | 从 Boss直聘 自动拉取沟通过/已投递/面试/感兴趣四个模块，支持翻页获取全量数据 |
| `投递汇总` | 四模块数据统计，按状态分组展示 |
| `导出Excel` / `导出 2026-02-20 的 Excel` | 生成投递记录表格，企业名和职位名可点击直达，面试单独分区 |

### 📄 日报与总结
| 指令 | 功能 |
|------|------|
| `生成日报` | 今日学习 + 求职进展自动汇总 → Markdown 文件 |
| `项目总结` | 读今天的对话 + devlog.md + 上传文件 → 生成开发简报（新增功能/修复问题/技术难点/解决方案） |

### 📁 文件上传
| 指令 | 功能 |
|------|------|
| 拖拽文件到对话框 | 保存 md/txt 到 `data/uploads/` |
| `导入 XX.md` | 加载上传文件内容参与总结 |
| `导入开发日志` | 加载 `devlog.md` |
| `查看上传文件` | 列出所有已上传文件 |

### 🔧 其他
| 指令 | 功能 |
|------|------|
| `搜索 XXX` | 查找历史对话记录 |
| `提交代码到 GitHub` | `git add + commit + push` 一键推送 |
| `看看 Git 状态` | 查看仓库改动文件 |

## 项目结构

```
agent/
├── config.py              # DeepSeek API 配置
├── storage.py             # JSON 文件持久化（对话、投递、上传文件）
├── boss.py                # Boss直聘 4 模块数据抓取 + 翻页 + 日期解析 + Excel 导出
├── skills.py              # 14 项技能 + OpenAI Function Calling 定义
├── agent.py               # DeepSeek Function Calling Agent 核心
├── git_ops.py             # Git add/commit/push 操作
├── app.py                 # FastAPI 接口
├── chainlit_app.py        # Chainlit 聊天 UI（含 Python 3.14 兼容补丁）
├── scraper.py             # 早期爬虫参考（已弃用，仅保留）
├── users.json             # 多用户配置（含 boss_cookie，已被 .gitignore 排除）
├── devlog.md              # 开发日志（已被 .gitignore 排除）
├── .env.example           # 环境变量模板
└── data/                  # 数据目录（已被 .gitignore 排除）
    ├── conversations/     # 按日对话记录 JSON
    ├── reports/           # 日报 Markdown + Excel 导出
    ├── applications.json  # 投递记录
    ├── uploads/           # 用户上传文件
    └── debug.log          # Agent 技能调用追踪
```

## 技术栈

| 层 | 技术 |
|---|---|
| 对话界面 | Chainlit 2.11 |
| API 服务 | FastAPI + Uvicorn |
| AI 推理 | DeepSeek Chat（OpenAI 兼容 SDK） |
| Agent 调度 | OpenAI Function Calling（tool_choice=auto） |
| 数据存储 | JSON 文件 |
| Excel 导出 | openpyxl |
| 浏览器抓取 | requests + Cookie 认证 |
| 版本管理 | Git + GitHub |

## 快速开始

```bash
# 1. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY

# 4. 配置 Boss直聘 Cookie（可选）
# 编辑 users.json 在 boss_cookie 字段粘贴从浏览器导出的 Cookie

# 5. 启动
chainlit run chainlit_app.py --headless --port 8000
```

## 开发日志

项目通过 `devlog.md` 机制记录开发进展。用户可以通过「导入开发日志」将开发记录加载到 Agent 对话中，再通过「项目总结」生成结构化的开发简报。

## License

MIT
