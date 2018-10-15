from __future__ import absolute_import

import re

from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from swaggapi.api.builder.utils import get_schema
from swaggapi.api.builder.common.fields import Field
from swaggapi.api.builder.common.response import (NoContentResponse,
                                                  AbstractResponse)
from swaggapi.api.openapi.models import (Operation,
                                         Parameter,
                                         Path,
                                         Componenets,
                                         OpenAPI,
                                         RequestBody,
                                         Media,
                                         Schema,
                                         Server,
                                         Example)


class Swagger(object):
    def __init__(self, info, requests, mount_url, tags=None):
        self.info = info
        self.tags = tags
        self.requests = requests
        self.mount_url = mount_url

        self.scheme_bank = {
            "schemas": {},
            "responses": {},
            "parameters": {},
            "examples": {},
            "requestBodies": {},
            "headers": {},
            "securitySchemes": {},
            "links": {},
            "callbacks": {}
        }

        self.api = self._build_file()

    def get_django_urls(self):
        return [url(r"^{}/?".format(request.URI),
                    csrf_exempt(request.as_view()))
                for request in self.requests]

    def _build_parameters(self, param_model):
        params = []
        body_content = {}
        required_fields = []
        example = None
        if param_model is not None:
            for param in param_model.PROPERTIES:
                if not isinstance(param, Field):
                    raise RuntimeError("{} expected, got {}".format(
                        Field.__name__, type(param)))

                schema = get_schema(param, self.scheme_bank, "schemas")
                if param.location is "body":
                    if example is None:
                        example = {}

                    example[param.name] = param.example
                    body_content[param.name] = schema
                    required_fields.append(param.name)

                else:
                    params.append(Parameter(name=param.name,
                                            description=param.description,
                                            required=param.required,
                                            schema=[schema],
                                            examples={
                                                "default":
                                                    Example(
                                                        value=param.example)},
                                            deprecated=param.deprecated,
                                            **{"in": param.location}))

        return RequestBody(content={
            "application/json": Media(schema=Schema(properties=body_content,
                                                    required=required_fields,
                                                    example=example))
        }), params

    def _build_responses(self, responses):
        return_dict = {}
        for response, model in responses.items():
            resp = NoContentResponse
            if issubclass(model, AbstractResponse):
                resp = model

            return_dict[str(int(response))] = resp.encode(self.scheme_bank)

        return return_dict

    def _build_paths(self):
        paths = {}
        for request in self.requests:
            path = "/" + request.URI
            path_description = request.__doc__
            path_summary = path_description.split("\n", 1)[0] \
                if path_description else None
            methods = request.implemented_methods()
            path_methods = {}
            parameters = []
            default_responses = {}
            if request.DEFAULT_RESPONSES is not None:
                default_responses = self._build_responses(
                    request.DEFAULT_RESPONSES)

            default_body = None
            if request.DEFAULT_MODEL is not None:
                default_body, parameters = self._build_parameters(
                    request.DEFAULT_MODEL
                )

            for method in methods:
                description = request.__doc__
                summary = description.split("\n", 1)[
                    0] if description else None

                params = parameters
                request_body = None
                if request.PARAMS_MODELS[method] is not None:
                    request_body, params = self._build_parameters(
                        request.PARAMS_MODELS[method])

                elif default_body is not None:
                    request_body = default_body

                responses = {}
                if request.RESPONSES_MODELS[method] is not None:
                    responses = self._build_responses(
                        request.RESPONSES_MODELS[method])

                operation_responses = default_responses.copy()
                operation_responses.update(responses)

                if operation_responses == {}:
                    operation_responses = None

                operation = Operation(tags=request.TAGS[method],
                                      summary=summary,
                                      description=description,
                                      parameters=params,
                                      requestBody=request_body,
                                      responses=operation_responses)
                path_methods[method] = operation

            paths[path] = Path(summary=path_summary,
                               description=path_description,
                               parameters=parameters,
                               **path_methods)

        return paths

    def _build_file(self):
        paths = self._build_paths()
        components = Componenets(**self.scheme_bank)
        return OpenAPI(openapi="3.0.1", info=self.info,
                       paths=paths, components=components,
                       tags=self.tags)

    def configure_base_url(self, request):
        full_path = request.build_absolute_uri()
        pattern = r"(?P<base_url>.*?/{}).*".format(self.mount_url)
        match = re.match(pattern, full_path)
        self.api.servers = [Server(url=str(match.group("base_url")))]
