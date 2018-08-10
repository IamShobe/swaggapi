import httplib
import os

import requests
from .openapi.utils import get_schema

from .openapi.models import Schema, Response, Media, Example

BASE_API = "api/"


class AbstractRequest(object):
    URI = NotImplemented
    METHOD = NotImplemented
    TAGS = []
    PARAMS = []
    RESPONSES = {}
    VIEW = NotImplemented

    def __init__(self, data):
        self.data = data

    def execute(self, base_url, logger):
        url = os.path.join(base_url, self.URI)
        logger.debug("request: %s - %s - %s", url, self.METHOD, self.data)

        response = requests.request(self.METHOD, url, json=self.data)

        logger.debug("response: %s(%s) - %s",
                     httplib.responses[response.status_code],
                     response.status_code,
                     response.content)

        return response


class Field(object):
    def __init__(self, name, type, description="", required=True,
                 example=None, location="body", deprecated=False):
        self.name = name
        self.required = required
        self.type = type
        self.description = description
        self.example = example
        self.location = location
        self.deprecated = deprecated

    def ref_name(self):
        return self.name

    def examples(self, schema_bank, index):
        return Example(value=self.example)

    def schemas(self, schema_bank, index):
        example_ref = get_schema(self, schema_bank, "examples")
        example = schema_bank[example_ref.type][example_ref.reference]
        return Schema(title=self.name, type=self.type,
                      description=self.description,
                      example=example.value,
                      deprecated=self.deprecated)


class AbstractAPIModel(object):
    TITLE = None
    PROPERTIES = []
    EXAMPLE = None
    COMPONENT = "schemas"

    @classmethod
    def ref_name(cls):
        return cls.TITLE if cls.TITLE is not None else cls.__name__

    @classmethod
    def examples(cls, schema_bank, index):
        return Example(value=cls.EXAMPLE)

    @classmethod
    def schemas(cls, schema_bank, index):
        properties = {property.name:
                          get_schema(property, schema_bank, cls.COMPONENT)
                      for property in cls.PROPERTIES}
        required_fields = [field.name for field in cls.PROPERTIES
                           if field.required]
        if cls.EXAMPLE is None:
            example = None

        else:
            example_ref = get_schema(cls, schema_bank, "examples")
            example = \
                schema_bank[example_ref.type][example_ref.reference].value

        return Schema(title=cls.ref_name(),
                      type="object",
                      properties=properties,
                      description=cls.__doc__,
                      required=required_fields,
                      example=example)


class AbstractResponse(AbstractAPIModel):
    EXAMPLES = {}
    COMPONENT = "responses"

    @classmethod
    def examples(cls, schema_bank, index):
        return Example(value=cls.EXAMPLES[index])

    @classmethod
    def get_examples(cls, schema_bank):
        return {key: get_schema(cls, schema_bank, "examples", index=key)
                for key in cls.EXAMPLES.keys()}

    @classmethod
    def responses(cls, schema_bank, index):
        return Response(description=cls.__doc__,
                        content={
                            "application/json":
                                Media(schema=cls.schemas(schema_bank, index),
                                      examples=cls.get_examples(schema_bank))
                        })

    @classmethod
    def encode(cls, schema_bank):
        return get_schema(cls, schema_bank, "responses")


class NoContentResponse(AbstractResponse):
    pass


class ArrayField(Field):
    def __init__(self, name, items_type, *args, **kwargs):
        self.items_type = items_type
        super(ArrayField, self).__init__(name, "array", *args, **kwargs)

    def schemas(self, schema_bank, index):
        super_schema = super(ArrayField, self).schemas(schema_bank, index)
        super_schema.items = self.items_type.schemas(schema_bank, index)
        return super_schema


class StringField(Field):
    def __init__(self, name, *args, **kwargs):
        super(StringField, self).__init__(name, "string", *args, **kwargs)


class NumberField(Field):
    def __init__(self, name, *args, **kwargs):
        super(NumberField, self).__init__(name, "integer", *args, **kwargs)


class ModelField(Field):
    def __init__(self, name, model, *args, **kwargs):
        self.model = model
        super(ModelField, self).__init__(name, "object", *args, **kwargs)
        self.example = self.model.EXAMPLE

    def ref_name(self):
        return self.model.ref_name()

    def schemas(self, schema_bank, index):
        return self.model.schemas(schema_bank, index)

class Requester(object):
    def __init__(self, host, port, logger, base_url):
        self.base_url = os.path.join("http://{}:{}/".format(host, port),
                                     base_url, BASE_API)
        self.logger = logger

    def request(self, request_type, data):
        request = request_type(data)
        return request.execute(self.base_url, self.logger)
