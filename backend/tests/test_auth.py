"""
认证模块测试。

覆盖：注册、登录、刷新令牌、密码校验、重复注册、无效登录等场景。
"""
import pytest
from httpx import AsyncClient


class TestRegister:
    """用户注册测试。"""

    async def test_register_success(self, client: AsyncClient):
        """正常注册应返回 201 和双 token。"""
        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "nickname": "NewUser",
        }
        resp = await client.post("/api/v1/auth/register", json=data)
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == 0
        assert "access_token" in body["data"]
        assert "refresh_token" in body["data"]
        assert body["data"]["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client: AsyncClient):
        """重复邮箱注册应返回 409。"""
        data = {
            "email": "duplicate@example.com",
            "password": "SecurePass123",
            "nickname": "User1",
        }
        resp1 = await client.post("/api/v1/auth/register", json=data)
        assert resp1.status_code == 201

        resp2 = await client.post("/api/v1/auth/register", json=data)
        assert resp2.status_code == 409

    async def test_register_weak_password(self, client: AsyncClient):
        """弱密码（无数字）应返回 422。"""
        data = {
            "email": "weak@example.com",
            "password": "onlyletters",
            "nickname": "WeakUser",
        }
        resp = await client.post("/api/v1/auth/register", json=data)
        assert resp.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        """密码少于 8 字符应返回 422。"""
        data = {
            "email": "short@example.com",
            "password": "Ab1",
            "nickname": "ShortUser",
        }
        resp = await client.post("/api/v1/auth/register", json=data)
        assert resp.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        """无效邮箱格式应返回 422。"""
        data = {
            "email": "not-an-email",
            "password": "SecurePass123",
            "nickname": "InvalidEmail",
        }
        resp = await client.post("/api/v1/auth/register", json=data)
        assert resp.status_code == 422


class TestLogin:
    """用户登录测试。"""

    @pytest.fixture
    async def registered_user(self, client: AsyncClient):
        """预注册一个用户供登录测试使用。"""
        data = {
            "email": "loginuser@example.com",
            "password": "LoginPass123",
            "nickname": "LoginUser",
        }
        resp = await client.post("/api/v1/auth/register", json=data)
        assert resp.status_code == 201
        return data

    async def test_login_success(self, client: AsyncClient, registered_user):
        """正确凭据登录应返回 200 和双 token。"""
        resp = await client.post("/api/v1/auth/login", json=registered_user)
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert "access_token" in body["data"]
        assert "refresh_token" in body["data"]

    async def test_login_wrong_password(self, client: AsyncClient, registered_user):
        """错误密码应返回 400。"""
        resp = await client.post("/api/v1/auth/login", json={
            "email": registered_user["email"],
            "password": "WrongPass123",
        })
        assert resp.status_code == 400

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """不存在的用户应返回 400。"""
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "SomePass123",
        })
        assert resp.status_code == 400


class TestRefreshToken:
    """刷新令牌测试。"""

    @pytest.fixture
    async def authenticated_user(self, client: AsyncClient):
        """注册并返回 tokens。"""
        data = {
            "email": "refreshuser@example.com",
            "password": "RefreshPass123",
            "nickname": "RefreshUser",
        }
        resp = await client.post("/api/v1/auth/register", json=data)
        assert resp.status_code == 201
        return resp.json()["data"]

    async def test_refresh_token_success(self, client: AsyncClient, authenticated_user):
        """有效 refresh_token 应返回新的 access_token。"""
        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": authenticated_user["refresh_token"],
        })
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body["data"]

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """无效 refresh_token 应返回 401。"""
        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid-token-string",
        })
        assert resp.status_code == 401


class TestLogout:
    """登出测试。"""

    async def test_logout(self, client: AsyncClient):
        """登出应返回 200。"""
        resp = await client.post("/api/v1/auth/logout")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
