import json
import os

import re

from astroid.decorators import cachedproperty
from api.base_api import ArrayField, ModelField


BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))


class SwaggerBuilder(object):
    def __init__(self, requests, request, base_uri):
        self._models = {}
        self.request = request
        self.requests = requests
        self.base_uri = base_uri

    def _parse_type(self, type_name):
        premative_types = [
            "array",
            "object",
            "string",
            "integer"
        ]
        if type_name is "model":
            type_name = "object"

        if type_name not in premative_types:
            mod = __import__('rotest.management.common.requests',
                             fromlist=[type_name])
            klass = getattr(mod, type_name)

            return klass

        else:
            return type_name

    def _build_model_properties(self, properties):
        return_dict = {}
        for property in properties:
            property.type = self._parse_type(property.type)
            return_dict[property.name] = {
                "type": property.type
            }
            if isinstance(property, ArrayField):
                return_dict[property.name].update({
                    "items": {
                        "$ref": self._get_model_referance(property.items_type)
                    }
                })

        return return_dict

    def _build_model(self, model):
        self._models[model.__name__] = {
            "title": model.TITLE,
            "required": [field.name for field in model.PROPERTIES
                         if field.required],
            "description": model.__doc__,
            "type": "object",
            "properties": self._build_model_properties(model.PROPERTIES)
        }

    def _get_model_referance(self, model):
        if not model.TITLE in self._models:
            self._build_model(model)

        return "#/components/schemas/{}".format(model.__name__)

    def  _build_parameters(self, parameters):
        parameters_list = []
        for parameter in parameters:
            parameter.type = self._parse_type(parameter.type)
            current_parameter = {
                "name": parameter.name,
                "in": "body",
                "description": parameter.description,
                "required": parameter.required,
                "schema": {
                    "type": parameter.type
                }
            }
            if isinstance(parameter, ModelField):
                current_parameter["schema"].update({
                    "$ref": self._get_model_referance(parameter.model)
                })

            elif isinstance(parameter, ArrayField):
                current_parameter["schema"].update({
                    "items": {
                        "$ref": self._get_model_referance(
                            self._parse_type(parameter.items_type))
                    }
                })

            parameters_list.append(current_parameter)

        return parameters_list

    def _build_responses(self, responses):
        return_dict = {}
        for response_code, response_model in responses.items():
            return_dict[response_code] = {
                "description": "No Content",
                "content": {
                    "application/json": {
                        "schema": {}
                    }
                }
            }
            if response_model is not None:
                return_dict[response_code]["description"] = \
                    response_model.__doc__
                content = \
                    return_dict[response_code]["content"]["application/json"]
                content["schema"] = {
                    "$ref": self._get_model_referance(response_model)
                }

        return return_dict

    def _build_swagger_methods(self, request):
        return {
            request.METHOD.lower(): {
                "tags": request.TAGS,
                "description": request.__doc__,
                "operationID": request.__name__,
                "parameters": self._build_parameters(request.PARAMS),
                "responses": self._build_responses(request.RESPONSES)
                }
            }

    def build_swagger(self):
        paths = {}
        for request in self.requests:
            paths["/" + request.URI] = self._build_swagger_methods(request)

        return paths, self._models

    @cachedproperty
    def swagger_file(self):
        with open(os.path.join(BASE_FOLDER, "swagger.json"),
                  "r") as swagger_json:
            swagger = json.load(swagger_json)

        match = re.match(r"(?P<base_path>.*{}).*".format(self.base_uri),
                         self.request.get_full_path())
        swagger["servers"] = [
            {
                "url": match.group("base_path"),
                "description": "Main server"
            }
        ]
        paths, schemas = self.build_swagger()
        swagger["paths"] = paths
        swagger["components"] = {
            "schemas": schemas
        }

        return swagger
