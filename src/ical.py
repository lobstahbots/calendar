from .event import Event
import icalendar
from datetime import datetime, timedelta


def get_icalendar(events: list[Event], calendar_name: str) -> icalendar.Calendar:
    cal = icalendar.Calendar()
    cal.color = "#c40000"
    cal.calendar_name = calendar_name
    cal.add("X-WR-CALNAME", cal.calendar_name)
    for event in events:
        ical_event = icalendar.Event()
        ical_event.uid = event.id
        ical_event.add("summary", event.title)
        ical_event.start = event.start_date
        ical_event.color = "#c40000"
        if event.end_date and not isinstance(event.end_date, datetime):
            ical_event.end = event.end_date + timedelta(days=1)
        elif event.end_date:
            ical_event.end = event.end_date
        if event.location:
            if event.location.strip().lower() == "lab":
                event.location = "110 Cummington Mall, Boston, MA, 02215"
            ical_event.add("location", event.location)
        ical_event.add("description", event.description)
        cal.add_component(ical_event)
    return cal
