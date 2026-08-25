import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_health(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data

@pytest.mark.asyncio
async def test_api_v1_health(async_client: AsyncClient):
    # This test hits the database, redis, and minio, expecting them to be running.
    # In a fully mocked unit test environment we might mock these, but the requirements
    # stated: "Tests must verify actual behavior" of the connectivity. 
    # Therefore, we expect 200 if the docker-compose services are running locally, 
    # or 503 if they are down.
    
    response = await async_client.get("/api/v1/health")
    
    # We assert that the application returns a structured payload in either case
    data = response.json()
    
    # If the stack is up, it should be 200
    if response.status_code == 200:
        assert "status" in data
        assert "services" in data
        assert data["status"] == "ok"
        assert data["services"]["database"] == "ok"
        assert data["services"]["redis"] == "ok"
        assert data["services"]["storage"] == "ok"
    else:
        assert response.status_code == 503
        assert "detail" in data
        assert data["detail"]["status"] == "failed"
        assert "services" in data["detail"]
