from typing import TypedDict


class Record(TypedDict):
    """
    A TimeTagger record object
    """

    key: str
    mt: int
    t1: int
    t2: int
    ds: str
    st: float


class Settings(TypedDict):
    """
    A TimeTagger settings object
    """

    key: str
    value: str
    mt: int
    st: float


class GetRecordsResponse(TypedDict):
    """
    A response from the Timetagger API at `GET /records`
    """

    records: list[Record]


class PutRecordsResponse(TypedDict):
    """
    A response from the Timetagger API at `PUT /records`
    """

    accepted: list[str]
    failed: list[str]
    errors: list[str]


class GetSettingsResponse(TypedDict):
    """
    A response from the Timetagger API at `GET /settings`
    """

    settings: list[Settings]


class PutSettingsResponse(TypedDict):
    """
    A response from the Timetagger API at `PUT /settings`
    """

    accepted: list[str]
    failed: list[str]
    errors: list[str]


class GetUpdatesResponse(TypedDict):
    """
    A response from the Timetagger API at `GET /updates`
    """

    server_time: int
    reset: bool
    records: list[Record]
    settings: list[Settings]
