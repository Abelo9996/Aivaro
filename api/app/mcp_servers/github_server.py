"""GitHub MCP Server — issues, PRs, branches, repos."""
from app.mcp_servers.base import BaseMCPServer


class GitHubMCPServer(BaseMCPServer):
    provider = "github"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.github_service import GitHubService
        self.svc = GitHubService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("github_create_issue", "Create a GitHub issue.", {
            "type": "object",
            "properties": {
                "owner": {"type": "string"}, "repo": {"type": "string"},
                "title": {"type": "string"}, "body": {"type": "string"},
                "labels": {"type": "array", "items": {"type": "string"}},
                "assignees": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["owner", "repo", "title"],
        }, self._create_issue)

        self._register("github_get_issue", "Get a GitHub issue.", {
            "type": "object",
            "properties": {
                "owner": {"type": "string"}, "repo": {"type": "string"},
                "issue_number": {"type": "integer"},
            },
            "required": ["owner", "repo", "issue_number"],
        }, self._get_issue)

        self._register("github_update_issue", "Update a GitHub issue.", {
            "type": "object",
            "properties": {
                "owner": {"type": "string"}, "repo": {"type": "string"},
                "issue_number": {"type": "integer"},
                "title": {"type": "string"}, "body": {"type": "string"},
                "state": {"type": "string", "description": "open or closed"},
                "labels": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["owner", "repo", "issue_number"],
        }, self._update_issue)

        self._register("github_list_issues", "List issues in a GitHub repo.", {
            "type": "object",
            "properties": {
                "owner": {"type": "string"}, "repo": {"type": "string"},
                "state": {"type": "string", "default": "open"},
                "limit": {"type": "integer", "default": 30},
            },
            "required": ["owner", "repo"],
        }, self._list_issues)

        self._register("github_search_issues", "Search GitHub issues across repos.", {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "GitHub search syntax"},
                "limit": {"type": "integer", "default": 30},
            },
            "required": ["query"],
        }, self._search_issues)

        self._register("github_add_labels", "Add labels to a GitHub issue.", {
            "type": "object",
            "properties": {
                "owner": {"type": "string"}, "repo": {"type": "string"},
                "issue_number": {"type": "integer"},
                "labels": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["owner", "repo", "issue_number", "labels"],
        }, self._add_labels)

        self._register("github_create_comment", "Comment on a GitHub issue or PR.", {
            "type": "object",
            "properties": {
                "owner": {"type": "string"}, "repo": {"type": "string"},
                "issue_number": {"type": "integer"},
                "body": {"type": "string"},
            },
            "required": ["owner", "repo", "issue_number", "body"],
        }, self._create_comment)

        self._register("github_create_pr", "Create a GitHub pull request.", {
            "type": "object",
            "properties": {
                "owner": {"type": "string"}, "repo": {"type": "string"},
                "title": {"type": "string"}, "head": {"type": "string"},
                "base": {"type": "string"}, "body": {"type": "string"},
                "draft": {"type": "boolean", "default": False},
            },
            "required": ["owner", "repo", "title", "head", "base"],
        }, self._create_pr)

        self._register("github_list_prs", "List pull requests in a repo.", {
            "type": "object",
            "properties": {
                "owner": {"type": "string"}, "repo": {"type": "string"},
                "state": {"type": "string", "default": "open"},
                "limit": {"type": "integer", "default": 30},
            },
            "required": ["owner", "repo"],
        }, self._list_prs)

        self._register("github_create_branch", "Create a new branch.", {
            "type": "object",
            "properties": {
                "owner": {"type": "string"}, "repo": {"type": "string"},
                "branch_name": {"type": "string"},
                "from_sha": {"type": "string", "description": "SHA to branch from"},
            },
            "required": ["owner", "repo", "branch_name", "from_sha"],
        }, self._create_branch)

        self._register("github_list_branches", "List branches in a repo.", {
            "type": "object",
            "properties": {
                "owner": {"type": "string"}, "repo": {"type": "string"},
                "limit": {"type": "integer", "default": 30},
            },
            "required": ["owner", "repo"],
        }, self._list_branches)

        self._register("github_list_repos", "List authenticated user's repos.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 30}},
        }, self._list_repos)

        self._register("github_get_repo", "Get repo details.", {
            "type": "object",
            "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}},
            "required": ["owner", "repo"],
        }, self._get_repo)

        self._register("github_lock_issue", "Lock a GitHub issue.", {
            "type": "object",
            "properties": {
                "owner": {"type": "string"}, "repo": {"type": "string"},
                "issue_number": {"type": "integer"},
                "reason": {"type": "string", "default": "resolved"},
            },
            "required": ["owner", "repo", "issue_number"],
        }, self._lock_issue)

        self._register("github_get_user", "Get a GitHub user profile.", {
            "type": "object",
            "properties": {"username": {"type": "string"}},
        }, self._get_user)

    async def _create_issue(self, owner: str, repo: str, title: str, body: str = "",
                            labels: list = None, assignees: list = None) -> dict:
        return await self.svc.create_issue(owner, repo, title, body, labels, assignees)

    async def _get_issue(self, owner: str, repo: str, issue_number: int) -> dict:
        return await self.svc.get_issue(owner, repo, issue_number)

    async def _update_issue(self, owner: str, repo: str, issue_number: int, **kwargs) -> dict:
        return await self.svc.update_issue(owner, repo, issue_number, **{k: v for k, v in kwargs.items() if k not in ("owner", "repo", "issue_number") and v is not None})

    async def _list_issues(self, owner: str, repo: str, state: str = "open", limit: int = 30) -> dict:
        issues = await self.svc.list_issues(owner, repo, state, limit)
        return {"issues": issues, "count": len(issues)}

    async def _search_issues(self, query: str, limit: int = 30) -> dict:
        issues = await self.svc.search_issues(query, limit)
        return {"issues": issues, "count": len(issues)}

    async def _add_labels(self, owner: str, repo: str, issue_number: int, labels: list) -> dict:
        return await self.svc.add_labels(owner, repo, issue_number, labels)

    async def _create_comment(self, owner: str, repo: str, issue_number: int, body: str) -> dict:
        return await self.svc.create_comment(owner, repo, issue_number, body)

    async def _create_pr(self, owner: str, repo: str, title: str, head: str, base: str,
                         body: str = "", draft: bool = False) -> dict:
        return await self.svc.create_pull_request(owner, repo, title, head, base, body, draft)

    async def _list_prs(self, owner: str, repo: str, state: str = "open", limit: int = 30) -> dict:
        prs = await self.svc.list_pull_requests(owner, repo, state, limit)
        return {"pull_requests": prs, "count": len(prs)}

    async def _create_branch(self, owner: str, repo: str, branch_name: str, from_sha: str) -> dict:
        return await self.svc.create_branch(owner, repo, branch_name, from_sha)

    async def _list_branches(self, owner: str, repo: str, limit: int = 30) -> dict:
        branches = await self.svc.list_branches(owner, repo, limit)
        return {"branches": branches, "count": len(branches)}

    async def _list_repos(self, limit: int = 30) -> dict:
        repos = await self.svc.list_repos(limit)
        return {"repos": repos, "count": len(repos)}

    async def _get_repo(self, owner: str, repo: str) -> dict:
        return await self.svc.get_repo(owner, repo)

    async def _lock_issue(self, owner: str, repo: str, issue_number: int, reason: str = "resolved") -> dict:
        await self.svc.lock_issue(owner, repo, issue_number, reason)
        return {"locked": True}

    async def _get_user(self, username: str = None) -> dict:
        return await self.svc.get_user(username)

    async def close(self):
        await self.svc.close()
