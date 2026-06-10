from pathlib import Path

from app.core.config import Settings


def test_env_example_lists_every_settings_field():
    env_example = Path("backend/.env.example").read_text(encoding="utf-8")
    keys = {
        line.split("=", 1)[0]
        for line in env_example.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }

    expected_keys = {field_name.upper() for field_name in Settings.model_fields}

    assert expected_keys.issubset(keys)


def test_env_example_can_be_loaded_by_settings(tmp_path):
    source = Path("backend/.env.example").read_text(encoding="utf-8")
    env_file = tmp_path / ".env"
    env_file.write_text(source, encoding="utf-8")

    settings = Settings(_env_file=env_file)

    assert settings.allowed_origins
    assert "http://127.0.0.1:5173" in settings.allowed_origins
