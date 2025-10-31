# conftest.py
import pytest

@pytest.fixture(autouse=True)
def _sqlite_test_db(settings, tmp_path):
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': tmp_path / "test.sqlite3",
        'ATOMIC_REQUESTS': False,
    }
