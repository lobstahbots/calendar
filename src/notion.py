import os
from datetime import date
from itertools import chain
from typing import Any

import dotenv
from notion_client import Client
from notion_client.helpers import is_full_page, iterate_paginated_api

from .event import Event

dotenv.load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))


def get_plain_text(property) -> str:
    if property["type"] == "rich_text":
        return "".join([text_part["plain_text"] for text_part in property["rich_text"]])
    elif property["type"] == "title":
        return "".join([text_part["plain_text"] for text_part in property["title"]])
    raise ValueError(f"Unsupported property type: {property['type']}")


def get_date(property) -> tuple[date, date | None]:
    if property["type"] != "date" or property["date"] is None:
        raise ValueError(f"Unsupported or empty date property: {property}")
    return (
        date.fromisoformat(property["date"]["start"]),
        (
            date.fromisoformat(property["date"]["end"])
            if property["date"]["end"] is not None
            else None
        ),
    )


def get_events() -> list[Event]:
    database_id = os.getenv("NOTION_DATABASE_ID")
    if database_id is None:
        raise ValueError("NOTION_DATABASE_ID environment variable is not set.")
    database: Any = notion.databases.retrieve(database_id=database_id)
    data_sources: list[str] = [
        data_source["id"] for data_source in database["data_sources"]
    ]
    events = []
    for page in chain.from_iterable(
        iterate_paginated_api(
            notion.data_sources.query,
            data_source_id=data_source,
            sorts=[
                {
                    "property": "Date",
                    "direction": "ascending",
                }
            ],
        )
        for data_source in data_sources
    ):
        if not is_full_page(page):
            continue
        try:
            events.append(
                Event(
                    id=page["id"],
                    title=get_plain_text(page["properties"]["Name"]) or "Untitled",
                    start_date=get_date(page["properties"]["Date"])[0],
                    end_date=get_date(page["properties"]["Date"])[1],
                    location=get_plain_text(page["properties"]["Location"]),
                )
            )
        except ValueError as e:
            print(
                f"Skipping page {page['id']} ({get_plain_text(page['properties']['Name']) or 'Untitled'}) due to error: {e}"
            )
    return events


if __name__ == "__main__":
    print(get_events())
