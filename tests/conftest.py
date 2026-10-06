import os
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session


# The application creates its database engine while modules are imported.
# Unit tests never connect to this URL, but they need a valid-looking value so
# importing the application does not fail before the tests start.
os.environ.setdefault(
	"DATABASE_URL",
	"postgresql+psycopg://test:test@localhost:5432/test",
)


@pytest.fixture
def db_session() -> Mock:
	# pytest runs this function for every test that names db_session as an
	# argument, giving each test an isolated mock with no previous call history.
	# Each test receives a fresh session-shaped mock, so calls and failures do
	# not leak from one test into another.
	return Mock(spec=Session)
