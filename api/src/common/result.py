import json


class Result:
    """Backend unified response payload"""
    def __init__(self, code, msg, data):
        self.code = code  # status code: 1 success, 0 failure
        self.msg = msg  # message
        self.data = data  # optional response data payload

    @classmethod
    def success(cls, msg="", data={}) -> dict:
        """successful result with optional data"""
        return cls(code=1, msg=msg, data=data).to_dict()

    @classmethod
    def error(cls, msg="", data={}) -> dict:
        """Error result with optional data"""
        return cls(code=0, msg=msg, data=data).to_dict()

    def to_dict(self):
        """Convert to dict for JSON serialization"""
        return {
            'code': self.code,
            'msg': self.msg,
            'data': self.data
        }

    def to_json(self):
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)

    def __str__(self):
        return f"Result(code={self.code}, msg='{self.msg}', data={self.data})"

    def __repr__(self):
        return self.__str__()
