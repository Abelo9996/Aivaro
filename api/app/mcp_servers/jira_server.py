"""Jira Cloud MCP Server — issues, projects, comments, search."""
from app.mcp_servers.base import BaseMCPServer


class JiraMCPServer(BaseMCPServer):
    provider = "jira"

    def __init__(self, domain: str, email: str, api_token: str):
        super().__init__()
        from app.services.integrations.jira_service import JiraService
        self.svc = JiraService(domain=domain, email=email, api_token=api_token)
        self._register_tools()

    def _register_tools(self):
        self._register("jira_create_issue", "Create a Jira issue.", {
            "type": "object",
            "properties": {
                "project_key": {"type": "string", "description": "Project key (e.g. PROJ)"},
                "summary": {"type": "string"},
                "issue_type": {"type": "string", "default": "Task", "description": "Task, Bug, Story, Epic"},
                "description": {"type": "string"},
                "priority": {"type": "string", "description": "Highest, High, Medium, Low, Lowest"},
                "assignee_id": {"type": "string"},
                "labels": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["project_key", "summary"],
        }, self._create_issue)

        self._register("jira_get_issue", "Get a Jira issue by key.", {
            "type": "object",
            "properties": {"issue_key": {"type": "string", "description": "e.g. PROJ-123"}},
            "required": ["issue_key"],
        }, self._get_issue)

        self._register("jira_update_issue", "Update a Jira issue.", {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string"},
                "fields": {"type": "object", "description": "Fields to update"},
            },
            "required": ["issue_key", "fields"],
        }, self._update_issue)

        self._register("jira_search_issues", "Search Jira issues with JQL.", {
            "type": "object",
            "properties": {
                "jql": {"type": "string", "description": "JQL query (e.g. 'project = PROJ AND status = Open')"},
                "max_results": {"type": "integer", "default": 50},
            },
            "required": ["jql"],
        }, self._search_issues)

        self._register("jira_add_comment", "Add a comment to a Jira issue.", {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["issue_key", "body"],
        }, self._add_comment)

        self._register("jira_list_comments", "List comments on a Jira issue.", {
            "type": "object",
            "properties": {"issue_key": {"type": "string"}},
            "required": ["issue_key"],
        }, self._list_comments)

        self._register("jira_assign_issue", "Assign a Jira issue to a user.", {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string"},
                "account_id": {"type": "string"},
            },
            "required": ["issue_key", "account_id"],
        }, self._assign_issue)

        self._register("jira_transition_issue", "Transition a Jira issue to a new status.", {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string"},
                "transition_id": {"type": "string"},
            },
            "required": ["issue_key", "transition_id"],
        }, self._transition_issue)

        self._register("jira_get_transitions", "Get available transitions for a Jira issue.", {
            "type": "object",
            "properties": {"issue_key": {"type": "string"}},
            "required": ["issue_key"],
        }, self._get_transitions)

        self._register("jira_list_projects", "List all Jira projects.", {
            "type": "object", "properties": {},
        }, self._list_projects)

        self._register("jira_search_users", "Search Jira users.", {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        }, self._search_users)

        self._register("jira_link_issues", "Link two Jira issues together.", {
            "type": "object",
            "properties": {
                "inward_key": {"type": "string"},
                "outward_key": {"type": "string"},
                "link_type": {"type": "string", "default": "Relates"},
            },
            "required": ["inward_key", "outward_key"],
        }, self._link_issues)

    async def _create_issue(self, project_key: str, summary: str, issue_type: str = "Task",
                            description: str = "", priority: str = None, assignee_id: str = None,
                            labels: list = None) -> dict:
        return await self.svc.create_issue(project_key, summary, issue_type, description, priority, assignee_id, labels)

    async def _get_issue(self, issue_key: str) -> dict:
        return await self.svc.get_issue(issue_key)

    async def _update_issue(self, issue_key: str, fields: dict) -> dict:
        return await self.svc.update_issue(issue_key, fields)

    async def _search_issues(self, jql: str, max_results: int = 50) -> dict:
        issues = await self.svc.search_issues(jql, max_results)
        return {"issues": issues, "count": len(issues)}

    async def _add_comment(self, issue_key: str, body: str) -> dict:
        return await self.svc.add_comment(issue_key, body)

    async def _list_comments(self, issue_key: str) -> dict:
        comments = await self.svc.list_comments(issue_key)
        return {"comments": comments, "count": len(comments)}

    async def _assign_issue(self, issue_key: str, account_id: str) -> dict:
        await self.svc.assign_issue(issue_key, account_id)
        return {"assigned": True}

    async def _transition_issue(self, issue_key: str, transition_id: str) -> dict:
        await self.svc.transition_issue(issue_key, transition_id)
        return {"transitioned": True}

    async def _get_transitions(self, issue_key: str) -> dict:
        transitions = await self.svc.get_transitions(issue_key)
        return {"transitions": transitions}

    async def _list_projects(self) -> dict:
        projects = await self.svc.list_projects()
        return {"projects": projects, "count": len(projects)}

    async def _search_users(self, query: str) -> dict:
        users = await self.svc.search_users(query)
        return {"users": users, "count": len(users)}

    async def _link_issues(self, inward_key: str, outward_key: str, link_type: str = "Relates") -> dict:
        await self.svc.link_issues(inward_key, outward_key, link_type)
        return {"linked": True}

    async def close(self):
        await self.svc.close()
