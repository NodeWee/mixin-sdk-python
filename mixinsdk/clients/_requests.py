import json
import uuid
from typing import Union

import httpx


class HttpRequest:
    def __init__(self, host_uri, get_auth_token: callable):
        self.get_auth_token = get_auth_token
        # get_auth_token() parameters: method: str, uri: str, bodystring: str

        self.host_uri = host_uri
        self.session = httpx.Client()

    def get(self, path, query_params: dict = None, request_id=None):
        if query_params:
            params_string = "&".join(f"{k}={v}" for k, v in query_params.items())
            path = f"{path}?{params_string}"

        url = self.host_uri + path
        headers = {"Content-Type": "application/json"}

        auth_token = self.get_auth_token("GET", path, "")
        if auth_token:
            headers["Authorization"] = "Bearer " + auth_token

        request_id = request_id if request_id else str(uuid.uuid4())
        headers["X-Request-Id"] = request_id

        r = self.session.get(url, headers=headers)
        r = r.json()

        return r

    def post(
        self, path, body: Union[dict, list], query_params: dict = None, request_id=None
    ):
        if query_params:
            params_string = "&".join(f"{k}={v}" for k, v in query_params.items())
            path = f"{path}?{params_string}"

        url = self.host_uri + path
        headers = {"Content-Type": "application/json"}
        bodystring = json.dumps(body)
        auth_token = self.get_auth_token("POST", path, bodystring)
        if auth_token:
            headers["Authorization"] = "Bearer " + auth_token

        request_id = request_id if request_id else str(uuid.uuid4())
        headers["X-Request-Id"] = request_id

        r = self.session.post(url, data=bodystring, headers=headers)
        r = r.json()

        # error response JSON have the key "error",
        # else have any data or empty JSON on success.
        """ example of error response:
        {
            "error": {
                "status": 202,
                "code": 20118,
                "description": "Invalid PIN format.",
            }
        }
        """

        if "error" in r:
            raise Exception(r["error"])

        return r
