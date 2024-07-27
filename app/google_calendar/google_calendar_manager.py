import os.path
import datetime as dt
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarManager:
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    def list_upcoming_events(self, max_results=50):
        now = dt.datetime.now().isoformat() + "Z"
        tomorrow = (dt.datetime.now() + dt.timedelta(days=14)).replace(hour=23,
                                                                      minute=59, second=0, microsecond=0).isoformat() + "Z"

        events_result = self.service.events().list(
            calendarId='primary', timeMin=now, timeMax=tomorrow,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        return events

    def update_event_color(self, event_id, color_id=None, summary=None):
        event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
        if color_id:
            event['colorId'] = color_id
        if summary:
            event['summary'] = summary
        updated_event = self.service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return updated_event

    def get_event_id_by_start_time(self, start_time, max_results=50):
        now = dt.datetime.now().isoformat() + "Z"
        tomorrow = (dt.datetime.now() + dt.timedelta(days=14)).replace(hour=23, minute=59, second=0,
                                                                       microsecond=0).isoformat() + "Z"

        events_result = self.service.events().list(
            calendarId='primary', timeMin=now, timeMax=tomorrow,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        for event in events:
            event_start = event.get('start').get('dateTime', event.get('start').get('date'))
            if event_start == start_time:
                return event.get('id')

        return None


calendar = GoogleCalendarManager()
