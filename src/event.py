from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Event:
    id: str
    title: str
    start_date: date
    end_date: Optional[date] = None
    location: Optional[str] = None
    description: str = ""
