import asyncio
import logging
from typing import List, Dict, Any, Optional

from magda_agent.agents.sub_agent import SubAgent
from magda_agent.llm_client import LLMClient

class TeamManager:
    """
    Manages the execution of multiple sub-agents in parallel using git worktree isolation.
    Inspired by Claude Agent Teams and Hermes parallel sub-agents.
    """
    def __init__(self, llm: LLMClient, max_concurrency: int = 5):
        """
        Initializes the TeamManager with an LLM client and optional concurrency limit.

        Args:
            llm (LLMClient): The LLM client to be used by spawned sub-agents.
            max_concurrency (int): Maximum number of sub-agents to run in parallel. Defaults to 5.
        """
        self.llm = llm
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def spawn_and_execute(
        self,
        tasks: List[Dict[str, Any]],
        context: str,
        use_isolation: bool = True
    ) -> List[str]:
        """
        Executes a list of tasks concurrently by spawning isolated SubAgents.

        Each task is executed in its own SubAgent. If use_isolation is True,
        each SubAgent will use a separate git worktree.

        Args:
            tasks (List[Dict[str, Any]]): A list of task specifications.
                Each spec should have a 'description'.
            context (str): The shared context to provide to all sub-agents.
            use_isolation (bool): Whether to use git worktree isolation for sub-agents.

        Returns:
            List[str]: A list of result strings from each sub-agent, in the same order as tasks.
                If a sub-agent fails, the error message is included as the result.
        """
        logging.info(f"TeamManager spawning {len(tasks)} sub-agents (isolation={use_isolation}).")

        async def _run_task_with_semaphore(task_spec: Dict[str, Any]) -> str:
            async with self.semaphore:
                sub_agent = SubAgent(llm=self.llm, use_isolation=use_isolation)
                task_desc = task_spec.get('description', 'Unknown task')
                try:
                    return await sub_agent.execute(task=task_desc, context=context)
                except Exception as e:
                    logging.error(f"Error in TeamManager sub-agent execution: {e}")
                    return f"Error: {e}"

        # Execute all tasks concurrently, respecting the semaphore
        results = await asyncio.gather(*(_run_task_with_semaphore(task) for task in tasks))
        return list(results)
