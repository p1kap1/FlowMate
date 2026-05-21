# FlowMate

基于 **FastAPI + Chainlit** 的个人工作智能助理，集成 DeepSeek Function Calling、多平台求职数据同步（Boss直聘 + 智联招聘）、日报自动生成、项目总结、Excel 导出等能力。

## 功能一览

### 📮 求职管理（Boss直聘 + 智联招聘）

| 指令 | 功能 |
|------|------|
| `同步投递` | 同步全部平台今日投递（Boss: 沟通过/已投递/面试/感兴趣 + 智联: 已投递/收藏） |
| `同步每日推荐` | 同步全部平台今日推荐（Boss + 智联） |
| `同步Boss直聘` | 只同步 Boss 直聘投递数据 |
| `同步智联` | 只同步智联招聘投递数据 |
| `投递汇总` | 全部平台投递统计 |
| `投递表` / `每日推荐表` | 列表展示岗位（最多10条） |
| `导出Excel` | 一次性导出全部平台 Excel |
| `导出BossExcel` / `导出智联Excel` | 单独导出某个平台 |
| `导出每日推荐Excel` | 单独导出推荐数据 |

### 📄 日报与总结

| 指令 | 功能 |
|------|------|
| `生成日报` | 今日投递 + 项目总结 + 开发技巧 + 知识推荐 → Markdown |
| `项目总结` | 读对话 + devlog.md + 上传文件 → 开发简报 |

### ⚙️ 配置管理

| 指令 | 功能 |
|------|------|
| `开始设置` / `查看配置` | 表格化配置中心（模型/Key/Boss/GitHub 状态一目了然） |
| `用DeepSeek` / `用OpenAI` / `用智谱` | 一键切换 AI 模型 |
| `设置Key为sk-xxx` | 配置 API Key |
| `更新Boss Cookie` | 更新指定平台登录态 |
| `设置GitHub Token为ghp_xxx` | 配置代码推送 |
| `切换用户 用户名` | 多用户独立配置 |

**支持的 AI 模型**：DeepSeek、OpenAI、智谱 GLM、Moonshot、自定义（任何兼容 OpenAI 接口的服务）

### 📁 文件上传与版本管理

| 指令 | 功能 |
|------|------|
| 拖拽 md/txt 到对话框 | 自动保存到 `data/uploads/` |
| `导入开发日志` | 加载 `devlog.md` |
| `提交代码到 GitHub` | git add + commit + push 一键推送 |

## 项目结构

```
agent/
├── config.py              # AI 模型配置
├── storage.py             # JSON 持久化（对话/投递/上传/多目录）
├── boss.py                # Boss直聘 5 模块（含每日推荐）+ Excel 导出
├── zhaopin.py             # 智联招聘 3 模块（已投递/收藏/推荐）+ Excel 导出
├── skills.py              # 30+ 项技能 + OpenAI Function Calling 定义
├── agent.py               # Function Calling Agent 核心
├── settings.py            # 模型/Key/Cookie/Token 统一配置管理
├── git_ops.py             # Git 操作
├── chainlit_app.py        # Chainlit UI（含 Python 3.14 兼容补丁、本地设置处理）
├── app.py                 # FastAPI 接口
├── users.json             # 多用户配置（已被 .gitignore 排除）
├── devlog.md              # 开发日志（已被 .gitignore 排除）
├── .env.example           # 环境变量模板（多模型示例）
└── data/                  # 数据目录（已被 .gitignore 排除）
    ├── conversations/     # 按日对话记录 JSON
    ├── applications.json  # 投递记录
    ├── uploads/           # 用户上传文件
    └── reports/
        ├── daily/         # 工作日报 .md
        ├── boss/          # Boss直聘 Excel
        └── zhaopin/       # 智联招聘 Excel
```

## 技术栈

| 层 | 技术 |
|---|---|
| 对话界面 | Chainlit 2.11 |
| AI 推理 | DeepSeek / OpenAI / 智谱 GLM / Moonshot（OpenAI 兼容 SDK） |
| Agent 调度 | OpenAI Function Calling（tool_choice=auto） |
| 数据存储 | JSON 文件（按平台/日期分布） |
| Excel 导出 | openpyxl |
| 浏览器抓取 | requests + Cookie 认证（多端点） |
| 版本管理 | Git + GitHub |

## 快速开始

```bash
# 1. 虚拟环境
python3 -m venv .venv && source .venv/bin/activate

# 2. 安装
pip install -r requirements.txt

# 3. 启动
chainlit run chainlit_app.py --headless --port 8000
```

首次启动会自动弹出引导界面，依次选择模型、设置 API Key 即可使用。Boss直聘/智联招聘同步需要额外配置对应 Cookie。

## 隐私说明

以下敏感文件已通过 `.gitignore` 排除，永远不会提交到 GitHub：

| 文件 | 内容 |
|---|---|
| `.env` | AI API Key、模型选择 |
| `users.json` | Boss直聘/智联 Cookie、多用户配置 |
| `.git/config` | GitHub Token |
| `data/` | 对话记录、投递数据、日报、Excel |
| `devlog.md` | 开发日志 |

## License

MIT
