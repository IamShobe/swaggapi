from __future__ import absolute_import
import sys


if sys.version_info[0] > 2:
    string_type = str

else:
    string_type = basestring

PRIMITIVES = (int, string_type)

def is_primitive(thing):
    return isinstance(thing, PRIMITIVES)


class CustomType(object):
    pass


class SpecialType(CustomType):
    def __init__(self, base_type):
        self.base_type = base_type


class Enum(SpecialType):
    def __init__(self, options):
        super(Enum, self).__init__(str)
        self.options = options

    def __repr__(self):
        return "<type Enum - {!r}>".format(self.options)

    def decode(self, value):
        return value


class Map(SpecialType):
    def __init__(self, key_type, value_type):
        super(Map, self).__init__(dict)
        self.key_type = key_type
        self.value_type = value_type

    def __repr__(self):
        return "<type Map({!r}, {!r})>".format(self.key_type, self.value_type)

    def decode(self, dict):
        to_ret = {}
        for key, value in dict.items():
            actual_key = key
            if not is_primitive(actual_key):
               actual_key = self.key_type.decode(key)

            actual_value = value
            if not is_primitive(actual_value):
                actual_value = self.value_type.decode(value)

            to_ret[actual_key] = actual_value

        return to_ret

class List(SpecialType):
    def __init__(self, type):
        super(List, self).__init__(list)
        self.type = type

    def decode(self, list):
        if issubclass(self.type, PRIMITIVES):
            return list

        return [self.type.decode(item) for item in list]

    def __repr__(self):
        return "<type [{!r}]>".format(self.type)


class MultiTypeList(SpecialType):
    def __init__(self, allowed_types):
        super(MultiTypeList, self).__init__(list)
        self.allowed_types = allowed_types

    def __repr__(self):
        types_repr = ["{!r}".format(_type) for _type in  self.allowed_types]
        types =  " | ".join(types_repr)
        return "<type [{}]>".format(types)

    def decode(self, value):
        to_ret = []
        for item in value:
            for type in self.allowed_types:
                try:
                    to_ret.append(type.decode(item))
                    break
                except:
                    pass

        return to_ret


class OneOf(CustomType):
    def __init__(self, types):
        self.types = types

    def __repr__(self):
        types_repr = ["{!r}".format(_type) for _type in self.types]
        types = " | ".join(types_repr)
        return "<type {}>".format(types)

    def decode(self, value):
        for type in self.types:
            try:
                return type.decode(value)

            except Exception as e:
                pass
        raise RuntimeError("couldn't parse {!r} of type, {!r}".format(value,
                                                                      self))


class DynamicType(CustomType):
    def __init__(self, type_as_str):
        self.type = type_as_str

    def __repr__(self):
        return "DynamicType({!r})".format(self.type)

    def eval(self):
        import swaggapi.api.openapi.models as models
        klass = getattr(models, self.type)

        return klass

    def decode(self, value):
        return self.eval().decode(value)
