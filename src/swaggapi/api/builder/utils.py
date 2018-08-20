from __future__ import absolute_import

from numbers import Number

from six import string_types
from swaggapi.api.openapi.models import Referance


def get_dict_leafs(dict_a):
    if not isinstance(dict_a, dict):
        raise RuntimeError("parameter should be dict!")

    leafs = {}
    def _inner(a_dict, leafs_dict):
        for key, value in a_dict.items():
            if isinstance(value, dict):
                _inner(value, leafs_dict)

            else:
                leafs_dict[key] = value

    _inner(dict_a, leafs)

    return leafs

def get_schema(model, schema_bank, type, index=None):
    ref_name = model.ref_name()
    if index is not None:
        ref_name += str(index)

    if not ref_name in schema_bank[type]:
        handler = getattr(model, type)
        schema_bank[type][ref_name] = None  # place holder to prevent recursion
        schema = handler(schema_bank, index)
        schema_bank[type][ref_name] = schema

    return Referance(ref_name, type,
                     **{"$ref": "#/components/{}/{}".format(type, ref_name)})


def isfit(obj, class_name):
    from swaggapi.api.builder.common.model import AbstractAPIModel
    from swaggapi.api.builder.common.fields import (StringField,
                                                    BoolField,
                                                    NumberField,
                                                    ModelField, ArrayField)
    if isinstance(class_name, StringField):
        return isinstance(obj, string_types)

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
