import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


class Notifier:
    """Sends SMS or WhatsApp messages via Twilio."""

    def __init__(self, account_sid: str, auth_token: str, from_number: str, to_number: str):
        self._client = Client(account_sid, auth_token)
        self._from = from_number
        self._to = to_number

    def send_sms(self, body: str) -> str:
        """Send an SMS message. Returns the message status string."""
        message = self._client.messages.create(
            body=body,
            from_=self._from,
            to=self._to,
        )
        return message.status

    def send_whatsapp(self, body: str) -> str:
        """
        Send a WhatsApp message. from_ and to must be prefixed with 'whatsapp:'.
        Returns the message status string.
        """
        from_wa = self._from if self._from.startswith("whatsapp:") else f"whatsapp:{self._from}"
        to_wa = self._to if self._to.startswith("whatsapp:") else f"whatsapp:{self._to}"
        message = self._client.messages.create(
            body=body,
            from_=from_wa,
            to=to_wa,
        )
        return message.status
