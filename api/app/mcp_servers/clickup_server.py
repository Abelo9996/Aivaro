"""ClickUp MCP Server — tasks, lists, spaces."""
from app.mcp_servers.base import BaseMCPServer


class ClickUpMCPServer(BaseMCPServer):
    provider = "clickup"

    def __init__(self, api_key: str):
        super().__init__()
        from app.services.integrations.clickup_service import ClickUpService
        self.svc = ClickUpService(api_key=api_key)
        self._register_tools()

    def _register_tools(self):
        self._register("clickup_list_workspaces", "List all ClickUp workspaces (teams).", {
            "type": "object", "properties": {},
        }, self._list_workspaces)

        self._register("clickup_list_spaces", "List spaces in a ClickUp workspace.", {
            "type": "object",
            "properties": {"team_id": {"type": "string", "description": "Workspace/team ID"}},
            "required": ["team_id"],
        }, self._list_spaces)

        self._register("clickup_list_folders", "List folders in a ClickUp space.", {
            "type": "object",
            "properties": {"space_id": {"type": "string", "description": "Space ID"}},
            "required": ["space_id"],
        }, self._list_folders)

        self._register("clickup_list_lists", "List lists in a ClickUp folder.", {
            "type": "object",
            "properties": {"folder_id": {"type": "string", "description": "Folder ID"}},
            "required": ["folder_id"],
        }, self._list_lists)

        self._register("clickup_list_tasks", "List tasks in a ClickUp list.", {
            "type": "object",
            "properties": {"list_id": {"type": "string", "description": "List ID"}},
            "required": ["list_id"],
        }, self._list_tasks)

        self._register("clickup_get_task", "Get details of a ClickUp task.", {
            "type": "object",
            "properties": {"task_id": {"type": "string", "description": "Task ID"}},
            "required": ["task_id"],
        }, self._get_task)

        self._register("clickup_create_task", "Create a task in a ClickUp list.", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string", "description": "List ID"},
                "name": {"type": "string", "description": "Task name"},
                "description": {"type": "string", "description": "Task description (markdown)"},
                "assignees": {"type": "array", "items": {"type": "integer"}, "description": "Assignee user IDs"},
                "due_date": {"type": "integer", "description": "Due date as Unix timestamp (ms)"},
                "priority": {"type": "integer", "description": "Priority: 1=Urgent, 2=High, 3=Normal, 4=Low"},
            },
            "required": ["list_id", "name"],
        }, self._create_task)

        self._register("clickup_update_task", "Update a ClickUp task.", {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
                "name": {"type": "string", "description": "New name"},
                "description": {"type": "string", "description": "New description"},
                "status": {"type": "string", "description": "New status name"},
                "priority": {"type": "integer", "description": "Priority: 1=Urgent, 2=High, 3=Normal, 4=Low"},
            },
            "required": ["task_id"],
        }, self._update_task)

        self._register("clickup_delete_task", "Delete a ClickUp task.", {
            "type": "object",
            "properties": {"task_id": {"type": "string", "description": "Task ID"}},
            "required": ["task_id"],
        }, self._delete_task)

        self._register("clickup_add_comment", "Add a comment to a ClickUp task.", {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
                "comment_text": {"type": "string", "description": "Comment text"},
            },
            "required": ["task_id", "comment_text"],
        }, self._add_comment)

    async def _list_workspaces(self) -> dict:
        ws = await self.svc.list_workspaces()
        return {"workspaces": ws, "count": len(ws)}

    async def _list_spaces(self, team_id: str) -> dict:
        spaces = await self.svc.list_spaces(team_id)
        return {"spaces": spaces, "count": len(spaces)}

    async def _list_folders(self, space_id: str) -> dict:
        folders = await self.svc.list_folders(space_id)
        return {"folders": folders, "count": len(folders)}

    async def _list_lists(self, folder_id: str) -> dict:
        lists = await self.svc.list_lists(folder_id)
        return {"lists": lists, "count": len(lists)}

    async def _list_tasks(self, list_id: str) -> dict:
        tasks = await self.svc.list_tasks(list_id)
        return {"tasks": tasks, "count": len(tasks)}

    async def _get_task(self, task_id: str) -> dict:
        return await self.svc.get_task(task_id)

    async def _create_task(self, list_id: str, name: str, description: str = "",
                           assignees: list = None, due_date: int = None, priority: int = None) -> dict:
        return await self.svc.create_task(list_id, name, description, assignees, due_date, priority)

    async def _update_task(self, task_id: str, **fields) -> dict:
        return await self.svc.update_task(task_id, **fields)

    async def _delete_task(self, task_id: str) -> dict:
        await self.svc.delete_task(task_id)
        return {"deleted": True, "task_id": task_id}

    async def _add_comment(self, task_id: str, comment_text: str) -> dict:
        return await self.svc.add_comment(task_id, comment_text)

    async def close(self):
        await self.svc.close()
