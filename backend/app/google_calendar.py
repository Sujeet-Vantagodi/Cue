from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


class GoogleCalendarAdapter:
    """Google Calendar adapter with OAuth refresh-token persistence."""

    SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

    def __init__(self, credentials_path: Path, token_path: Path) -> None:
        self.credentials_path, self.token_path = credentials_path, token_path
        self._service: Any = None

    def _service_client(self) -> Any:
        if self._service is not None:
            return self._service
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        credentials = None
        if self.token_path.exists():
            credentials = Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), self.SCOPES)
                credentials = flow.run_local_server(port=0)
            self.token_path.write_text(credentials.to_json())
        self._service = build("calendar", "v3", credentials=credentials)
        return self._service

    @staticmethod
    def _start_date(value: str) -> date:
        # LLMs sometimes return an ISO datetime even though Cue requests an
        # all-day date. Keep the user's month/day, but never schedule it in
        # the past when the user did not provide a year.
        try:
            parsed_iso = datetime.fromisoformat(value.replace("Z", "+00:00")).date()
            if parsed_iso < date.today():
                parsed_iso = parsed_iso.replace(year=date.today().year)
                if parsed_iso < date.today():
                    parsed_iso = parsed_iso.replace(year=parsed_iso.year + 1)
            return parsed_iso
        except ValueError:
            pass
        for fmt in ("%Y-%m-%d", "%B %d", "%b %d"):
            try:
                parsed = datetime.strptime(value, fmt).date()
                if fmt != "%Y-%m-%d":
                    parsed = parsed.replace(year=datetime.now().year)
                    if parsed < date.today():
                        parsed = parsed.replace(year=parsed.year + 1)
                return parsed
            except ValueError:
                continue
        return date.today()

    async def create(self, args: dict[str, Any]) -> dict[str, Any]:
        service = self._service_client()
        raw_date_value = args.get("date") or args.get("start") or ""
        if isinstance(raw_date_value, dict):
            raw_date_value = raw_date_value.get("date") or raw_date_value.get("dateTime") or ""
        raw_date = str(raw_date_value)
        if not raw_date or raw_date == "TBD":
            raise ValueError("A concrete calendar date is required before creating an event")
        start = self._start_date(raw_date)
        event = service.events().insert(calendarId="primary", body={
            "summary": str(args.get("title", "Cue life-event task")),
            "description": "Created by Cue. Review before sharing.",
            "start": {"date": start.isoformat()},
            "end": {"date": (start + timedelta(days=1)).isoformat()},
        }).execute()
        return {"status": "done", "adapter": "google-calendar", "created_by": "cue", "external_id": event["id"], "link": event.get("htmlLink")}

    async def undo(self, args: dict[str, Any]) -> dict[str, Any]:
        self._service_client().events().delete(calendarId="primary", eventId=args["external_id"]).execute()
        return {"status": "undone", "adapter": "google-calendar", "external_id": args["external_id"]}
