"""Implementation of the MQTT Service."""

import json
from typing import Any, Dict

import paho.mqtt.client as mqtt

from app.config.i_configuration import IConfiguration
from app.domain.interfaces.i_mqtt_service import IMqttService
from app.utils.json_util import UUIDEncoder


class MQTTService(IMqttService):
    """
    Service class for handling MQTT communication.
    """

    def __init__(self, configuration: IConfiguration):
        """
        Initializes the MQTTService with configuration.

        Args:
            configuration: The application configuration.
        """
        self._username = configuration.mqtt.username
        self._password = configuration.mqtt.password
        self._broken_url = configuration.mqtt.broken_url
        self._port = int(configuration.mqtt.port)

    def send_message_to_topic(self, topic_name: str, message: str):
        """
        Sends a message to a specified MQTT topic.

        Args:
            topic_name: The name of the topic.
            message: The message content.
        """
        client = mqtt.Client()
        client.username_pw_set(
            username=self._username, password=self._password
        )
        client.connect(self._broken_url, self._port, 60)
        client.publish(topic_name, message, qos=2)
        client.disconnect()

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
        return {
            "meta": application_name,
            "phoneNumber": mobile_no,
            "content": {
                "otp": otp,
            },
            "txnId": txn_id,
        }

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
        message = self.to_json(
            self.sms_content_dict(application_name, mobile_no, otp, txn_id)
        )
        self.send_message_to_topic(topic_name, message)

    def to_json(self, json_dict: Dict[str, Any]) -> str:
        """
        Converts a dictionary to a JSON string.

        Args:
            json_dict: The dictionary to convert.

        Returns:
            A JSON string representation of the dictionary.
        """
        return json.dumps(json_dict, cls=UUIDEncoder)
