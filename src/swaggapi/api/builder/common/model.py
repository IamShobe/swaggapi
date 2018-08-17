from attrdict import AttrDict
from swaggapi.api.openapi.models import Example, Schema
from swaggapi.api.builder.utils import get_schema, isfit


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