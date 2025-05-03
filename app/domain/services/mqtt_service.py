import json

import paho.mqtt.client as mqtt

from app.domain.interfaces.i_mqtt_service import IMQTTService
from app.utils.json_util import UUIDEncoder


class MQTTService(IMQTTService):
    def __init__(self, configuration):
        self._username = configuration.mqtt.username
        self._password = configuration.mqtt.password
        self._broken_url = configuration.mqtt.broken_url
        self._port = int(configuration.mqtt.port)

    def send_message_to_topic(self, topic_name, message, broken_url, port):
        client = mqtt.Client()
        client.username_pw_set(username=self._username, password=self._password)
        client.connect(self._broken_url, port, 60)
        client.publish(topic_name, message, qos=2)
        client.disconnect()

    def sms_content_dict(self, application_name, mobile_no, otp, txn_id):
        return {
            "meta": application_name,
            "phoneNumber": mobile_no,
            "content": {
                "otp": otp,
            },
            "txnId": txn_id,
        }

    def send_sms(self, topic_name, application_name, mobile_no, otp, txn_id):
        message = self.to_json(
            self.sms_content_dict(application_name, mobile_no, otp, txn_id)
        )
        self.send_message_to_topic(
            topic_name, message, self._broken_url, int(self._port)
        )

    def to_json(self, json_dict):
        return json.dumps(json_dict, cls=UUIDEncoder)
