"""Host-side coding agent for a Zero2Repo solve round."""

import asyncio
import time
from pathlib import Path

from pydantic_ai import Agent, RunUsage
from pydantic_ai.workspaces import WorkspaceRef
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.docker_sandbox import DockerSandboxBackend


async def solve(
    runner,
    model,
    effort,
    container,
    *,
    limits,
    out_dir,
    log_name,
    wall_timeout_sec=None,
    abort=None,
    usage,
    env=None,
):
    started = time.monotonic()
    workspace = DockerSandboxBackend(
        ref=WorkspaceRef(provider="docker", id=container.container_id), working_dir="/app", env=env
    )
    agent = Agent(
        model,
        capabilities=[Coder(repo_context=False, sub_agents=False, unrestricted_filesystem=True)],
        model_settings={"openai_reasoning_effort": effort},
    )
    prompt = Path(out_dir, "current-instruction.md")
    if not container.cp_from(runner.CONTAINER_INSTRUCTION_PATH, prompt):
        raise RuntimeError("could not read native solve instruction")
    run_usage = RunUsage()
    last_activity = started

    async def run():
        nonlocal last_activity
        async with agent.iter(prompt.read_text(), workspace=workspace, usage=run_usage) as session:
            try:
                async for _ in session:
                    last_activity = time.monotonic()
            finally:
                Path(out_dir, log_name).write_bytes(session.all_messages_json())

    task = asyncio.create_task(run())
    deadline = started + (wall_timeout_sec or limits.max_agent_timeout_sec)
    completed = False
    try:
        while not task.done():
            await asyncio.wait([task], timeout=1)
            now = time.monotonic()
            stopped = abort is not None and abort.is_set()
            stalled = bool(
                limits.stall_window_sec and now - last_activity >= limits.stall_window_sec
            )
            if not task.done() and (stopped or stalled or now >= deadline):
                return runner.ExecResult(
                    1,
                    timed_out=now >= deadline,
                    stall_killed=stalled,
                    aborted=stopped,
                    seconds=now - started,
                )
        await task
        completed = True
        return runner.ExecResult(0, seconds=time.monotonic() - started)
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        usage.append(run_usage.total_tokens if completed and run_usage.requests else None)
