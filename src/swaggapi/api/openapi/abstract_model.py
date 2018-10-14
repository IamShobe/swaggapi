from __future__ import absolute_import

import re
import json
from textwrap import TextWrapper

from six import add_metaclass

from .utils import is_instance


class OpenAPIError(Exception):
    pass


class OpenAPIPattern(object):
    def __init__(self, pattern, type, description):
        self.pattern = pattern
        self.type = type
        self.description = description


class OpenAPIEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, OpenAPIObject):
            return {key: value for key, value in obj.kwargs.items()
                    if value is not None}
        
        return super(OpenAPIEncoder, self).default(obj)


class OpenAPIObject(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs if kwargs is not None else {}
        self.validate()

    def __getattr__(self, item):
        if item in self.kwargs:
            return self.kwargs[item]

        else:
            try:
                return getattr(self.__class__, item)

            except:
                raise OpenAPIError("No attribute: {}".format(item))

    def __repr__(self):
        return "<instance OpenApi - {}>".format(self.__class__.__name__)

    def __dir__(self):
        res = dir(type(self)) + list(self.__dict__.keys())
        return res + list(self.kwargs.keys())

    def json(self):
        return json.loads(json.dumps(self, cls=OpenAPIEncoder, indent=4))

    def validate(self):
        pass


class PatternedOpenAPIObject(OpenAPIObject):
    patterns = NotImplemented

    @property
    def pattern_fields(self):
        return self.kwargs

    @classmethod
    def is_matched(self, value):
        if not is_instance(value, dict):
            return False

        for arg, _value in value.items():
            found = None
            for pattern in self.patterns:
                match = re.match(pattern.pattern, arg)
                if match:
                    found = pattern
                    break

            if found is None:
                return False

            if not is_instance(_value, found.type):
                return False

        return True

    def validate_args_patterns(self):
        for arg, value in self.pattern_fields.items():
            found = None
            for pattern in self.patterns:
                match = re.match(pattern.pattern, arg)
                if match:
                    found = pattern
                    break

            if found is None:
                wrapper = TextWrapper(initial_indent="        ",
                                      subsequent_indent="        ")
                available_patterns = ["    Pattern: '{}'\n{}""".format(
                    pattern.pattern, wrapper.fill(pattern.description))
                for pattern in self.patterns]

                raise OpenAPIError("No pattern found for given arg: {}."
                                   "\nAvailable Patterns:\n{}".format(
                    arg, "\n".join(available_patterns)))

            if not is_instance(value, found.type):
                raise OpenAPIError("Value type invalid: {} expected {}".format(
                    type(value), found.type))

    def validate(self):
        self.validate_args_patterns()


class StaticOpenAPIMetaClass(type):
    @property
    def fields_dict(cls):
        return {field.name: field for field in cls.fields}

    def __dir__(self):
        return dir(type(self)) + list(self.__dict__.keys()) + \
               list(self.fields_dict.keys())

    @property
    def required_fields(cls):
        return [field for field in cls.fields if field.required]

    def __getattr__(self, item):
        if item in self.fields_dict:
            return self.fields_dict[item]

        raise OpenAPIError("No item {} in fields dict".format(item))


@add_metaclass(StaticOpenAPIMetaClass)
class StaticOpenAPIObject(OpenAPIObject):
    fields = NotImplemented

    def __init__(self, **kwargs):
        super(StaticOpenAPIObject, self).__init__(**kwargs)
        self.initiate_default_fields()
    
    def __setattr__(self, key, value):
        fields_dict = {field.name: field for field in self.fields}
        if key in list(fields_dict.keys()):
            if not is_instance(value, fields_dict[key].type):
                raise OpenAPIError(
                    "Invalid value given! Must be of type: {}".format(
                        fields_dict[key].type))

            self.kwargs[key] = value
            return

        super(StaticOpenAPIObject, self).__setattr__(key, value)

    @property
    def static_fields(self):
        return self.kwargs

    def initiate_default_fields(self):
        for field in self.fields:
            if field.name not in self.kwargs:
                self.kwargs[field.name] = None

    def validate_required(self):
        for field in self.fields:
            if field.required:
                if not field.name in self.kwargs:
                    raise OpenAPIError("Missing required field: {}".format(
                        field.name))

    def validate_type(self):
        for field, value in self.static_fields.items():
            static_field = self.fields_dict[field]
            if not is_instance(value, static_field.type):
                raise OpenAPIError("invalid type given! "
                                   "field: {!r}, got type {!r}".format(
                    static_field, value, static_field.type))

    def validate_no_extra(self):
        all_fields_names = list(self.fields_dict.keys())
        for field in self.static_fields.keys():
            if field not in all_fields_names:
                raise RuntimeError("{} object doesn't have {} field in its "
                                   "openapi structure!".format(
                    self.__class__.__name__, field))

    def validate(self):
        self.validate_required()
        self.validate_no_extra()
        self.validate_type()


class PatternedStaticOpenAPIObject(StaticOpenAPIObject,
                                   PatternedOpenAPIObject):
    @property
    def pattern_fields(self):
        pattern_keys = list(self.kwargs.keys())
        for field in self.fields:
            if field.name in pattern_keys:
                pattern_keys.remove(field.name)

        return {key: self.kwargs[key] for key in pattern_keys}

    @property
    def static_fields(self):
        pattern_keys = list(self.pattern_fields.keys())

        return {key: self.kwargs[key] for key in self.kwargs
                if key not in pattern_keys}

    def validate(self):
        self.validate_required()
        self.validate_no_extra()
        self.validate_args_patterns()
        self.validate_type()


class OpenAPIField(object):
    def __init__(self, name, type, default=None, required=False,
                 description=""):
        self.name = name
        self.type = type
        self.required = required
        self.description = description
        self.default = default

    def __repr__(self):
        return "OpenApiField({}, {}, required={})".format(
            self.name,
            self.type,
            self.required
        )

    def extract_from(self, object):
        return getattr(object, self.name)
