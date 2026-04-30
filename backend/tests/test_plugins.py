"""
插件模块测试。

覆盖：创建插件、获取插件列表、获取插件详情、更新插件、删除插件等场景。
"""
import uuid

import pytest
from httpx import AsyncClient


@pytest.fixture
async def developer_client(client: AsyncClient) -> AsyncClient:
    """创建开发者身份客户端。"""
    register_data = {
        "email": "dev@example.com",
        "password": "DevPass123456",
        "nickname": "DevUser",
    }
    resp = await client.post("/api/v1/auth/register", json=register_data)
    assert resp.status_code == 201
    tokens = resp.json()["data"]

    client.headers["Authorization"] = f"Bearer {tokens['access_token']}"

    resp_role = await client.put("/api/v1/users/me/role")
    assert resp_role.status_code in (200, 204)

    return client


class TestCreatePlugin:
    """创建插件测试。"""

    async def test_create_plugin_success(self, developer_client: AsyncClient):
        """开发者应能成功创建插件。"""
        data = {
            "name": "Test Plugin",
            "summary": "A test plugin for pytest",
            "description": "# Test Plugin\n\nThis is a test.",
            "price": "9.90",
        }
        resp = await developer_client.post("/api/v1/plugins", json=data)
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["name"] == "Test Plugin"

    async def test_create_plugin_unauthenticated(self, client: AsyncClient):
        """未认证用户创建插件应返回 401。"""
        data = {
            "name": "Unauthorized Plugin",
            "summary": "Should fail",
        }
        resp = await client.post("/api/v1/plugins", json=data)
        assert resp.status_code == 401

    async def test_create_plugin_empty_name(self, developer_client: AsyncClient):
        """空名称应返回 422。"""
        data = {
            "name": "",
            "summary": "No name",
        }
        resp = await developer_client.post("/api/v1/plugins", json=data)
        assert resp.status_code == 422


class TestListPlugins:
    """插件列表测试。"""

    async def test_list_plugins_empty(self, client: AsyncClient):
        """空库应返回空列表。"""
        resp = await client.get("/api/v1/plugins")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["items"] == []

    async def test_list_plugins_with_data(self, developer_client: AsyncClient):
        """有数据时应返回插件列表。"""
        await developer_client.post("/api/v1/plugins", json={
            "name": "Listable Plugin",
            "summary": "Should appear in list",
        })
        resp = await developer_client.get("/api/v1/plugins")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert len(body["data"]["items"]) >= 1


class TestGetPlugin:
    """插件详情测试。"""

    @pytest.fixture
    async def created_plugin(self, developer_client: AsyncClient) -> dict:
        """创建一个插件供详情测试使用。"""
        resp = await developer_client.post("/api/v1/plugins", json={
            "name": "Detail Plugin",
            "summary": "For detail test",
            "description": "Detailed description",
        })
        return resp.json()["data"]

    async def test_get_plugin_success(self, client: AsyncClient, created_plugin):
        """获取存在的插件详情应返回 200。"""
        plugin_id = created_plugin["id"]
        resp = await client.get(f"/api/v1/plugins/{plugin_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["name"] == "Detail Plugin"

    async def test_get_plugin_not_found(self, client: AsyncClient):
        """获取不存在的插件应返回 404。"""
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/api/v1/plugins/{fake_id}")
        assert resp.status_code == 404


class TestUpdatePlugin:
    """更新插件测试。"""

    @pytest.fixture
    async def updatable_plugin(self, developer_client: AsyncClient) -> dict:
        """创建一个插件供更新测试使用。"""
        resp = await developer_client.post("/api/v1/plugins", json={
            "name": "Original Name",
            "summary": "Original summary",
        })
        return resp.json()["data"]

    async def test_update_plugin_success(self, developer_client: AsyncClient, updatable_plugin):
        """插件创建者应能更新插件。"""
        plugin_id = updatable_plugin["id"]
        resp = await developer_client.put(f"/api/v1/plugins/{plugin_id}", json={
            "name": "Updated Name",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["name"] == "Updated Name"


class TestDeletePlugin:
    """删除插件测试。"""

    @pytest.fixture
    async def deletable_plugin(self, developer_client: AsyncClient) -> dict:
        """创建一个插件供删除测试使用。"""
        resp = await developer_client.post("/api/v1/plugins", json={
            "name": "To Be Deleted",
            "summary": "Will be deleted",
        })
        return resp.json()["data"]

    async def test_delete_plugin_success(self, developer_client: AsyncClient, deletable_plugin):
        """插件创建者应能删除插件。"""
        plugin_id = deletable_plugin["id"]
        resp = await developer_client.delete(f"/api/v1/plugins/{plugin_id}")
        assert resp.status_code == 200

    async def test_delete_plugin_not_found(self, developer_client: AsyncClient):
        """删除不存在的插件应返回 404。"""
        fake_id = str(uuid.uuid4())
        resp = await developer_client.delete(f"/api/v1/plugins/{fake_id}")
        assert resp.status_code == 404
