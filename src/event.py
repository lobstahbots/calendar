from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Event:
    id: str
    title: str
    start_date: date | datetime
    end_date: Optional[date | datetime] = None
    location: Optional[str] = None
    description: str = ""
