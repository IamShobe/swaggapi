from __future__ import absolute_import

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


class Map(SpecialType):
    def __init__(self, key_type, value_type):
        super(Map, self).__init__(dict)
        self.key_type = key_type
        self.value_type = value_type

    def __repr__(self):
        return "<type Map({!r}, {!r})>".format(self.key_type, self.value_type)


class List(SpecialType):
    def __init__(self, type):
        super(List, self).__init__(list)
        self.type = type

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

class OneOf(CustomType):
    def __init__(self, types):
        self.types = types

    def __repr__(self):
        types_repr = ["{!r}".format(_type) for _type in self.types]
        types = " | ".join(types_repr)
        return "<type {}>".format(types)


class DynamicType(CustomType):
    def __init__(self, type_as_str):
        self.type = type_as_str

    def __repr__(self):
        return "DynamicType({!r})".format(self.type)

    def eval(self):
        import swaggapi.api.openapi.models as models
        klass = getattr(models, self.type)

        return klass
