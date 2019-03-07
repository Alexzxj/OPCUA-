import json
import decimal
from datetime import date
from datetime import datetime



class JsonExtendEncoder(json.JSONEncoder):
    """
        This class provide an extension to json serialization for datetime/date.
    """

    def default(self, o):
        """
            provide a interface for datetime/date
        """
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, bytes):
            return int.from_bytes(o, byteorder='big', signed=True)
        else:
            return json.JSONEncoder.default(self, o)

