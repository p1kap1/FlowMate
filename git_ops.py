"""Git 操作模块 —— 推送项目更新到 GitHub"""

import subprocess
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def _run(cmd: list[str]) -> tuple[int, str, str]:
    r = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def git_push(commit_message: str) -> str:
    """add → commit → push，自动处理未配置的 git 信息"""

    # 检查是否 git 仓库
    ret, _, err = _run(["git", "status"])
    if ret != 0:
        return f"❌ 当前目录不是 Git 仓库：{err}"

    # 检查 user.name
    ret, name, _ = _run(["git", "config", "user.name"])
    if not name:
        return "❌ 未配置 git user.name，请先执行：\n```bash\ngit config user.name \"你的名字\"\n```"

    # 检查是否有远程仓库
    ret, remote, err = _run(["git", "remote", "get-url", "origin"])
    if ret != 0:
        return f"❌ 未配置远程仓库 origin，请先执行：\n```bash\ngit remote add origin <url>\n```"

    # 检查是否有改动
    ret, changes, _ = _run(["git", "status", "--porcelain"])
    if not changes:
        return "ℹ️ 没有需要提交的改动，工作区已是最新。"

    # add
    ret, _, err = _run(["git", "add", "-A"])
    if ret != 0:
        return f"❌ git add 失败：{err}"

    # commit
    ret, _, err = _run(["git", "commit", "-m", commit_message])
    if ret != 0:
        return f"❌ git commit 失败：{err}"

    # push（尝试 push，如果失败给出凭据提示）
    ret, out, err = _run(["git", "push", "-u", "origin", "HEAD"])
    if ret != 0:
        # 解析常见错误
        merged = (out + "\n" + err).lower()
        if "authentication" in merged or "could not read" in merged or "terminal" in merged:
            return (
                "❌ GitHub 认证失败，请配置凭据：\n\n"
                f"```bash\n"
                f"# 方式1：用 Token\n"
                f"git remote set-url origin https://TOKEN@github.com/你的用户名/仓库.git\n\n"
                f"# 方式2：用 SSH\n"
                f"git remote set-url origin git@github.com:你的用户名/仓库.git\n\n"
                f"# 方式3：缓存凭据\n"
                f"git config credential.helper store\n"
                f"```"
            )
        if "permission denied" in merged or "403" in merged:
            return "❌ GitHub 推送被拒（403），检查远程仓库权限或 Token 是否有效。"
        return f"❌ git push 失败：\n{err}\n{out}"

    # 成功
    _, log, _ = _run(["git", "log", "-1", "--oneline"])
    return f"✅ 已推送到 {remote.strip()}\n\n提交：{log}"


def git_status() -> str:
    """查看当前仓库状态"""
    ret, out, err = _run(["git", "status", "--short"])
    if ret != 0:
        return f"Git 状态获取失败：{err}"
    if not out:
        return "工作区干净，没有待提交的改动。"
    changed = len([l for l in out.split("\n") if l.strip()])
    return f"待提交的改动（{changed} 个文件）：\n{out}"
