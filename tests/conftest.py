import os
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session


os.environ.setdefault(
	"DATABASE_URL",
	"postgresql+psycopg://test:test@localhost:5432/test",
)


@pytest.fixture
def db_session() -> Mock:
	# Each test receives a fresh session-shaped mock, so calls and failures do
	# not leak from one test into another.
	return Mock(spec=Session)
