import pytest
from pydantic import ValidationError

from app.core.config import PROJECT_ROOT, Settings


def test_default_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = Settings(_env_file=None)

    expected_url = f"sqlite:///{(PROJECT_ROOT / 'documents.db').as_posix()}"

    assert settings.database_url == expected_url
    assert PROJECT_ROOT.is_absolute()


def test_database_url_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")

    settings = Settings(_env_file=None)

    assert settings.database_url == "sqlite:///test.db"


def test_invalid_database_url_type(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError):
        Settings(database_url=None, _env_file=None)


def test_database_url_from_env_file(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=sqlite:///from-env-file.db\n", encoding="utf-8")

    settings = Settings(_env_file=env_file)

    assert settings.database_url == "sqlite:///from-env-file.db"


def test_environment_variable_takes_precedence_over_env_file(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///from-environment.db")

    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=sqlite:///from-env-file.db\n", encoding="utf-8")

    settings = Settings(_env_file=env_file)

    assert settings.database_url == "sqlite:///from-environment.db"


# A .env in the current working directory must not be loaded; only the
# project's .env is, regardless of where the process starts.
def test_env_file_is_not_read_from_working_directory(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".env").write_text(
        "DATABASE_URL=sqlite:///from-working-directory.db\n",
        encoding="utf-8",
    )

    settings = Settings()

    assert settings.database_url != "sqlite:///from-working-directory.db"


def test_empty_database_url_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
