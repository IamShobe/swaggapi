import re
from api.openapi.utils import get_schema
from django.conf.urls import url

from .api.base_api import Field, AbstractResponse, NoContentResponse
from .api.openapi.models import (Operation,
                                 Parameter,
                                 Path,
                                 Componenets,
                                 OpenAPI, RequestBody, Media, Schema, Server)


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
        return [url(r"^{}/?".format(request.URI), request.VIEW.__func__)
                for request in self.requests]

    def _build_parameters(self, parameters):
        params = []
        body_content = {}
        required_fields = []
        example = {}
        for param in parameters:
            if not isinstance(param, Field):
                raise RuntimeError("{} expected, got {}".format(
                    Field.__name__, type(param)))

            schema = get_schema(param, self.scheme_bank, "schemas")
            if param.location is "body":
                body_content[param.name] = schema
                required_fields.append(param.name)
                example[param.name] = param.example

            else:
                params.append(Parameter(name=param.name,
                                        description=param.description,
                                        required=param.required,
                                        schema=schema,
                                        examples=param.example,
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
            if isinstance(model, AbstractResponse):
                resp = model

            return_dict[str(response)] = resp.encode(self.scheme_bank)

        return return_dict

    def _build_paths(self):
        paths = {}
        for request in self.requests:
            path = "/" + request.URI
            method = request.METHOD.lower()
            summery = request.__doc__

            request_body, parameters = self._build_parameters(request.PARAMS)
            operation = Operation(tags=request.TAGS,
                                  summery=summery,
                                  description=summery,
                                  requestBody=request_body,
                                  responses=self._build_responses(
                                      request.RESPONSES))

            paths[path] = Path(summery=summery,
                               parameters=parameters,
                               **{method: operation})

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
