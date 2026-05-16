# Agent 项目

这是一个 Python 项目。将以下步骤用于把本地仓库推送到 GitHub：

1. 本地初始化并提交（已包含在脚本中）：
   - `git init`
   - `git add .`
   - `git commit -m "Initial commit"`

2. 在 GitHub 上创建远程仓库：
   - 使用 GitHub CLI（推荐）：`gh repo create <OWNER>/<REPO> --public --source=. --remote=origin --push`
   - 或者在网页上创建，然后运行：
     - `git remote add origin git@github.com:OWNER/REPO.git`
     - `git branch -M main`
     - `git push -u origin main`

3. 完成后分享仓库 URL 给我，我可以帮你验证或继续配置 CI。 
