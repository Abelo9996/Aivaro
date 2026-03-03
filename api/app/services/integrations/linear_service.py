"""
Linear Integration Service — issues, projects, teams.
"""
import httpx
from typing import Optional, Any


class LinearService:
    """Service for Linear GraphQL API."""

    BASE_URL = "https://api.linear.app/graphql"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _gql(self, query: str, variables: dict = None) -> dict:
        client = await self._get_client()
        body = {"query": query}
        if variables: body["variables"] = variables
        resp = await client.post(self.BASE_URL, json=body,
                                 headers={"Authorization": self.api_key, "Content-Type": "application/json"})
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise Exception(data["errors"][0].get("message", str(data["errors"])))
        return data.get("data", {})

    async def create_issue(self, team_id: str, title: str, description: str = "",
                           priority: int = 0, assignee_id: str = None, state_id: str = None,
                           label_ids: list = None) -> dict:
        mutation = """mutation($input: IssueCreateInput!) { issueCreate(input: $input) { success issue { id identifier title url } } }"""
        inp = {"teamId": team_id, "title": title}
        if description: inp["description"] = description
        if priority: inp["priority"] = priority
        if assignee_id: inp["assigneeId"] = assignee_id
        if state_id: inp["stateId"] = state_id
        if label_ids: inp["labelIds"] = label_ids
        result = await self._gql(mutation, {"input": inp})
        return result.get("issueCreate", {}).get("issue", {})

    async def update_issue(self, issue_id: str, **kwargs) -> dict:
        mutation = """mutation($id: String!, $input: IssueUpdateInput!) { issueUpdate(id: $id, input: $input) { success issue { id identifier title url state { name } } } }"""
        result = await self._gql(mutation, {"id": issue_id, "input": kwargs})
        return result.get("issueUpdate", {}).get("issue", {})

    async def get_issue(self, issue_id: str) -> dict:
        query = """query($id: String!) { issue(id: $id) { id identifier title description url priority state { id name } assignee { id name } labels { nodes { id name } } createdAt updatedAt } }"""
        result = await self._gql(query, {"id": issue_id})
        return result.get("issue", {})

    async def search_issues(self, query: str, limit: int = 20) -> list:
        gql = """query($filter: IssueFilter, $first: Int) { issues(filter: $filter, first: $first) { nodes { id identifier title url state { name } assignee { name } priority } } }"""
        result = await self._gql(gql, {
            "filter": {"or": [{"title": {"containsIgnoreCase": query}}, {"description": {"containsIgnoreCase": query}}]},
            "first": limit,
        })
        return result.get("issues", {}).get("nodes", [])

    async def list_issues(self, team_id: str = None, limit: int = 50) -> list:
        gql = """query($first: Int) { issues(first: $first, orderBy: updatedAt) { nodes { id identifier title url state { name } assignee { name } priority } } }"""
        result = await self._gql(gql, {"first": limit})
        return result.get("issues", {}).get("nodes", [])

    async def create_comment(self, issue_id: str, body: str) -> dict:
        mutation = """mutation($input: CommentCreateInput!) { commentCreate(input: $input) { success comment { id body } } }"""
        result = await self._gql(mutation, {"input": {"issueId": issue_id, "body": body}})
        return result.get("commentCreate", {}).get("comment", {})

    async def list_teams(self) -> list:
        query = """query { teams { nodes { id name key } } }"""
        result = await self._gql(query)
        return result.get("teams", {}).get("nodes", [])

    async def list_projects(self, limit: int = 50) -> list:
        query = """query($first: Int) { projects(first: $first) { nodes { id name state url } } }"""
        result = await self._gql(query, {"first": limit})
        return result.get("projects", {}).get("nodes", [])

    async def list_states(self, team_id: str) -> list:
        query = """query($teamId: String!) { workflowStates(filter: { team: { id: { eq: $teamId } } }) { nodes { id name type position } } }"""
        result = await self._gql(query, {"teamId": team_id})
        return result.get("workflowStates", {}).get("nodes", [])

    async def list_labels(self, team_id: str = None) -> list:
        query = """query { issueLabels { nodes { id name color } } }"""
        result = await self._gql(query)
        return result.get("issueLabels", {}).get("nodes", [])
