import asyncio
import logging
import os
import shutil
import uuid
from typing import Optional

class GitWorktreeManager:
    """
    Manages isolated Git worktrees for SubAgents.
    Ensures parallel tasks run in separate file system contexts.
    """
    def __init__(self, base_dir: str = "/tmp/magda_worktrees"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def create_worktree_async(self, branch_name: Optional[str] = None) -> tuple[str, str]:
        """
        Creates a new git worktree. If branch_name is not provided,
        a unique branch name is generated.
        Returns a tuple of (worktree_path, branch_name).
        """
        worktree_id = str(uuid.uuid4())[:8]
        worktree_path = os.path.join(self.base_dir, f"worktree_{worktree_id}")

        if not branch_name:
            branch_name = f"task_{worktree_id}"

        cmd = ["git", "worktree", "add", "-b", branch_name, worktree_path, "HEAD"]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                logging.error(f"Failed to create git worktree: {stderr.decode()}")
                raise RuntimeError(f"Git worktree creation failed: {stderr.decode()}")

            logging.info(f"Created git worktree at {worktree_path} on branch {branch_name}")
            return worktree_path, branch_name
        except Exception as e:
            logging.error(f"Error executing git worktree add: {e}")
            raise

    async def commit_changes_async(self, worktree_path: str, message: str) -> None:
        """
        Commits all changes in the given worktree.
        """
        try:
            # git add .
            add_process = await asyncio.create_subprocess_exec(
                "git", "add", ".",
                cwd=worktree_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await add_process.communicate()

            # git commit -m message
            commit_process = await asyncio.create_subprocess_exec(
                "git", "commit", "-m", message,
                cwd=worktree_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await commit_process.communicate()

            if commit_process.returncode != 0:
                # If there's nothing to commit, it's fine
                if "nothing to commit" in stdout.decode() or "nothing to commit" in stderr.decode():
                    logging.info(f"No changes to commit in {worktree_path}")
                else:
                    logging.error(f"Failed to commit changes in {worktree_path}: {stderr.decode()}")
                    raise RuntimeError(f"Git commit failed: {stderr.decode()}")
            else:
                logging.info(f"Committed changes in {worktree_path} with message: {message}")
        except Exception as e:
            logging.error(f"Error committing changes: {e}")
            raise

    async def merge_changes_async(self, branch_name: str, target_branch: str = "main") -> None:
        """
        Merges changes from the given branch back to the target branch.
        This is executed in the main repository.
        """
        try:
            # Ensure we are on the target branch
            checkout_process = await asyncio.create_subprocess_exec(
                "git", "checkout", target_branch,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await checkout_process.communicate()

            # git merge branch_name
            merge_process = await asyncio.create_subprocess_exec(
                "git", "merge", branch_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await merge_process.communicate()

            if merge_process.returncode != 0:
                logging.error(f"Conflict or error during merge of {branch_name} into {target_branch}: {stderr.decode()}")
                raise RuntimeError(f"Git merge conflict or error: {stderr.decode()}")

            logging.info(f"Successfully merged {branch_name} into {target_branch}")
        except Exception as e:
            logging.error(f"Error merging changes: {e}")
            raise

    async def remove_worktree_async(self, worktree_path: str) -> None:
        """
        Removes a git worktree and deletes its directory.
        """
        cmd = ["git", "worktree", "remove", "--force", worktree_path]
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                logging.error(f"Failed to remove git worktree: {stderr.decode()}")
                # Fallback to manual deletion if git worktree remove fails
                if os.path.exists(worktree_path):
                    shutil.rmtree(worktree_path)
            else:
                 logging.info(f"Removed git worktree at {worktree_path}")
        except Exception as e:
            logging.error(f"Error executing git worktree remove: {e}")
            if os.path.exists(worktree_path):
                shutil.rmtree(worktree_path)
