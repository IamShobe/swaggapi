from __future__ import absolute_import

import os
import json
import six.moves.urllib.request, six.moves.urllib.parse, six.moves.urllib.error

from django.test import Client
from swaggapi.api.builder.utils import get_dict_leafs
from swaggapi.api.builder.common.model import AbstractAPIModel


class Requester(object):
    def __init__(self, host, port, base_url, logger=None):
        self.base_url = os.path.join("http://{}:{}/".format(host, port),
                                     base_url)
        self.logger = logger

    def make_request(self, request_type, method, data=None):
        if data is None:
            response = request_type.execute(self.base_url, method,
                                            logger=self.logger)

        else:
            response = request_type.execute(self.base_url, method,
                                            data.body,
                                            get_dict_leafs(data.params),
                                            logger=self.logger)
        try:
            content = response.json() if response.content else {}

        except:
            with open('error.html', "w") as f:
                f.write(response.content)

            raise RuntimeError("Invalid response received!")

        return response, content

    def request(self, request_type, method, data=None):
        if data is not None and not isinstance(data, AbstractAPIModel):
            raise ValueError("data must be an instance of AbstractAPIModel!")

        response, content = \
            self.make_request(request_type, method, data)

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

    def make_request(self, request_type, method, data=None):
        params = ""
        if data and data.params:
            params = six.moves.urllib.parse.urlencode(
                {key: str(value) for key, value in get_dict_leafs(
                    data.params).items()})

        response = self.client.generic(
            method,
            "{}?{}".format(os.path.join(self.base_url, request_type.URI),
                           params),
            data=json.dumps(data.body) if data else None,
            content_type="application/json")

        response_content = response.content.decode("utf-8")

        try:
            return response, json.loads(response_content)

        except:
            return (response,
                    response_content if response_content != "" else {})
