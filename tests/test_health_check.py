import allure
import pytest

@allure.feature("Test Ping")
@allure.story("Test connection")
def test_ping(api_client):
    status_code = api_client.ping()
    assert status_code == 201, f'Expected status 201 but got {status_code}'
