import os

from swaggapi.api.builder.common.model import AbstractAPIModel


class Requester(object):
    def __init__(self, host, port, base_url, logger=None):
        self.base_url = os.path.join("http://{}:{}/".format(host, port),
                                     base_url)
        self.logger = logger

    def request(self, request_type, method, data):
        if not isinstance(data, AbstractAPIModel):
            raise ValueError("data must be an instance of AbstractAPIModel!")

        response = request_type.execute(self.base_url, method,
                                        data.obj, logger=self.logger)

        response_code = response.status_code
        responses_models = request_type.RESPONSES_MODELS[method]
        if responses_models is None or \
                not response_code in responses_models:
            responses_models = request_type.DEFAULT_RESPONSES
        try:
            content = response.json() if response.content else {}
        except:
            return response.content

        response = responses_models[response_code](content)
        response.code = response_code
        return response
