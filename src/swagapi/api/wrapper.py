import httplib
import inspect
import json
import os

import requests
from swagapi.api.base_api import AbstractAPIModel
from django.http import JsonResponse
from django.views.generic import View


class ServerError(Exception):
    def __init__(self, details, model, response):
        self.details = details
        self.model = model
        self.response = response
        super(ServerError, self).__init__(self.details)

    def encode(self):
        return {
            "details": self.details,
            "expected": str(self.model),
            "actual": self.response
        }



class BadRequest(Exception):
    pass


class RequestView(View):
    URI = None
    DEFAULT_MODEL = None
    DEFAULT_RESPONSES = {}
    PARAMS_MODELS = {
        "get": None,
        "post": None,
        "delete": None,
        "put": None,
        "head": None,
        "patch": None,
        "trace": None,
    }
    RESPONSES_MODELS = {
        "get": None,
        "post": None,
        "delete": None,
        "put": None,
        "head": None,
        "patch": None,
        "trace": None,
    }
    TAGS = {
        "get": [],
        "post": [],
        "delete": [],
        "put": [],
        "head": [],
        "patch": [],
        "trace": [],
    }
    valid_methods = ["get", "post", "delete", "put", "head", "patch", "trace"]

    def dispatch(self, request, *args, **kwargs):
        try:
            method = request.method.lower()
            model = self.PARAMS_MODELS[method] \
                if self.PARAMS_MODELS[method] is not None else \
                        self.DEFAULT_MODEL

            if not (model is None or issubclass(model, AbstractAPIModel)):
                raise ServerError(
                    details="Method params model should be subclass of"
                            "{}".format(AbstractAPIModel),
                    model=model,
                    response=request
                )

            if model is not None and issubclass(model, AbstractAPIModel):
                try:
                    request_params = json.loads(request.body)

                except Exception as e:
                    raise ServerError(
                        details=e.message,
                        model=model,
                        response=request.body
                    )
                try:
                    model = model(request_params)

                except Exception as e:
                    raise ServerError(
                        details=e.message,
                        model=model,
                        response=request_params
                    )


            request.model = model
            return super(RequestView, self).dispatch(request, *args, **kwargs)

        except BadRequest as e:
            return JsonResponse(e.message,
                                status=httplib.BAD_REQUEST)

        except ServerError as e:
            return JsonResponse(e.encode(),
                                status=httplib.INTERNAL_SERVER_ERROR)

        except Exception as e:
            raise JsonResponse(e.message,
                                status=httplib.INTERNAL_SERVER_ERROR)

    @classmethod
    def implemented_methods(cls):
        return [m.lower() for m in cls.valid_methods if hasattr(cls, m)]

    @classmethod
    def execute(cls, base_url, method, data, logger=None):
        url = os.path.join(base_url, cls.URI)
        if logger:
            logger.debug("request: %s - %s - %s", url, method, data)

        response = requests.request(method, url, json=data)

        if logger:
            logger.debug("response: %s(%s) - %s",
                         httplib.responses[response.status_code],
                         response.status_code,
                         response.content)

        return response


class Response(JsonResponse):
    def __init__(self, response, status, *args, **kwargs):
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__
        the_method = stack[1][0].f_code.co_name

        responses_models = the_class.RESPONSES_MODELS[the_method]

        try:
            if responses_models is None or status not in responses_models:
                responses_models = the_class.DEFAULT_RESPONSES

            if responses_models is None or status not in responses_models:
                raise ServerError(
                    details="status code given is not defined in either "
                            "method dict or default dict",
                    model=the_class.RESPONSES_MODELS,
                    response=status
                )
            else:
                try:
                    responses_models[status].validate(response)

                except Exception as e:
                    raise ServerError(
                        details=e.message,
                        model=str(responses_models[status]),
                        response=response
                    )

        except ServerError as e:
            response = e.encode()
            status = httplib.INTERNAL_SERVER_ERROR

        except Exception as e:
            raise JsonResponse(e.message,
                                status=httplib.INTERNAL_SERVER_ERROR)

        super(Response, self).__init__(response, status=status, *args,
                                       **kwargs)