import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from backend.main import app
from backend.models import UserInDB
from datetime import datetime, timedelta
import asyncio

client = TestClient(app)

# Mock Auth
def mock_get_current_admin():
    return UserInDB(email="admin@example.com", hashed_password="hash", role="admin")

def mock_get_current_user():
    return UserInDB(email="user@example.com", hashed_password="hash", role="user")

@pytest.fixture
def mock_db():
    mock = MagicMock()
    # Mock collections
    mock.__getitem__.return_value = mock
    # Mock find_one
    mock.find_one.return_value = None # Default return
    return mock

@pytest.fixture(autouse=True)
def override_db(mock_db):
    app.dependency_overrides = {} # Clear previous
    from backend.database import get_database
    app.dependency_overrides[get_database] = lambda: mock_db
    yield
    app.dependency_overrides = {}

@pytest.fixture
def admin_auth():
    from backend.routers.auth import get_current_admin, get_current_user
    app.dependency_overrides[get_current_admin] = mock_get_current_admin
    app.dependency_overrides[get_current_user] = mock_get_current_admin
    yield
    app.dependency_overrides = {}

@pytest.fixture
def user_auth():
    from backend.routers.auth import get_current_admin, get_current_user
    def mock_user():
        return UserInDB(email="user@example.com", hashed_password="hash", role="user")
    app.dependency_overrides[get_current_user] = mock_user
    yield
    app.dependency_overrides = {}

def test_system_status_offline_initially(mock_db):
    # Mock find_one to be awaitable
    mock_db["system_state"].find_one = AsyncMock(return_value=None)
    
    response = client.get("/api/admin/system-status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OFFLINE"

@patch("backend.routers.admin.KiteConnect")
@patch("backend.routers.admin.ticker_service", new_callable=AsyncMock)
def test_admin_submit_token_success(mock_ticker, mock_kite, admin_auth, mock_db):
    # Mock DB async calls
    mock_db["system_state"].update_many = AsyncMock(return_value=None)
    mock_db["system_state"].insert_one = AsyncMock(return_value=None)

    # Mock Kite
    mock_k = MagicMock()
    mock_k.generate_session.return_value = {
        "access_token": "access_token_123",
        "public_token": "public_token_123"
    }
    mock_kite.return_value = mock_k

    payload = {
        "request_token_url": "https://kite.trade/?request_token=valid_token_123&action=login"
    }
    
    response = client.post("/api/admin/submit-request-token", json=payload)
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Verify Service calls
    mock_k.generate_session.assert_called_once()
    mock_ticker.restart.assert_called_once_with("access_token_123")

def test_admin_submit_invalid_url(admin_auth):
    payload = {
        "request_token_url": "invalid_url"
    }
    response = client.post("/api/admin/submit-request-token", json=payload)
    assert response.status_code == 400

def test_user_cannot_submit_token(user_auth):
    payload = {
        "request_token_url": "https://kite.trade/?request_token=valid_token_123"
    }
    response = client.post("/api/admin/submit-request-token", json=payload)
    # Should be 403 Forbidden
    assert response.status_code == 403
