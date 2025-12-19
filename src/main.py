from .notion import get_events
from .ical import get_icalendar

def get_icalendar_feed() -> bytes:
    events = get_events()
    calendar = get_icalendar(events)
    return calendar.to_ical()

if __name__ == "__main__":
    ical_feed = get_icalendar_feed()
    with open("build/calendar.ics", "wb") as f:
        f.write(ical_feed)