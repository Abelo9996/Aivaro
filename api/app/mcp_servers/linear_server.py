"""Linear MCP Server — issues, projects, teams, comments."""
from app.mcp_servers.base import BaseMCPServer


class LinearMCPServer(BaseMCPServer):
    provider = "linear"

    def __init__(self, api_key: str):
        super().__init__()
        from app.services.integrations.linear_service import LinearService
        self.svc = LinearService(api_key=api_key)
        self._register_tools()

    def _register_tools(self):
        self._register("linear_create_issue", "Create a Linear issue.", {
            "type": "object",
            "properties": {
                "team_id": {"type": "string"}, "title": {"type": "string"},
                "description": {"type": "string"}, "priority": {"type": "integer", "description": "0=none,1=urgent,2=high,3=medium,4=low"},
                "assignee_id": {"type": "string"}, "state_id": {"type": "string"},
                "label_ids": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["team_id", "title"],
        }, self._create_issue)

        self._register("linear_update_issue", "Update a Linear issue.", {
            "type": "object",
            "properties": {
                "issue_id": {"type": "string"},
                "title": {"type": "string"}, "description": {"type": "string"},
                "priority": {"type": "integer"}, "state_id": {"type": "string"},
                "assignee_id": {"type": "string"},
            },
            "required": ["issue_id"],
        }, self._update_issue)

        self._register("linear_get_issue", "Get a Linear issue by ID.", {
            "type": "object",
            "properties": {"issue_id": {"type": "string"}},
            "required": ["issue_id"],
        }, self._get_issue)

        self._register("linear_search_issues", "Search Linear issues.", {
            "type": "object",
            "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 20}},
            "required": ["query"],
        }, self._search_issues)

        self._register("linear_list_issues", "List recent Linear issues.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 50}},
        }, self._list_issues)

        self._register("linear_create_comment", "Add a comment to a Linear issue.", {
            "type": "object",
            "properties": {"issue_id": {"type": "string"}, "body": {"type": "string"}},
            "required": ["issue_id", "body"],
        }, self._create_comment)

        self._register("linear_list_teams", "List Linear teams.", {
            "type": "object", "properties": {},
        }, self._list_teams)

        self._register("linear_list_projects", "List Linear projects.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 50}},
        }, self._list_projects)

        self._register("linear_list_states", "List workflow states for a team.", {
            "type": "object",
            "properties": {"team_id": {"type": "string"}},
            "required": ["team_id"],
        }, self._list_states)

        self._register("linear_list_labels", "List issue labels.", {
            "type": "object", "properties": {},
        }, self._list_labels)

    async def _create_issue(self, team_id: str, title: str, description: str = "",
                            priority: int = 0, assignee_id: str = None, state_id: str = None,
                            label_ids: list = None) -> dict:
        return await self.svc.create_issue(team_id, title, description, priority, assignee_id, state_id, label_ids)

    async def _update_issue(self, issue_id: str, **kwargs) -> dict:
        updates = {k: v for k, v in kwargs.items() if k != "issue_id" and v is not None}
        return await self.svc.update_issue(issue_id, **updates)

    async def _get_issue(self, issue_id: str) -> dict:
        return await self.svc.get_issue(issue_id)

    async def _search_issues(self, query: str, limit: int = 20) -> dict:
        issues = await self.svc.search_issues(query, limit)
        return {"issues": issues, "count": len(issues)}

    async def _list_issues(self, limit: int = 50) -> dict:
        issues = await self.svc.list_issues(limit=limit)
        return {"issues": issues, "count": len(issues)}

    async def _create_comment(self, issue_id: str, body: str) -> dict:
        return await self.svc.create_comment(issue_id, body)

    async def _list_teams(self) -> dict:
        teams = await self.svc.list_teams()
        return {"teams": teams, "count": len(teams)}

    async def _list_projects(self, limit: int = 50) -> dict:
        projects = await self.svc.list_projects(limit)
        return {"projects": projects, "count": len(projects)}

    async def _list_states(self, team_id: str) -> dict:
        states = await self.svc.list_states(team_id)
        return {"states": states, "count": len(states)}

    async def _list_labels(self) -> dict:
        labels = await self.svc.list_labels()
        return {"labels": labels, "count": len(labels)}

    async def close(self):
        await self.svc.close()
