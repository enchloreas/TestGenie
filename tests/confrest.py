import pytest

def pytest_addoption(parser):
    """
    Add the custom '--test' argument to pytest.
    """
    parser.addoption(
        "--test", action="store_true", default=False, help="Run tests using the test database"
    )

@pytest.fixture(scope="session")
def test_mode(request):
    """
    Provide the value of the '--test' argument as a fixture.
    """
    return request.config.getoption("--test")