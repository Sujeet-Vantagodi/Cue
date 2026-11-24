import base64
from email import policy
from email.parser import BytesParser

from app.google_gmail import GoogleGmailAdapter


def test_gmail_draft_message_is_encoded_without_sending() -> None:
    payload = GoogleGmailAdapter._message({
        "to": "hr@example.com",
        "subject": "Joining details",
        "body": "Could you confirm the next steps?",
    })
    message = BytesParser(policy=policy.default).parsebytes(
        base64.urlsafe_b64decode(payload["raw"] + "==")
    )
    assert message["To"] == "hr@example.com"
    assert message["Subject"] == "Joining details"
    assert "next steps" in message.get_content()

