"""Interface for the MQTT Service."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IMqttService(ABC):
    """Abstract base class for the MQTT Service."""

    @abstractmethod
    def send_message_to_topic(self, topic_name: str, message: str):
        """
        Sends a message to a specified MQTT topic.

        Args:
            topic_name: The name of the topic.
            message: The message content.
        """

    @abstractmethod
    def sms_content_dict(
        self, application_name: str, mobile_no: str, otp: str, txn_id: str
    ) -> Dict[str, Any]:
        """
        Returns a dictionary containing SMS content.

        Args:
            application_name: The name of the application.
            mobile_no: The mobile number.
            otp: The one-time password.
            txn_id: The transaction ID.

        Returns:
            A dictionary with SMS content.
        """

    @abstractmethod
    def send_sms(
        self,
        topic_name: str,
        application_name: str,
        mobile_no: str,
        otp: str,
        txn_id: str,
    ):
        """
        Formats and sends an SMS message via MQTT.

        Args:
            topic_name: The MQTT topic for SMS messages.
            application_name: The name of the application.
            mobile_no: The recipient's mobile number.
            otp: The one-time password.
            txn_id: The transaction ID.
        """

    @abstractmethod
    def to_json(self, json_dict: Dict[str, Any]) -> str:
        """
        Converts a dictionary to a JSON string.

        Args:
            json_dict: The dictionary to convert.

        Returns:
            A JSON string representation of the dictionary.
        """
