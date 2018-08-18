from __future__ import absolute_import

import os
import json

from django.test import Client
from swaggapi.api.builder.common.model import AbstractAPIModel


class Requester(object):
    def __init__(self, host, port, base_url, logger=None):
        self.base_url = os.path.join("http://{}:{}/".format(host, port),
                                     base_url)
        self.logger = logger

    def make_request(self, request_type, method, data):
        response = request_type.execute(self.base_url, method,
                                        data.obj, logger=self.logger)
        try:
            content = response.json() if response.content else {}

        except:
            with open('error.html', "w") as f:
                f.write(response.content)

            raise RuntimeError("Invalid response received!")

        return response, content

    def request(self, request_type, method, data):
        if not isinstance(data, AbstractAPIModel):
            raise ValueError("data must be an instance of AbstractAPIModel!")

        response, content = self.make_request(request_type, method, data)

        response_code = response.status_code
        responses_models = request_type.RESPONSES_MODELS[method]
        if responses_models is None or \
                not response_code in responses_models:
            responses_models = request_type.DEFAULT_RESPONSES

        response = responses_models[response_code](content)
        response.code = response_code
        return response


# django client tester
class TestRequester(Requester):
    def __init__(self, host, port, base_url, logger=None):
        super(TestRequester, self).__init__(host, port, base_url, logger)
        self.client = Client()

    def make_request(self, request_type, method, data):
        response = self.client.generic(
            method, os.path.join(self.base_url, request_type.URI),
            data=json.dumps(data.obj),
            content_type="application/json")

        try:
            return response, json.loads(response.content)

        except:
            return (response,
             response.content if response.content != "" else {})
