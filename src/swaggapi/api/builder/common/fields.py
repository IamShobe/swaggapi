import inspect
from numbers import Number

from swaggapi.api.builder.utils import get_schema
from swaggapi.api.openapi.models import Schema, Example
from swaggapi.api.builder.common.model import AbstractAPIModel


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
