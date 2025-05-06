from app.config.i_configuration import IConfiguration
from app.domain.interfaces.i_mqtt_service import IMqttService
from app.domain.interfaces.i_sms_service import ISmsService
from app.utils.logger import logger


class SmsService(ISmsService):
    def __init__(
        self, configuration: IConfiguration, mqtt_service: IMqttService
    ):
        self._mqtt_service = mqtt_service
        self._default_number = configuration.sms.default_number
        self._application_name = configuration.mqtt.application_name
        self._topic = configuration.sms.topic

    def send_otp_sms(self, phone_number: str, otp: str, txn_id: str):
        try:
            if phone_number != self._default_number:
                topic_name = self._topic
                application_name = self._application_name
                self._mqtt_service.send_sms(
                    topic_name=topic_name,
                    application_name=application_name,
                    mobile_no=phone_number,
                    otp=otp,
                    txn_id=txn_id,
                )
        except Exception as e:
            logger.error("Failed to push sms message in queue: %s", e)
            # raise
