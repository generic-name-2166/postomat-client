from collections.abc import Mapping, Sequence
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import smtplib
from typing import Any

from attrs import define
import cattrs
from cattrs.converters import Converter
import httpx
from httpx import Response
import humps


def _datetime_hook(s: str, _: Any) -> datetime:  # pyright: ignore[reportExplicitAny]
    return datetime.fromisoformat(s)


_converter: Converter = cattrs.Converter()
_converter.register_structure_hook(datetime, _datetime_hook)


type CamelCaseParams = (
    str | Mapping[str, CamelCaseParams | int | None] | Sequence[CamelCaseParams]
)


class CamelCaseConverter:
    converter: Converter = _converter

    def load[T](
        self, params: CamelCaseParams, data_cls: type[T], camel_to_snake: bool = True
    ) -> T:
        """Convert camelCase keys to snake_case before structuring."""
        if camel_to_snake:
            params = humps.depascalize(params)  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
        return self.converter.structure(params, data_cls)

    def dump(self, data: Any, snake_to_camel: bool = False) -> CamelCaseParams:  # pyright: ignore[reportExplicitAny, reportAny]
        """Convert snake_case keys to camelCase when unstructuring."""
        result: CamelCaseParams = self.converter.unstructure(data)  # pyright: ignore[reportAny]
        if snake_to_camel:
            result = humps.camelize(result)  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
        return result  # pyright: ignore[reportUnknownVariableType]


@define
class Cell:
    id: int
    name: str
    cell_id: int
    # actually 0 and 1 boolean
    active: int
    session_id: str | None
    position: str | None
    block: str | None
    created_at: datetime
    updated_at: datetime


async def get_status(base_url: str) -> list[Cell]:
    c: CamelCaseConverter = CamelCaseConverter()
    url: str = f"{base_url}:5003/storage"
    async with httpx.AsyncClient() as client:
        r: Response = await client.get(url)
        params: CamelCaseParams = r.json()["data"]  # pyright: ignore[reportAny]
        body: list[Cell] = c.load(params, list[Cell])
        return body


async def open_cell(base_url: str, cell_id: int) -> None:
    url: str = f"{base_url}:5003/storage/{cell_id}/open"
    async with httpx.AsyncClient() as client:
        _: Response = await client.get(url)


def scan_folder(path: Path) -> list[str]:
    files: list[str] = [filename[0] for _path, _, filename in path.walk()]
    return files


def send_email(sender_email: str, receiver_email: str, password: str, subject: str, contents: str) -> None:
    """
    only yandex for now 
    TODO which email service is used
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(contents, "plain"))
    with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as server: # https://www.getmailbird.com/setup/access-mail-ru-via-imap-smtp
        _ = server.login(sender_email, password)
        _ = server.sendmail(sender_email, receiver_email, message.as_string())


def main() -> None:
    import json

    example = """
    {
        "message": "OK",
        "data": [
            {
                "id": 1,
                "name": "1",
                "cellId": 1,
                "active": 1,
                "sessionId": null,
                "position": null,
                "block": null,
                "createdAt": "2022-08-23T07:07:45.000Z",
                "updatedAt": "2022-08-23T08:01:22.000Z"
            },
            {
                "id": 2,
                "name": "2",
                "cellId": 2,
                "active": 1,
                "sessionId": null,
                "position": null,
                "block": null,
                "createdAt": "2022-08-23T13:19:53.000Z",
                "updatedAt": "2022-08-24T13:38:17.000Z"
            },
            {
                "id": 3,
                "name": "3",
                "cellId": 3,
                "active": 1,
                "sessionId": null,
                "position": null,
                "block": null,
                "createdAt": "2022-08-23T13:19:53.000Z",
                "updatedAt": "2022-08-24T13:38:19.000Z"
            },
            {
                "id": 4,
                "name": "4",
                "cellId": 4,
                "active": 1,
                "sessionId": null,
                "position": null,
                "block": null,
                "createdAt": "2022-08-23T13:19:53.000Z",
                "updatedAt": "2022-08-23T13:19:57.000Z"
            },
            {
                "id": 5,
                "name": "5",
                "cellId": 5,
                "active": 0,
                "sessionId": null,
                "position": null,
                "block": null,
                "createdAt": "2022-09-01T13:22:22.000Z",
                "updatedAt": "2022-09-01T13:22:29.000Z"
            }
        ]
    }
    """
    c: CamelCaseConverter = CamelCaseConverter()
    params: list[dict[str, str | int | None]] = json.loads(example)["data"]  # pyright: ignore[reportAny]
    print(params)
    print(c.load(params, list[Cell]))


if __name__ == "__main__":
    main()
