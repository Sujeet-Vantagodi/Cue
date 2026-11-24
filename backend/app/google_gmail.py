from __future__ import annotations

import base64
from email.message import EmailMessage
from pathlib import Path
from typing import Any


class GoogleGmailAdapter:
    """Google Gmail adapter limited to draft creation and deletion."""

    SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

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
        self._service = build("gmail", "v1", credentials=credentials)
        return self._service

    @staticmethod
    def _message(args: dict[str, Any]) -> dict[str, str]:
        message = EmailMessage()
        if args.get("to"):
            message["To"] = str(args["to"])
        message["Subject"] = str(args.get("subject", "Cue draft"))
        message.set_content(str(args.get("body", "")))
        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode().rstrip("=")
        return {"raw": encoded}

    async def create(self, args: dict[str, Any]) -> dict[str, Any]:
        draft = self._service_client().users().drafts().create(
            userId="me", body={"message": self._message(args)}
        ).execute()
        return {
            "status": "done",
            "adapter": "google-gmail",
            "created_by": "cue",
            "external_id": draft["id"],
        }

    async def undo(self, args: dict[str, Any]) -> dict[str, Any]:
        self._service_client().users().drafts().delete(
            userId="me", id=args["external_id"]
        ).execute()
        return {
            "status": "undone",
            "adapter": "google-gmail",
            "external_id": args["external_id"],
        }
