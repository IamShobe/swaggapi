from __future__ import absolute_import

from .types import (DynamicType,
                    OneOf,
                    MultiTypeList,
                    List,
                    Enum,
                    Map,
                    SpecialType)


def is_instance(value, class_name):
    if value is None:
        return True

    if isinstance(class_name, SpecialType):
        base_type = class_name.base_type
        if not isinstance(value, base_type):
            return False

        if isinstance(class_name, Enum):
            options = class_name.options
            return value in options

        elif isinstance(class_name, Map):
            key_type = class_name.key_type
            value_type = class_name.value_type
            for key, value in value.items():
                if not is_instance(key, key_type) or \
                        not is_instance(value, value_type):
                    return False

            return True

        elif isinstance(class_name, List):
            type = class_name.type

            for item in value:
                if not isinstance(item, type):
                    return False

            return True

        elif isinstance(class_name, MultiTypeList):
            for item in value:
                if not is_instance(item, tuple(class_name.allowed_types)):
                    return False

            return True

    elif isinstance(class_name, OneOf):
        return is_instance(value, tuple(class_name.types))

    elif isinstance(class_name, DynamicType):
        type = class_name.eval()
        return is_instance(value, type)

    else:
        from .abstract_model import PatternedOpenAPIObject

        if isinstance(class_name, tuple):
            new_class_name = []

            for klass in class_name:
                if is_instance(klass, DynamicType):
                    new_class_name.append(klass.eval())

                else:
                    new_class_name.append(klass)

            class_name = tuple(new_class_name)

            if any(is_instance(value, klass) for klass in class_name):
                return True

        elif issubclass(class_name, PatternedOpenAPIObject):
            return class_name.is_matched(value)

        return isinstance(value, class_name)
