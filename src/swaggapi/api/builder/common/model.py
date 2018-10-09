from __future__ import absolute_import

from attrdict import AttrDict
from swaggapi.api.openapi.models import Example, Schema
from swaggapi.api.builder.utils import get_schema, isfit
import six


NAME2TYPE = {
    "str": str,
    "string": six.text_type,
    "basestring": six.text_type,
    "unicode": six.text_type,
    "bool": bool,
    "boolean": bool,
    "int": int,
    "integer": int,
    "number": int
}


class AbstractAPIModel(object):
    TITLE = None
    PROPERTIES = []
    EXAMPLE = None
    COMPONENT = "schemas"

    class TempField(object):
        def __init__(self, field, instance):
            self.instance = instance
            self.field = field

        def __getattr__(self, item):
            related_field = self.field.model.get_properties_dict()[item]
            if item in self.instance.attr_dict:
                to_ret = getattr(self.instance.attr_dict, item)
                if isinstance(to_ret, tuple):
                    to_ret = to_ret[0]
                return NAME2TYPE[related_field.type](to_ret)

            return self.instance.TempField(related_field, self)

    def __init__(self, obj):
        self.validate(obj)
        self.obj = obj
        self.attr_dict = AttrDict(self.obj)

    @classmethod
    def get_properties_dict(cls):
        return {field.name: field for field in cls.PROPERTIES}

    @property
    def params(self):
        return {key: value for key, value in self.obj.items()
                if key in self.params_properties}

    @property
    def body(self):
        return {key: value for key, value in self.obj.items()
                if key in self.body_properties}

    @property
    def params_properties(self):
        return [field.name
                for field in self.PROPERTIES if field.location != "body"]

    @property
    def body_properties(self):
        return [field.name
                for field in self.PROPERTIES if field.location == "body"]

    def __getattr__(self, item):
        if item in self.body_properties:
            return getattr(self.attr_dict, item)

        related_field = self.get_properties_dict()[item]
        if item in self.attr_dict:
            to_ret = getattr(self.attr_dict, item)
            if isinstance(to_ret, tuple):
                to_ret = to_ret[0]
            return NAME2TYPE[related_field.type](to_ret)

        return self.TempField(related_field, self)

    @classmethod
    def get_required_props(cls):
        return [prop for prop in cls.PROPERTIES if prop.required and
                prop.location == "body"]

    @classmethod
    def validate(cls, obj):
        if not isinstance(obj, dict):
            raise ValueError("Object must be of type dict! given {}".format(
                obj))

        keys = list(obj.keys())
        if len(keys) < len(cls.get_required_props()):
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
            example = {}
            for property in cls.PROPERTIES:
                example[property.name] = property.example

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