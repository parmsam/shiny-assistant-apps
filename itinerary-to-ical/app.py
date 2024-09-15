from shiny import App, ui, render, reactive
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import re
import uuid

ui = ui.page_fluid(
    ui.panel_title("Itinerary to iCalendar Builder"),
    ui.markdown(f"""App will accept the following format:
    \nDate: Event - Location (Start time-End time) - URL (optional) - Notes (optional)
    """),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_text_area("itinerary", f"""Enter your itinerary:""", rows=10,
               value=f"""2024-10-05: Meeting #1 with John - Office (14:00-15:30) - https://zoom.us/j/123456 - Bring project files\n2024-10-16: Meeting #2 with John - Office (14:00-15:30) - https://zoom.us/j/123456 - Bring project files
                   """, 
               placeholder="Format: Date: Event - Location (Time) - URL - Notes\nExample:\n2023-06-15: Meeting with John - Office (14:00-15:30) - https://zoom.us/j/123456 - Bring project files\n2023-06-16: Dinner with family - Home (19:00-21:00) - - Remember to bring dessert"
            ),
            ui.input_text("timezone", "Enter your timezone (e.g., US/Eastern):", value="US/Hawaii"),
            ui.input_action_button("generate", "Generate iCalendar"),
            open="always"
        ),
        ui.output_text("preview"),
        ui.download_button("download", "Download iCalendar file"),
    )
)

def server(input, output, session):
    
    calendar = reactive.Value(None)
    
    @reactive.Effect
    @reactive.event(input.generate)
    def generate_calendar():
        cal = Calendar()
        cal.add('prodid', '-//Itinerary to iCalendar Converter//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        
        itinerary = input.itinerary()
        timezone = pytz.timezone(input.timezone())
        
        for line in itinerary.split('\n'):
            if line.strip():
                match = re.match(r'(\d{4}-\d{2}-\d{2}): (.*) - (.*) \((\d{2}:\d{2})-(\d{2}:\d{2})\)(?: - (\S+))?(?: - (.*))?', line)
                if match:
                    date, summary, location, start_time, end_time, url, notes = match.groups()
                    
                    event = Event()
                    event.add('summary', summary)
                    event.add('location', location)
                    
                    start_datetime = timezone.localize(datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M"))
                    end_datetime = timezone.localize(datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M"))
                    
                    event.add('dtstart', start_datetime)
                    event.add('dtend', end_datetime)
                    event.add('dtstamp', datetime.now(tz=timezone))
                    event.add('created', datetime.now(tz=timezone))
                    event.add('last-modified', datetime.now(tz=timezone))
                    event.add('uid', str(uuid.uuid4()))
                    
                    if url:
                        pass
                        event.add('url', url)
                    if notes:
                        pass
                        event.add('description', notes)
                    
                    cal.add_component(event)
        
        calendar.set(cal)

    @output
    @render.text
    def preview():
        if calendar() is None:
            return "Enter your itinerary and click 'Generate iCalendar' first."
        
        preview_text = "iCalendar Preview:\n\n"
        for component in calendar().walk():
            if component.name == "VEVENT":
                summary = component.get('summary')
                start = component.get('dtstart').dt
                end = component.get('dtend').dt
                location = component.get('location')
                url = component.get('url', '')
                notes = component.get('description', '')
                preview_text += f"{start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%H:%M')}: {summary} at {location}\n"
                if url:
                    preview_text += f"  URL: {url}\n"
                if notes:
                    preview_text += f"  Notes: {notes}\n"
                preview_text += "\n"
        
        return preview_text

    @output
    @render.download(
        filename=lambda: "itinerary.ics"
    )
    async def download():
        if calendar() is not None:
            yield calendar().to_ical()

app = App(ui, server)
