import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from magda_agent.agents.teams import TeamManager
from magda_agent.llm_client import LLMClient

@pytest.mark.asyncio
async def test_team_manager_parallel_execution() -> None:
    """Tests that TeamManager executes tasks in parallel."""
    llm_mock = MagicMock(spec=LLMClient)
    # Set max_concurrency to 2 for the test
    manager = TeamManager(llm=llm_mock, max_concurrency=2)

    tasks = [
        {"description": "Parallel Task 1"},
        {"description": "Parallel Task 2"}
    ]

    # We want to verify that they actually run concurrently.
    # We'll make the mock execute wait a bit.

    start_event = asyncio.Event()

    async def slow_execute(task, context):
        if task == "Parallel Task 1":
            start_event.set()
        else:
            # Wait for task 1 to start
            await start_event.wait()
        await asyncio.sleep(0.1)
        return f"Result for {task}"

    with patch('magda_agent.agents.teams.SubAgent') as MockSubAgent:
        sub_mock_1 = MagicMock()
        sub_mock_1.execute = AsyncMock(side_effect=slow_execute)
        sub_mock_2 = MagicMock()
        sub_mock_2.execute = AsyncMock(side_effect=slow_execute)

        MockSubAgent.side_effect = [sub_mock_1, sub_mock_2]

        import time
        start_time = time.time()
        results = await manager.spawn_and_execute(tasks, context="Shared context")
        end_time = time.time()

        assert results == ["Result for Parallel Task 1", "Result for Parallel Task 2"]
        # If they were sequential, it would take at least 0.2s.
        # In parallel, it should take around 0.1s + overhead.
        assert end_time - start_time < 0.18

@pytest.mark.asyncio
async def test_team_manager_concurrency_limit() -> None:
    """Tests that TeamManager respects the max_concurrency limit."""
    llm_mock = MagicMock(spec=LLMClient)
    # Concurrency limit of 1 (forces sequential execution)
    manager = TeamManager(llm=llm_mock, max_concurrency=1)

    tasks = [
        {"description": "Task A"},
        {"description": "Task B"}
    ]

    async def slow_execute(task, context):
        await asyncio.sleep(0.1)
        return f"Result for {task}"

    with patch('magda_agent.agents.teams.SubAgent') as MockSubAgent:
        sub_mock_1 = MagicMock()
        sub_mock_1.execute = AsyncMock(side_effect=slow_execute)
        sub_mock_2 = MagicMock()
        sub_mock_2.execute = AsyncMock(side_effect=slow_execute)

        MockSubAgent.side_effect = [sub_mock_1, sub_mock_2]

        import time
        start_time = time.time()
        results = await manager.spawn_and_execute(tasks, context="Shared context")
        end_time = time.time()

        assert results == ["Result for Task A", "Result for Task B"]
        # With concurrency 1, it MUST take at least 0.2s
        assert end_time - start_time >= 0.2

@pytest.mark.asyncio
async def test_team_manager_error_handling() -> None:
    """Tests that TeamManager handles sub-agent failures gracefully."""
    llm_mock = MagicMock(spec=LLMClient)
    manager = TeamManager(llm=llm_mock)

    tasks = [
        {"description": "Failing Task"},
        {"description": "Succeeding Task"}
    ]

    with patch('magda_agent.agents.teams.SubAgent') as MockSubAgent:
        sub_mock_1 = MagicMock()
        sub_mock_1.execute = AsyncMock(side_effect=RuntimeError("Sub-agent crashed"))
        sub_mock_2 = MagicMock()
        sub_mock_2.execute = AsyncMock(return_value="Success Result")

        MockSubAgent.side_effect = [sub_mock_1, sub_mock_2]

        results = await manager.spawn_and_execute(tasks, context="Context")

        assert "Error: Sub-agent crashed" in results[0]
        assert results[1] == "Success Result"
