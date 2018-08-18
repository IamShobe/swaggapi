from __future__ import absolute_import

import inspect

from six.moves import http_client
from django.http import JsonResponse

from swaggapi.api.builder.server.exceptions import ServerError


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
                        details=str(e),
                        model=str(responses_models[status]),
                        response=response
                    )

        except ServerError as e:
            response = e.encode()
            status = http_client.INTERNAL_SERVER_ERROR

        super(Response, self).__init__(response, status=status, *args,
                                       **kwargs)
