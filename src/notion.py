import os
from datetime import date, datetime, timedelta
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
    elif property["type"] == "select":
        return property["select"]["name"] if property["select"] is not None else ""
    raise ValueError(f"Unsupported property type: {property['type']}")


def get_date(property) -> tuple[date | datetime, date | datetime | None]:
    if property["type"] != "date" or property["date"] is None:
        raise ValueError(f"Unsupported or empty date property: {property}")
    return (
        (
            date.fromisoformat(property["date"]["start"])
            if "T" not in property["date"]["start"]
            else datetime.fromisoformat(property["date"]["start"])
        ),
        (
            (
                date.fromisoformat(property["date"]["end"])
                if "T" not in property["date"]["end"]
                else datetime.fromisoformat(property["date"]["end"])
            )
            if property["date"]["end"] is not None
            else (
                None
                if "T" not in property["date"]["start"]
                else datetime.fromisoformat(property["date"]["start"])
                + timedelta(hours=1)
            )
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


def get_meetings() -> list[Event]:
    database_id = os.getenv("NOTION_MEETING_DATABASE_ID")
    if database_id is None:
        raise ValueError("NOTION_MEETING_DATABASE_ID environment variable is not set.")
    database: Any = notion.databases.retrieve(database_id=database_id)
    data_sources: list[str] = [
        data_source["id"] for data_source in database["data_sources"]
    ]
    events: list[Event] = []
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
                    description=f"Meeting type: {get_plain_text(page['properties']['Meeting type'])}\n",
                )
            )
            match events[-1].location.lower().strip() if events[-1].location else "":
                case "lab":
                    events[-1].location = "110 Cummington Mall, Boston, MA 02215"
                case "wpi":
                    events[-1].location = "229 Grove St, Worcester, MA 01605"
                case "bua":
                    events[-1].location = "1 University Rd, Boston, MA 02215"
                case "zoom":
                    events[-1].location = None
                    events[
                        -1
                    ].description += "Zoom link: https://lobstahbots.com/url/zoom\n"
        except ValueError as e:
            print(
                f"Skipping page {page['id']} ({get_plain_text(page['properties']['Name']) or 'Untitled'}) due to error: {e}"
            )
    return events


if __name__ == "__main__":
    print(get_events())
    print(get_meetings())
