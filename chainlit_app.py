import chainlit as cl
from agent import WorkAgent


# ---- Python 3.14 + nest_asyncio compat ----
# nest_asyncio._run_once pops the current task before executing callbacks,
# causing asyncio.current_task() to return None. This breaks:
# 1. anyio._core._eventloop.current_async_library() → NoEventLoopError
# 2. anyio._backends._asyncio.CancelScope.__enter__ → TypeError
# 3. asyncio.timeouts.Timeout.__aenter__ → RuntimeError
# 4. engineio.async_server._service_task → RuntimeError

import asyncio as _asyncio
import threading as _threading
import heapq as _heapq

_nest_task = _threading.local()

# ---- Patch 1: Store popped task in thread-local during _run_once ----

def _patch_run_once(loop):
    if getattr(loop, "_nest14_patched", False):
        return

    _orig = loop._run_once

    def _new_run_once(self):
        cur = _asyncio.tasks._current_tasks
        ready = self._ready
        sched = self._scheduled
        while sched and sched[0]._cancelled:
            _heapq.heappop(sched)
        timeout = (
            0 if ready or self._stopping
            else min(max(sched[0]._when - self.time(), 0), 86400)
            if sched else None
        )
        ev = self._selector.select(timeout)
        self._process_events(ev)
        et = self.time() + self._clock_resolution
        while sched and sched[0]._when < et:
            ready.append(_heapq.heappop(sched))
        for _ in range(len(ready)):
            if not ready:
                break
            h = ready.popleft()
            if not h._cancelled:
                t = cur.pop(self, None)
                _nest_task.value = t
                try:
                    h._run()
                finally:
                    if t is not None:
                        cur[self] = t
                    _nest_task.value = None

    loop._run_once = _new_run_once.__get__(loop, type(loop))
    loop._nest14_patched = True

_patch_run_once(_asyncio.get_event_loop())

# ---- Patch 2: current_task never returns None when loop is running ----

_orig_current_task = _asyncio.current_task

def _patched_current_task(loop=None):
    t = _orig_current_task(loop)
    if t is not None:
        return t
    t = getattr(_nest_task, "value", None)
    if t is not None:
        return t
    if loop is None:
        try:
            loop = _asyncio.get_running_loop()
        except RuntimeError:
            return None
    return _asyncio.tasks._current_tasks.get(loop)

_asyncio.current_task = _patched_current_task

import anyio._backends._asyncio as _aba
_aba.current_task = _patched_current_task

# ---- Patch 3: current_async_library fallback ----

import anyio._core._eventloop as _aloop
_orig_alib = _aloop.current_async_library

def _patched_current_async_library():
    r = _orig_alib()
    if r is None:
        try:
            if _asyncio.get_running_loop() is not None:
                return "asyncio"
        except RuntimeError:
            pass
    return r

_aloop.current_async_library = _patched_current_async_library

# ---- Patch 4: CancelScope.__enter__ handles None host_task ----

_orig_cs_enter = _aba.CancelScope.__enter__

def _patched_enter(self):
    if self._active:
        raise RuntimeError(
            "Each CancelScope may only be used for a single 'with' block")
    import anyio._backends._asyncio as _m
    host = _patched_current_task()
    if host is None:
        host = _asyncio.tasks._CTask()  # dummy fallback
    self._host_task = host
    self._tasks.add(host)
    try:
        ts = _m._task_states[host]
    except KeyError:
        ts = _m.TaskState(None, self)
        _m._task_states[host] = ts
    else:
        self._parent_scope = ts.cancel_scope
        ts.cancel_scope = self
        if self._parent_scope is not None:
            self._parent_scope._child_scopes.add(self)
            self._parent_scope._tasks.discard(host)
    self._timeout()
    self._active = True
    if self._cancel_called:
        self._deliver_cancellation(self)
    return self

_aba.CancelScope.__enter__ = _patched_enter

# ---- Patch 5: Timeout.__aenter__ handles None current_task ----

import asyncio.timeouts as _ato
_orig_timeout_enter = _ato.Timeout.__aenter__

async def _patched_timeout_enter(self):
    if self._state is not _ato._State.CREATED:
        raise RuntimeError("Timeout has already been entered")
    task = _patched_current_task()
    if task is None:
        # nest_asyncio popped it; try original one more time
        task = _asyncio.tasks._CTask()
    self._state = _ato._State.ENTERED
    self._task = task
    self._cancelling = task.cancelling()
    self.reschedule(self._when)
    return self

_ato.Timeout.__aenter__ = _patched_timeout_enter
# -------------------------------------------------


@cl.on_chat_start
async def start():
    cl.user_session.set("agent", WorkAgent())
    await cl.Message(
        content="你好！我是工作记录助手。我可以帮你：\n\n"
        "1. **添加记录** — 记录今天做了什么、花了多少时间\n"
        "2. **按日期查看** — 列出某天或全部记录\n"
        "3. **汇总分析** — 统计一段时间的工作情况\n"
        "4. **生成周报** — 自动生成一周工作报告\n"
        "5. **时间分配** — 分析你的时间都去哪了\n"
        "6. **优化建议** — 基于记录给出改进建议\n"
        "7. **关键词搜索** — 快速查找相关记录\n\n"
        "试试说「我今天开发了3小时，写文档1小时」吧！"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    agent: WorkAgent = cl.user_session.get("agent")
    reply = agent.chat(message.content)
    await cl.Message(content=reply).send()
