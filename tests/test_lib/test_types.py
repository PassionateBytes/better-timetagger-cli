"""Tests for type definitions."""

from better_timetagger_cli.lib.types import (
    ConfigDict,
    GetRecordsResponse,
    GetSettingsResponse,
    GetUpdatesResponse,
    LegacyConfigDict,
    PutRecordsResponse,
    PutSettingsResponse,
    Record,
    Settings,
)


def test_config_dict_structure():
    """ConfigDict accepts all required fields."""
    config: ConfigDict = {
        "base_url": "https://timetagger.example.com",
        "api_token": "test-token-123",
        "ssl_verify": True,
        "datetime_format": "%Y-%m-%d %H:%M:%S",
        "weekday_format": "%A",
        "running_records_search_window": 7,
    }

    assert config["base_url"] == "https://timetagger.example.com"
    assert config["api_token"] == "test-token-123"
    assert config["ssl_verify"] is True
    assert config["datetime_format"] == "%Y-%m-%d %H:%M:%S"
    assert config["weekday_format"] == "%A"
    assert config["running_records_search_window"] == 7


def test_legacy_config_dict_structure():
    """LegacyConfigDict accepts all required fields."""
    legacy_config: LegacyConfigDict = {
        "api_url": "https://old.timetagger.example.com/api",
        "api_token": "legacy-token-456",
        "ssl_verify": False,
    }

    assert legacy_config["api_url"] == "https://old.timetagger.example.com/api"
    assert legacy_config["api_token"] == "legacy-token-456"
    assert legacy_config["ssl_verify"] is False


def test_legacy_config_dict_ssl_verify_string():
    """LegacyConfigDict accepts ssl_verify as string."""
    legacy_config: LegacyConfigDict = {
        "api_url": "https://old.timetagger.example.com/api",
        "api_token": "legacy-token-456",
        "ssl_verify": "false",
    }

    assert legacy_config["ssl_verify"] == "false"


def test_record_structure():
    """Record accepts all required fields."""
    record: Record = {
        "key": "abc12345",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 1640998800,
        "ds": "#work #project documentation",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 3600,
    }

    assert record["key"] == "abc12345"
    assert record["mt"] == 1640995200
    assert record["t1"] == 1640995200
    assert record["t2"] == 1640998800
    assert record["ds"] == "#work #project documentation"
    assert record["st"] == 1640995200.0
    assert record["_running"] is False
    assert record["_duration"] == 3600


def test_record_running_flag():
    """Record can handle running state."""
    record: Record = {
        "key": "def67890",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 0,  # Running records have t2=0
        "ds": "#development #coding",
        "st": 1640995200.0,
        "_running": True,
        "_duration": 0,
    }

    assert record["_running"] is True
    assert record["t2"] == 0


def test_settings_structure():
    """Settings accepts all required fields."""
    settings: Settings = {
        "key": "setting_key",
        "value": "setting_value",
        "mt": 1640995200,
        "st": 1640995200.0,
    }

    assert settings["key"] == "setting_key"
    assert settings["value"] == "setting_value"
    assert settings["mt"] == 1640995200
    assert settings["st"] == 1640995200.0


def test_get_records_response_structure():
    """GetRecordsResponse accepts list of records."""
    response: GetRecordsResponse = {
        "records": [
            {
                "key": "abc12345",
                "mt": 1640995200,
                "t1": 1640995200,
                "t2": 1640998800,
                "ds": "#work documentation",
                "st": 1640995200.0,
                "_running": False,
                "_duration": 3600,
            }
        ]
    }

    assert len(response["records"]) == 1
    assert response["records"][0]["key"] == "abc12345"


def test_get_records_response_empty():
    """GetRecordsResponse handles empty record list."""
    response: GetRecordsResponse = {"records": []}

    assert response["records"] == []


def test_put_records_response_structure():
    """PutRecordsResponse accepts all required fields."""
    response: PutRecordsResponse = {
        "accepted": ["abc12345", "def67890"],
        "failed": ["ghi11111"],
        "errors": ["Invalid timestamp for record ghi11111"],
    }

    assert response["accepted"] == ["abc12345", "def67890"]
    assert response["failed"] == ["ghi11111"]
    assert response["errors"] == ["Invalid timestamp for record ghi11111"]


def test_put_records_response_empty_failures():
    """PutRecordsResponse handles no failures."""
    response: PutRecordsResponse = {
        "accepted": ["abc12345"],
        "failed": [],
        "errors": [],
    }

    assert len(response["accepted"]) == 1
    assert response["failed"] == []
    assert response["errors"] == []


def test_get_settings_response_structure():
    """GetSettingsResponse accepts list of settings."""
    response: GetSettingsResponse = {
        "settings": [
            {
                "key": "timezone",
                "value": "UTC",
                "mt": 1640995200,
                "st": 1640995200.0,
            }
        ]
    }

    assert len(response["settings"]) == 1
    assert response["settings"][0]["key"] == "timezone"
    assert response["settings"][0]["value"] == "UTC"


def test_put_settings_response_structure():
    """PutSettingsResponse accepts all required fields."""
    response: PutSettingsResponse = {
        "accepted": ["timezone", "theme"],
        "failed": ["invalid_setting"],
        "errors": ["Setting 'invalid_setting' is not recognized"],
    }

    assert response["accepted"] == ["timezone", "theme"]
    assert response["failed"] == ["invalid_setting"]
    assert response["errors"] == ["Setting 'invalid_setting' is not recognized"]


def test_get_updates_response_structure():
    """GetUpdatesResponse accepts all required fields."""
    response: GetUpdatesResponse = {
        "server_time": 1640995200,
        "reset": 0,
        "records": [
            {
                "key": "abc12345",
                "mt": 1640995200,
                "t1": 1640995200,
                "t2": 1640998800,
                "ds": "#work update",
                "st": 1640995200.0,
                "_running": False,
                "_duration": 3600,
            }
        ],
        "settings": [
            {
                "key": "theme",
                "value": "dark",
                "mt": 1640995200,
                "st": 1640995200.0,
            }
        ],
    }

    assert response["server_time"] == 1640995200
    assert response["reset"] == 0
    assert len(response["records"]) == 1
    assert len(response["settings"]) == 1


def test_get_updates_response_empty_updates():
    """GetUpdatesResponse handles empty updates."""
    response: GetUpdatesResponse = {
        "server_time": 1640995200,
        "reset": 0,
        "records": [],
        "settings": [],
    }

    assert response["server_time"] == 1640995200
    assert response["records"] == []
    assert response["settings"] == []
