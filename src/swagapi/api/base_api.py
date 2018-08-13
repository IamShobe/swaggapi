import httplib
import inspect
import json
import os
from numbers import Number

import requests
from attrdict import AttrDict

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
    def __init__(self, name, type, description="", required=False,
                 example=None, location="body", deprecated=False):
        self.name = name
        self.required = required
        self.type = type
        self.description = description
        self.example = self.default_example() if example is None else example
        self.location = location
        self.deprecated = deprecated

    def default_example(self):
        return

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

    def __init__(self, obj):
        self.validate(obj)
        self.obj = obj
        self.attr_dict = AttrDict(self.obj)

    def __getattr__(self, item):
        return getattr(self.attr_dict, item)

    @classmethod
    def get_required_props(cls):
        return [prop for prop in cls.PROPERTIES if prop.required]

    @classmethod
    def validate(cls, obj):
        if not isinstance(obj, dict):
            raise ValueError("Object must be of type dict! given {}".format(
                obj))

        keys = obj.keys()
        if len(keys) < len(cls.PROPERTIES):
            raise ValueError("Invalid number of properties")

        for field in cls.get_required_props():
            if field.name not in keys:
                raise RuntimeError("Missing required field {}".format(
                    field.name))

            if not isfit(obj[field.name], field):
                raise RuntimeError("Object doesn't fit the field: {!r} "
                                   "doesn't fit {!r} in {!r}".format(
                    obj[field.name], field, field.name))

        return True

    def __str__(self):
        return str(self.PROPERTIES)

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

    def default_example(self):
        if inspect.isclass(self.items_type):
            if issubclass(self.items_type, AbstractAPIModel):
                return [self.items_type.EXAMPLE]

            elif issubclass(self.items_type, basestring):
                return ["example", "example2"]

            elif issubclass(self.items_type, Number):
                return [0, 0]

        elif isinstance(self.items_type, Field):
            return [self.items_type.default_example()]

    def validate(self, obj):
        if not isinstance(obj, list):
            return False

        for item in obj:
            if not isinstance(item, self.items_type):
                return False

        return True

    def schemas(self, schema_bank, index):
        super_schema = super(ArrayField, self).schemas(schema_bank, index)
        super_schema.items = self.items_type.schemas(schema_bank, index)
        return super_schema


class StringField(Field):
    def __init__(self, name, *args, **kwargs):
        super(StringField, self).__init__(name, "string", *args, **kwargs)

    def default_example(self):
        return "example"


class BoolField(Field):
    def __init__(self, name, *args, **kwargs):
        super(BoolField, self).__init__(name, "boolean", *args, **kwargs)

    def default_example(self):
        return False

class NumberField(Field):
    def __init__(self, name, *args, **kwargs):
        super(NumberField, self).__init__(name, "integer", *args, **kwargs)

    def default_example(self):
        return 0


class ModelField(Field):
    def __init__(self, name, model, *args, **kwargs):
        self.model = model
        super(ModelField, self).__init__(name, "object", *args, **kwargs)

    def default_example(self):
        return self.model.EXAMPLE

    def ref_name(self):
        return self.model.ref_name()

    def schemas(self, schema_bank, index):
        return self.model.schemas(schema_bank, index)

class Requester(object):
    def __init__(self, host, port, logger, base_url):
        self.base_url = os.path.join("http://{}:{}/".format(host, port),
                                     base_url, BASE_API)
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


def isfit(obj, class_name):
    if isinstance(class_name, StringField):
        return isinstance(obj, basestring)

    elif isinstance(class_name, BoolField):
        return isinstance(obj, bool)

    elif isinstance(class_name, NumberField):
        return isinstance(obj, Number)

    elif isinstance(class_name, ModelField):
        return class_name.model.validate(obj)

    elif isinstance(class_name, ArrayField):
        if not isinstance(obj, list):
            return False

        for item in obj:
            if not isfit(item, class_name.items_type):
                return False

        return True

    elif issubclass(class_name, AbstractAPIModel):
        return class_name.validate(obj)

    else:
        return isinstance(obj, class_name)
