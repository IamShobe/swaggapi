from __future__ import absolute_import

import inspect
from numbers import Number

from six import string_types

from swaggapi.api.builder.utils import get_schema
from swaggapi.api.openapi.models import Schema, Example
from swaggapi.api.builder.common.model import AbstractAPIModel

class DynamicType(object):
    def __init__(self, class_name, module):
        self.class_name = class_name
        self.module = module

    def eval(self):
        models = __import__(self.module, fromlist=[self.class_name])
        klass = getattr(models, self.class_name)

        return klass


class Field(object):
    def __init__(self, name, type, description="", required=False,
                 example=None, location="body", deprecated=False):
        self.name = name
        self.required = required
        self._type = type
        self.description = description
        self._example = example
        self.location = location
        self.deprecated = deprecated

    @property
    def example(self):
        return self.default_example() \
            if self._example is None else self._example

    @property
    def type(self):
        if isinstance(self._type, DynamicType):
            self._type = self._type.eval()

        return self._type

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


class ArrayField(Field):
    def __init__(self, name, items_type, *args, **kwargs):
        self._items_type = items_type

        super(ArrayField, self).__init__(name, "array", *args, **kwargs)

    @property
    def items_type(self):
        if isinstance(self._items_type, DynamicType):
            self._items_type = self._items_type.eval()

        return self._items_type

    def default_example(self):
        if inspect.isclass(self.items_type):
            if issubclass(self.items_type, AbstractAPIModel):
                return [self.items_type.EXAMPLE]

            elif issubclass(self.items_type, string_types):
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
        self._model = model

        super(ModelField, self).__init__(name, "object", *args, **kwargs)

    @property
    def model(self):
        if isinstance(self._model, DynamicType):
            self._model = self._model.eval()

        return self._model

    def default_example(self):
        if self.model.EXAMPLE is not None:
            return self.model.EXAMPLE

        example = {}
        for property in self.model.PROPERTIES:
            example[property.name] = property.example

        return example

    def ref_name(self):
        return self.model.ref_name()

    def schemas(self, schema_bank, index):
        return self.model.schemas(schema_bank, index)
