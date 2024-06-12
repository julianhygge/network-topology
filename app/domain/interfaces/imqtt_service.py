from abc import ABC, abstractmethod


class IMQTTService(ABC):

    @abstractmethod
    def send_message_to_topic(self, topic_name, message, broken_url, port):
        """"""

    @abstractmethod
    def sms_content_dict(self, application_name, mobile_no, otp, txn_id):
        """"""

    @abstractmethod
    def send_sms(self, topic_name, application_name, mobile_no, otp, txn_id):
        """"""

    @abstractmethod
    def to_json(self, json_dict):
        """"""
