"""Asana MCP Server — tasks, projects, workspaces."""
from app.mcp_servers.base import BaseMCPServer


class AsanaMCPServer(BaseMCPServer):
    provider = "asana"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.asana_service import AsanaService
        self.svc = AsanaService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("asana_list_workspaces", "List all Asana workspaces.", {
            "type": "object", "properties": {},
        }, self._list_workspaces)

        self._register("asana_list_projects", "List projects in an Asana workspace.", {
            "type": "object",
            "properties": {
                "workspace_gid": {"type": "string", "description": "Workspace GID"},
            },
            "required": ["workspace_gid"],
        }, self._list_projects)

        self._register("asana_create_project", "Create a new Asana project.", {
            "type": "object",
            "properties": {
                "workspace_gid": {"type": "string", "description": "Workspace GID"},
                "name": {"type": "string", "description": "Project name"},
                "notes": {"type": "string", "description": "Project description"},
            },
            "required": ["workspace_gid", "name"],
        }, self._create_project)

        self._register("asana_list_tasks", "List tasks in an Asana project.", {
            "type": "object",
            "properties": {
                "project_gid": {"type": "string", "description": "Project GID"},
            },
            "required": ["project_gid"],
        }, self._list_tasks)

        self._register("asana_get_task", "Get details of an Asana task.", {
            "type": "object",
            "properties": {
                "task_gid": {"type": "string", "description": "Task GID"},
            },
            "required": ["task_gid"],
        }, self._get_task)

        self._register("asana_create_task", "Create a task in an Asana project.", {
            "type": "object",
            "properties": {
                "project_gid": {"type": "string", "description": "Project GID"},
                "name": {"type": "string", "description": "Task name"},
                "notes": {"type": "string", "description": "Task description"},
                "assignee": {"type": "string", "description": "Assignee email or GID"},
                "due_on": {"type": "string", "description": "Due date (YYYY-MM-DD)"},
            },
            "required": ["project_gid", "name"],
        }, self._create_task)

        self._register("asana_update_task", "Update an Asana task.", {
            "type": "object",
            "properties": {
                "task_gid": {"type": "string", "description": "Task GID"},
                "name": {"type": "string", "description": "New task name"},
                "notes": {"type": "string", "description": "New description"},
                "completed": {"type": "boolean", "description": "Mark complete/incomplete"},
                "due_on": {"type": "string", "description": "New due date (YYYY-MM-DD)"},
            },
            "required": ["task_gid"],
        }, self._update_task)

        self._register("asana_add_comment", "Add a comment to an Asana task.", {
            "type": "object",
            "properties": {
                "task_gid": {"type": "string", "description": "Task GID"},
                "text": {"type": "string", "description": "Comment text"},
            },
            "required": ["task_gid", "text"],
        }, self._add_comment)

    async def _list_workspaces(self) -> dict:
        ws = await self.svc.list_workspaces()
        return {"workspaces": ws, "count": len(ws)}

    async def _list_projects(self, workspace_gid: str) -> dict:
        projects = await self.svc.list_projects(workspace_gid)
        return {"projects": projects, "count": len(projects)}

    async def _create_project(self, workspace_gid: str, name: str, notes: str = "") -> dict:
        return await self.svc.create_project(workspace_gid, name, notes)

    async def _list_tasks(self, project_gid: str) -> dict:
        tasks = await self.svc.list_tasks(project_gid)
        return {"tasks": tasks, "count": len(tasks)}

    async def _get_task(self, task_gid: str) -> dict:
        return await self.svc.get_task(task_gid)

    async def _create_task(self, project_gid: str, name: str, notes: str = "",
                           assignee: str = None, due_on: str = None) -> dict:
        return await self.svc.create_task(project_gid, name, notes, assignee, due_on)

    async def _update_task(self, task_gid: str, **fields) -> dict:
        return await self.svc.update_task(task_gid, **fields)

    async def _add_comment(self, task_gid: str, text: str) -> dict:
        return await self.svc.add_comment(task_gid, text)

    async def close(self):
        await self.svc.close()
