import pytest
import os
import shutil
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from magda_agent.agents.teams import TeamManager
from magda_agent.llm_client import LLMClient
from magda_agent.isolation.git_worktree import GitWorktreeManager

@pytest.fixture
def mock_llm():
    return MagicMock(spec=LLMClient)

@pytest.mark.asyncio
async def test_team_manager_merge_success(mock_llm):
    """Tests successful merging of changes from multiple sub-agents."""
    manager = TeamManager(llm=mock_llm)

    tasks = [{"description": "Modify file A"}, {"description": "Modify file B"}]
    context = "Project context"

    with patch('magda_agent.agents.teams.SubAgent') as MockSubAgent:
        sub1 = MagicMock()
        sub1.execute = AsyncMock(return_value="Task A done")
        sub1.worktree_path = "/tmp/wt1"
        sub1.branch_name = "task_wt1"
        sub1.worktree_manager = MagicMock(spec=GitWorktreeManager)
        sub1.worktree_manager.commit_changes_async = AsyncMock()
        sub1.worktree_manager.merge_changes_async = AsyncMock()
        sub1.worktree_manager.remove_worktree_async = AsyncMock()

        sub2 = MagicMock()
        sub2.execute = AsyncMock(return_value="Task B done")
        sub2.worktree_path = "/tmp/wt2"
        sub2.branch_name = "task_wt2"
        sub2.worktree_manager = MagicMock(spec=GitWorktreeManager)
        sub2.worktree_manager.commit_changes_async = AsyncMock()
        sub2.worktree_manager.merge_changes_async = AsyncMock()
        sub2.worktree_manager.remove_worktree_async = AsyncMock()

        MockSubAgent.side_effect = [sub1, sub2]

        results = await manager.spawn_and_execute(tasks, context, use_isolation=True, merge_results=True)

        assert results == ["Task A done", "Task B done"]

        # Verify commit and merge were called for both
        sub1.worktree_manager.commit_changes_async.assert_awaited_once()
        sub1.worktree_manager.merge_changes_async.assert_awaited_once_with("task_wt1")
        sub1.worktree_manager.remove_worktree_async.assert_awaited_once_with("/tmp/wt1")

        sub2.worktree_manager.commit_changes_async.assert_awaited_once()
        sub2.worktree_manager.merge_changes_async.assert_awaited_once_with("task_wt2")
        sub2.worktree_manager.remove_worktree_async.assert_awaited_once_with("/tmp/wt2")

@pytest.mark.asyncio
async def test_team_manager_merge_conflict(mock_llm):
    """Tests detection and reporting of a git merge conflict."""
    manager = TeamManager(llm=mock_llm)

    tasks = [{"description": "Conflicting task"}]
    context = "Project context"

    with patch('magda_agent.agents.teams.SubAgent') as MockSubAgent:
        sub = MagicMock()
        sub.execute = AsyncMock(return_value="Task done with conflicts")
        sub.worktree_path = "/tmp/wt_conflict"
        sub.branch_name = "task_conflict"
        sub.worktree_manager = MagicMock(spec=GitWorktreeManager)
        sub.worktree_manager.commit_changes_async = AsyncMock()
        sub.worktree_manager.merge_changes_async = AsyncMock(side_effect=RuntimeError("Merge conflict in file.txt"))
        sub.worktree_manager.remove_worktree_async = AsyncMock()

        MockSubAgent.return_value = sub

        results = await manager.spawn_and_execute(tasks, context, use_isolation=True, merge_results=True)

        assert "Merge Error: Merge conflict in file.txt" in results[0]
        sub.worktree_manager.remove_worktree_async.assert_awaited_once()

@pytest.mark.asyncio
async def test_git_worktree_manager_real_git(tmp_path):
    """Tests GitWorktreeManager with real git operations in a temp repo."""
    # 1. Initialize a real git repo
    repo_dir = tmp_path / "main_repo"
    repo_dir.mkdir()

    async def run(cmd, cwd=repo_dir):
        proc = await asyncio.create_subprocess_exec(*cmd, cwd=cwd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        return await proc.communicate()

    await run(["git", "init"])
    # Need at least one commit to use git worktree add
    (repo_dir / "init.txt").write_text("initial")
    await run(["git", "add", "."])
    await run(["git", "config", "user.email", "you@example.com"])
    await run(["git", "config", "user.name", "Your Name"])
    await run(["git", "commit", "-m", "initial commit"])

    manager = GitWorktreeManager(base_dir=str(tmp_path / "worktrees"))

    # 2. Create worktree
    # We need to run this from the repo root
    with patch('magda_agent.isolation.git_worktree.os.getcwd', return_value=str(repo_dir)):
        import os
        old_cwd = os.getcwd()
        os.chdir(str(repo_dir))
        try:
            wt_path, branch = await manager.create_worktree_async()
            assert os.path.exists(wt_path)
            assert branch.startswith("task_")

            # 3. Commit changes in worktree
            with open(os.path.join(wt_path, "new_file.txt"), "w") as f:
                f.write("new content")
            await manager.commit_changes_async(wt_path, "added new file")

            # 4. Merge changes back
            # Find current branch
            proc = await asyncio.create_subprocess_exec("git", "rev-parse", "--abbrev-ref", "HEAD", stdout=asyncio.subprocess.PIPE)
            stdout, _ = await proc.communicate()
            current_branch = stdout.decode().strip()

            await manager.merge_changes_async(branch, target_branch=current_branch)

            assert os.path.exists(repo_dir / "new_file.txt")

            # 5. Cleanup
            await manager.remove_worktree_async(wt_path)
            assert not os.path.exists(wt_path)
        finally:
            os.chdir(old_cwd)
