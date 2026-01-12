from pathlib import Path
from shutil import copy2

from .ical import get_icalendar
from .notion import get_events, get_meetings


def get_icalendar_feed() -> bytes:
    events = get_events()
    calendar = get_icalendar(events, "Lobstah Bots Calendar")
    return calendar.to_ical()

def get_meetings_icalendar_feed() -> bytes:
    meetings = get_meetings()
    calendar = get_icalendar(meetings, "Lobstah Bots Meetings")
    return calendar.to_ical()

if __name__ == "__main__":
    ical_feed = get_icalendar_feed()
    file = Path(__file__).parent.parent / "build" / "calendar.ics"
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open("wb") as f:
        f.write(ical_feed)
    copy2(file, file.parent / "index.html")
    meetings_ical_feed = get_meetings_icalendar_feed()
    meetings_file = file.parent / "meetings.ics"
    with meetings_file.open("wb") as f:
        f.write(meetings_ical_feed)
    copy2(meetings_file, meetings_file.parent / "meetings.html")