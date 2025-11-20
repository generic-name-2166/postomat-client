from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from attrs import define
import cattrs
from cattrs.converters import Converter
import humps


def _datetime_hook(s: str, _: Any) -> datetime:  # pyright: ignore[reportExplicitAny]
    return datetime.fromisoformat(s)


_converter: Converter = cattrs.Converter()
_converter.register_structure_hook(datetime, _datetime_hook)


type _CamelCaseParams = (
    str | Mapping[str, _CamelCaseParams | int | None] | Sequence[_CamelCaseParams]
)


class CamelCaseConverter:
    converter: Converter = _converter

    def load[T](
        self, params: _CamelCaseParams, data_cls: type[T], camel_to_snake: bool = True
    ) -> T:
        """Convert camelCase keys to snake_case before structuring."""
        if camel_to_snake:
            params = humps.depascalize(params)  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
        return self.converter.structure(params, data_cls)

    def dump(self, data: Any, snake_to_camel: bool = False) -> _CamelCaseParams:  # pyright: ignore[reportExplicitAny, reportAny]
        """Convert snake_case keys to camelCase when unstructuring."""
        result: _CamelCaseParams = self.converter.unstructure(data)  # pyright: ignore[reportAny]
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
