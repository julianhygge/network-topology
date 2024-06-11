import datetime
import decimal
import json
from uuid import UUID


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def uuid_convert(o):
    if isinstance(o, UUID):
        return o.hex
    else:
        return o


def to_json(json_dict):
    return json.dumps(json_dict, cls=UUIDEncoder)


def from_json(json_string):
    if not isinstance(json_string, str):
        return json.loads(json_string.decode('utf-8'))
    else:
        return json.loads(json_string)
