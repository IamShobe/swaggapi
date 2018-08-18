from __future__ import absolute_import

from django.db.migrations.operations.base import Operation

from .abstract_model import (StaticOpenAPIObject,
                             OpenAPIField,
                             PatternedOpenAPIObject,
                             OpenAPIPattern,
                             PatternedStaticOpenAPIObject)
from .types import (Map,
                    List,
                    MultiTypeList,
                    Enum,
                    OneOf,
                    DynamicType)


class ExternalDocumentation(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="description", type=str,
                     description="A short description of the target "
                                 "documentation. CommonMark syntax MAY be "
                                 "used for rich text representation."),
        OpenAPIField(name="url", type=str, required=True,
                     description="The URL for the target "
                                 "documentation. Value MUST be in the format"
                                 " of a URL.")
    ]


class Tag(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="name", type=str, required=True,
                     description="The name of the tag."),
        OpenAPIField(name="description", type=str,
                     description="A short description for the tag. "
                                 "CommonMark syntax MAY be used for rich "
                                 "text representation."),
        OpenAPIField(name="externalDocs", type=ExternalDocumentation,
                     description="Additional external documentation for this "
                                 "tag.")
    ]


class License(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="name", type=str, required=True,
                     description="The license name used for the API."),
        OpenAPIField(name="url", type=str,
                     description="A URL to the license used for the API."
                                 " MUST be in the format of a URL.")
    ]


class Contact(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="name", type=str,
                     description="The identifying name of the contact "
                                 "person/organization."),
        OpenAPIField(name="url", type=str,
                     description="The URL pointing to the contact "
                                 "information. "
                                 "MUST be in the format of a URL."),
        OpenAPIField(name="email", type=str,
                     description="The email address of the contact "
                                 "person/organization."
                                 " MUST be in the format of an email "
                                 "address.")
    ]


class Info(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="title", type=str, required=True,
                     description="The title of the application."),
        OpenAPIField(name="description", type=str,
                     description="A short description of the "
                                 "application. CommonMark syntax MAY be "
                                 "used for rich text representation."),
        OpenAPIField(name="termsOfService", type=str,
                     description="A URL to the Terms of Service for "
                                 "the API. "
                                 "MUST be in the format of a URL."),
        OpenAPIField(name="contact", type=Contact,
                     description="The contact information for the "
                                 "exposed API."),
        OpenAPIField(name="license", type=License,
                     description="The license information for the "
                                 "exposed API."),
        OpenAPIField(name="version", type=str, required=True,
                     description="The version of the OpenAPI document "
                                 "(which is distinct from the OpenAPI "
                                 "Specification version or the API "
                                 "implementation version).")
    ]


class ServerVariable(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="enum", type=List(str),
                     description="An enumeration of string values to "
                                 "be used if the substitution options "
                                 "are from a limited set."),
        OpenAPIField(name="default", type=str, required=True,
                     description="The default value to use for "
                                 "substitution, and to send, if an "
                                 "alternate value is not supplied. "
                                 "Unlike the Schema Object's default, "
                                 "this value MUST be provided by the "
                                 "consumer."),
        OpenAPIField(name="description", type=str,
                     description="An optional description for "
                                 "the server variable. CommonMark "
                                 "syntax MAY be used for rich text "
                                 "representation.")
    ]


class Server(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="url", type=str, required=True,
                     description=" A URL to the target host. "
                                 "This URL supports Server Variables "
                                 "and MAY be relative, to indicate "
                                 "that the host location is relative "
                                 "to the location where the OpenAPI "
                                 "document is being served. Variable "
                                 "substitutions will be made when a "
                                 "variable is named in {brackets}."),
        OpenAPIField(name="description", type=str,
                     description="An optional string describing the "
                                 "host designated by the URL. "
                                 "CommonMark syntax MAY be used for "
                                 "rich text representation."),
        OpenAPIField(name="variables", type=Map(str, ServerVariable),
                     description="A map between a variable name and "
                                 "its value. The value is used for "
                                 "substitution in the server's "
                                 "URL template.")
    ]


class Referance(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="$ref", type=str, required=True,
                     description="The reference string.")
    ]
    def __init__(self, reference, type, **kwargs):
        self.reference = reference
        self.type = type
        super(Referance, self).__init__(**kwargs)


class Discriminator(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="propertyName", type=str, required=True,
                     description="The name of the property in the payload "
                                 "that will hold the discriminator value."),
        OpenAPIField(name="mapping", type=Map(str, str),
                     description="An object to hold mappings between payload "
                                 "values and schema names or references.")
    ]


class XML(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="name", type=str,
                     description="Replaces the name of the element/attribute "
                                 "used for the described schema property. "
                                 "When defined within items, it will affect "
                                 "the name of the individual XML elements "
                                 "within the list. When defined alongside "
                                 "type being array (outside the items), "
                                 "it will affect the wrapping element and "
                                 "only if wrapped is true. If wrapped is "
                                 "false, it will be ignored."),
        OpenAPIField(name="namespace", type=str,
                     description="The URI of the namespace definition. Value "
                                 "MUST be in the form of an absolute URI."),
        OpenAPIField(name="prefix", type=str,
                     description="The prefix to be used for the name."),
        OpenAPIField(name="attribute", type=bool, default=False,
                     description="Declares whether the property definition "
                                 "translates to an attribute instead of an "
                                 "element. Default value is false."),
        OpenAPIField(name="wrapped", type=bool,
                     description="MAY be used only for an array definition. "
                                 "Signifies whether the array is wrapped ("
                                 "for example, "
                                 "<books><book/><book/></books>) or "
                                 "unwrapped (<book/><book/>). Default value "
                                 "is false. The definition takes effect only "
                                 "when defined alongside type being array ("
                                 "outside the items).")
    ]


class Example(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="summary", type=str,
                     description="Short description for the example."),
        OpenAPIField(name="description", type=str,
                     description="Long description for the example. "
                                 "CommonMark syntax MAY be used for rich "
                                 "text representation."),
        OpenAPIField(name="value", type=object,
                     description="Embedded literal example. The value field "
                                 "and externalValue field are mutually "
                                 "exclusive. To represent examples of media "
                                 "types that cannot naturally represented in "
                                 "JSON or YAML, use a string value to "
                                 "contain the example, escaping where "
                                 "necessary."),
        OpenAPIField(name="externalValue", type=str,
                     description="A URL that points to the literal example. "
                                 "This provides the capability to reference "
                                 "examples that cannot easily be included in "
                                 "JSON or YAML documents. The value field "
                                 "and externalValue field are mutually "
                                 "exclusive.")
    ]


class Schema(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="title", type=str,
                     description="Used to "
                                 "decorate a user interface with information "
                                 "about the data produced by this user "
                                 "interface. A title will preferably be "
                                 "short."),
        OpenAPIField(name="multipleOf", type=int,
                     description='The value of "multipleOf" MUST be a '
                                 'number, strictly greater than 0.'
                                 "A numeric instance is valid only if "
                                 "division by this keyword's value results "
                                 "in an integer."),
        OpenAPIField(name="maximum", type=int),
        OpenAPIField(name="exclusiveMaximum", type=int),
        OpenAPIField(name="minimum", type=int),
        OpenAPIField(name="exclusiveMinimum", type=int),
        OpenAPIField(name="maxLength", type=int,
                     description="A string instance is valid against this "
                                 "keyword if its length is less than, "
                                 "or equal to, the value of this keyword."),
        OpenAPIField(name="minLength", type=int,
                     description="A string instance is valid against this "
                                 "keyword if its length is less than, "
                                 "or equal to, the value of this keyword."),
        OpenAPIField(name="pattern", type=str,
                     description="The value of this keyword MUST be a "
                                 "string. This string SHOULD be a valid "
                                 "regular expression, according to the ECMA "
                                 "262 regular expression dialect."
                                 "A string instance is considered valid if "
                                 "the regular expression matches the "
                                 "instance successfully. Recall: regular "
                                 "expressions are not implicitly anchored."),
        OpenAPIField(name="maxItems", type=int,
                     description='An array instance is valid against '
                                 '"maxItems" if its size is less than, '
                                 'or equal to, the value of this keyword.'),
        OpenAPIField(name="minItems", type=int, default=0,
                     description='An array instance is valid against '
                                 '"minItems" if its size is greater than, '
                                 'or equal to, the value of this keyword.'),
        OpenAPIField(name="uniqueItems", type=bool, default=False,
                     description='If this keyword has boolean value false, '
                                 'the instance validates successfully. If it '
                                 'has boolean value true, the instance '
                                 'validates successfully if all of its '
                                 'elements are unique.'),
        OpenAPIField(name="maxProperties", type=int,
                     description='An object instance is valid against '
                                 '"maxProperties" if its number of '
                                 'properties is less than, or equal to, '
                                 'the value of this keyword.'),
        OpenAPIField(name="minProperties", type=int, default=0,
                     description='An object instance is valid against '
                                 '"minProperties" if its number of '
                                 'properties is greater than, or equal to, '
                                 'the value of this keyword.'),
        OpenAPIField(name="required", type=List(str), default=[],
                     description="The value of this keyword MUST be an "
                                 "array. Elements of this array, if any, "
                                 "MUST be strings, and MUST be unique."
                                 "An object instance is valid against this "
                                 "keyword if every item in the array is the "
                                 "name of a property in the instance."),
        OpenAPIField(name="enum", type=List(object),
                     description="The value of this keyword MUST be an "
                                 "array. This array SHOULD have at least one "
                                 "element. Elements in the array SHOULD be "
                                 "unique. An instance validates successfully "
                                 "against this keyword if its value is equal "
                                 "to one of the elements in this keyword's "
                                 "array value."),
        OpenAPIField(name="type", type=str,
                     description="Value MUST be a string. Multiple types via "
                                 "an array are not supported."),
        OpenAPIField(name="allOf", type=OneOf((Referance,
                                               DynamicType("Schema"))),
                     description="An instance validates successfully against "
                                 "this keyword if it validates successfully "
                                 "against all schemas defined by this "
                                 "keyword's value."),
        OpenAPIField(name="oneOf", type=OneOf((Referance,
                                               DynamicType("Schema"))),
                     description="An instance validates successfully against "
                                 "this keyword if it validates successfully "
                                 "against exactly one schema defined by this "
                                 "keyword's value."),
        OpenAPIField(name="anyOf", type=OneOf((Referance,
                                               DynamicType("Schema"))),
                     description="An instance validates successfully against "
                                 "this keyword if it validates successfully "
                                 "against at least one schema defined by "
                                 "this keyword's value."),
        OpenAPIField(name="not", type=OneOf((Referance,
                                             DynamicType("Schema"))),
                     description="An instance is valid against this keyword "
                                 "if it fails to validate successfully "
                                 "against the schema defined by this "
                                 "keyword."),
        OpenAPIField(name="items", type=OneOf((Referance,
                                               DynamicType("Schema"))),
                     description="Value MUST be an object and not an array. "
                                 "items MUST be present if the type is array."
                                 "validation succeeds if all elements in the "
                                 "array successfully validate against that "
                                 "schema."),
        OpenAPIField(name="properties",
                     type=Map(str, OneOf((Referance, DynamicType("Schema")))),
                     description="This keyword determines how child "
                                 "instances validate for objects, and does "
                                 "not directly validate the immediate "
                                 "instance itself."
                                 "Validation succeeds if, for each name that "
                                 "appears in both the instance and as a name "
                                 "within this keyword's value, the child "
                                 "instance for that name successfully "
                                 "validates against the corresponding "
                                 "schema."),
        OpenAPIField(name="description", type=str,
                     description="CommonMark syntax MAY be used for rich "
                                 "text representation"),
        OpenAPIField(name="format", type=Enum(["int32", "int64", "float",
                                               "double", "byte", "binary",
                                               "data", "date-time",
                                               "password"]),
                     description="JSON Schema format"),
        OpenAPIField(name="default", type=object,
                     description='The default value represents what would be '
                                 'assumed by the consumer of the input as '
                                 'the value of the schema if one is not '
                                 'provided. Unlike JSON Schema, the value '
                                 'MUST conform to the defined type for the '
                                 'Schema Object defined at the same level. '
                                 'For example, if type is string, '
                                 'then default can be "foo" but cannot be 1.'),
        OpenAPIField(name="nullable", type=bool, default=False,
                     description="Allows sending a null value for the "
                                 "defined schema. Default value is false."),
        OpenAPIField(name="discriminator", type=Discriminator,
                     description="Adds support for polymorphism. The "
                                 "discriminator is an object name that is "
                                 "used to differentiate between other "
                                 "schemas which may satisfy the payload "
                                 "description."),
        OpenAPIField(name="readOnly", type=bool, default=False,
                     description='Relevant only for Schema "properties" '
                                 'definitions. Declares the property as '
                                 '"read only". This means that it MAY be '
                                 'sent as part of a response but SHOULD NOT '
                                 'be sent as part of the request. If the '
                                 'property is marked as readOnly being true '
                                 'and is in the required list, the required '
                                 'will take effect on the response only. A '
                                 'property MUST NOT be marked as both '
                                 'readOnly and writeOnly being true. Default '
                                 'value is false.'),
        OpenAPIField(name="writeOnly", type=bool, default=False,
                     description='Relevant only for Schema "properties" '
                                 'definitions. Declares the property as '
                                 '"write only". Therefore, it MAY be sent as '
                                 'part of a request but SHOULD NOT be sent '
                                 'as part of the response. If the property '
                                 'is marked as writeOnly being true and is '
                                 'in the required list, the required will '
                                 'take effect on the request only. A '
                                 'property MUST NOT be marked as both '
                                 'readOnly and writeOnly being true. Default '
                                 'value is false.'),
        OpenAPIField(name="xml", type=XML,
                     description="This MAY be used only on properties "
                                 "schemas. It has no effect on root schemas. "
                                 "Adds additional metadata to describe the "
                                 "XML representation of this property."),
        OpenAPIField(name="externalDocs", type=ExternalDocumentation,
                     description="Additional external documentation for this "
                                 "schema."),
        OpenAPIField(name="example", type=OneOf([Example, object]),
                     description="A free-form property to include an example "
                                 "of an instance for this schema. To "
                                 "represent examples that cannot be "
                                 "naturally represented in JSON or YAML, "
                                 "a string value can be used to contain the "
                                 "example with escaping where necessary."),
        OpenAPIField(name="deprecated", type=bool, default=False,
                     description="Specifies that a schema is deprecated and "
                                 "SHOULD be transitioned out of usage. "
                                 "Default value is false.")
    ]


class Encoding(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="contentType", type=str,
                     description="The Content-Type for encoding a specific "
                                 "property."),
        OpenAPIField(name="headers", type=Map(str,
                                              OneOf([Referance,
                                                     DynamicType("Header")])
                                              ),
                     description="A map allowing additional information to "
                                 "be provided as headers, for example "
                                 "Content-Disposition. Content-Type is "
                                 "described separately and SHALL be ignored "
                                 "in this section. This property SHALL be "
                                 "ignored if the request body media type is "
                                 "not a multipart."),
        OpenAPIField(name="style", type=str,
                     description="Describes how a specific property value "
                                 "will be serialized depending on its type. "
                                 "See Parameter Object for details on the "
                                 "style property. The behavior follows the "
                                 "same values as query parameters, including "
                                 "default values. This property SHALL be "
                                 "ignored if the request body media type is "
                                 "not application/x-www-form-urlencoded."),
        OpenAPIField(name="explode", type=bool,
                     description="When this is true, property values of type "
                                 "array or object generate separate "
                                 "parameters for each value of the array, "
                                 "or key-value-pair of the map. For other "
                                 "types of properties this property has no "
                                 "effect. When style is form, the default "
                                 "value is true. For all other styles, "
                                 "the default value is false. This property "
                                 "SHALL be ignored if the request body media "
                                 "type is not "
                                 "application/x-www-form-urlencoded."),
        OpenAPIField(name="allowReserved", type=bool,
                     description="Determines whether the parameter value "
                                 "SHOULD allow reserved characters, "
                                 "as defined by RFC3986 :/?#[]@!$&'()*+,"
                                 ";= to be included without "
                                 "percent-encoding. The default value is "
                                 "false. This property SHALL be ignored if "
                                 "the request body media type is not "
                                 "application/x-www-form-urlencoded.")
    ]


class Media(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="schema", type=OneOf([Schema, Referance]),
                     description="The schema defining the type used for the "
                                 "request body."),
        OpenAPIField(name="example", type=OneOf([Example, object]),
                     description="Example of the media type. The example "
                                 "object SHOULD be in the correct format as "
                                 "specified by the media type. The example "
                                 "field is mutually exclusive of the "
                                 "examples field. Furthermore, "
                                 "if referencing a schema which contains an "
                                 "example, the example value SHALL override "
                                 "the example provided by the schema."),
        OpenAPIField(name="examples", type=Map(str,
                                               OneOf([Example, Referance])),
                     description="Examples of the media type. Each example "
                                 "object SHOULD match the media type and "
                                 "specified schema if present. The examples "
                                 "field is mutually exclusive of the example "
                                 "field. Furthermore, if referencing a "
                                 "schema which contains an example, "
                                 "the examples value SHALL override the "
                                 "example provided by the schema."),
        OpenAPIField(name="encoding", type=Map(str, Encoding),
                     description="A map between a property name and its "
                                 "encoding information. The key, being the "
                                 "property name, MUST exist in the schema as "
                                 "a property. The encoding object SHALL only "
                                 "apply to requestBody objects when the "
                                 "media type is multipart or "
                                 "application/x-www-form-urlencoded.")
    ]



class RequestBody(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="description", type=str,
                     description="	A brief description of the request body. "
                                 "This could contain examples of use. "
                                 "CommonMark syntax MAY be used for rich "
                                 "text representation."),
        OpenAPIField(name="content", type=Map(str, Media), required=True,
                     description="The content of the request body. "
                                 "The key is a media type or media type "
                                 "range and the value describes it. For "
                                 "requests that match multiple keys, "
                                 "only the most specific key is applicable. "
                                 "e.g. text/plain overrides text/*"),
        OpenAPIField(name="required", type=bool, default=False,
                     description="Determines if the request body is required "
                                 "in the request. Defaults to false.")
    ]


class Parameter(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="name", type=str, required=True,
                     description='The name of the parameter. Parameter names '
                                 'are case sensitive.\n'
                                 'If in is "path", the name field MUST '
                                 'correspond to the associated path segment '
                                 'from the path field in the Paths Object. '
                                 'See Path Templating for further '
                                 'information.\n'
                                 'If in is "header" and the name field is '
                                 '"Accept", "Content-Type" or '
                                 '"Authorization", the parameter definition '
                                 'SHALL be ignored.\n'
                                 'For all other cases, the name corresponds '
                                 'to the parameter name used by the in '
                                 'property.'),
        OpenAPIField(name="in",
                     type=Enum(["query", "header", "path", "cookie"]),
                     required=True,
                     description='The location of the parameter. Possible '
                                 'values are "query", "header", "path" or '
                                 '"cookie".'),
        OpenAPIField(name="description", type=str,
                     description="	A brief description of the parameter. "
                                 "This could contain examples of use. "
                                 "CommonMark syntax MAY be used for rich "
                                 "text representation."),
        OpenAPIField(name="required", type=bool, default=False,
                     description='Determines whether this parameter is '
                                 'mandatory. If the parameter location is '
                                 '"path", this property is REQUIRED and its '
                                 'value MUST be true. Otherwise, '
                                 'the property MAY be included and its '
                                 'default value is false.'),
        OpenAPIField(name="deprecated", type=bool, default=False,
                     description="Specifies that a parameter is deprecated "
                                 "and SHOULD be transitioned out of usage."),
        OpenAPIField(name="allowEmptyValue", type=bool, default=False,
                     description="Sets the ability to pass empty-valued "
                                 "parameters. This is valid only for query "
                                 "parameters and allows sending a parameter "
                                 "with an empty value. Default value is "
                                 "false. If style is used, and if behavior "
                                 "is n/a (cannot be serialized), the value "
                                 "of allowEmptyValue SHALL be ignored."),
        OpenAPIField(name="schema", type=MultiTypeList([Schema, Referance]),
                     description="The schema defining the type used for the "
                                 "parameter."),
        OpenAPIField(name="example", type=OneOf([Example, object]),
                     description="A free-form property to include an example "
                                 "of an instance for this schema. To "
                                 "represent examples that cannot be "
                                 "naturally represented in JSON or YAML, "
                                 "a string value can be used to contain the "
                                 "example with escaping where necessary."),
        OpenAPIField(name="examples", type=Map(str,
                                               OneOf([Example, Referance])),
                     description="Examples of the media type. Each example "
                                 "SHOULD contain a value in the correct "
                                 "format as specified in the parameter "
                                 "encoding. The examples field is mutually "
                                 "exclusive of the example field. "
                                 "Furthermore, if referencing a schema which "
                                 "contains an example, the examples value "
                                 "SHALL override the example provided by the "
                                 "schema."),
        OpenAPIField(name="content", type=Map(str, Media),
                     description="A map containing the representations for "
                                 "the parameter. The key is the media type "
                                 "and the value describes it. The map MUST "
                                 "only contain one entry.")
    ]


class Header(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="description", type=str,
                     description="	A brief description of the parameter. "
                                 "This could contain examples of use. "
                                 "CommonMark syntax MAY be used for rich "
                                 "text representation."),
        OpenAPIField(name="required", type=bool, default=False,
                     description='Determines whether this parameter is '
                                 'mandatory. If the parameter location is '
                                 '"path", this property is REQUIRED and its '
                                 'value MUST be true. Otherwise, '
                                 'the property MAY be included and its '
                                 'default value is false.'),
        OpenAPIField(name="deprecated", type=bool, default=False,
                     description="Specifies that a parameter is deprecated "
                                 "and SHOULD be transitioned out of usage."),
        OpenAPIField(name="allowEmptyValue", type=bool, default=False,
                     description="Sets the ability to pass empty-valued "
                                 "parameters. This is valid only for query "
                                 "parameters and allows sending a parameter "
                                 "with an empty value. Default value is "
                                 "false. If style is used, and if behavior "
                                 "is n/a (cannot be serialized), the value "
                                 "of allowEmptyValue SHALL be ignored."),
        OpenAPIField(name="schema", type=MultiTypeList([Schema, Referance]),
                     description="The schema defining the type used for the "
                                 "parameter."),
        OpenAPIField(name="example", type=OneOf([Example, object]),
                     description="A free-form property to include an example "
                                 "of an instance for this schema. To "
                                 "represent examples that cannot be "
                                 "naturally represented in JSON or YAML, "
                                 "a string value can be used to contain the "
                                 "example with escaping where necessary."),
        OpenAPIField(name="examples", type=Map(str,
                                               OneOf([Example, Referance])),
                     description="Examples of the media type. Each example "
                                 "SHOULD contain a value in the correct "
                                 "format as specified in the parameter "
                                 "encoding. The examples field is mutually "
                                 "exclusive of the example field. "
                                 "Furthermore, if referencing a schema which "
                                 "contains an example, the examples value "
                                 "SHALL override the example provided by the "
                                 "schema."),
        OpenAPIField(name="content", type=Map(str, Media),
                     description="A map containing the representations for "
                                 "the parameter. The key is the media type "
                                 "and the value describes it. The map MUST "
                                 "only contain one entry.")
    ]


class Link(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="operationRef", type=str,
                     description="A relative or absolute reference to an OAS "
                                 "operation. This field is mutually "
                                 "exclusive of the operationId field, "
                                 "and MUST point to an Operation Object. "
                                 "Relative operationRef values MAY be used "
                                 "to locate an existing Operation Object in "
                                 "the OpenAPI definition."),
        OpenAPIField(name="operationId", type=str,
                     description="The name of an existing, resolvable OAS "
                                 "operation, as defined with a unique "
                                 "operationId. This field is mutually "
                                 "exclusive of the operationRef field."),
        OpenAPIField(name="parameters", type=Map(str, object),
                     description="A map representing parameters to pass to "
                                 "an operation as specified with operationId "
                                 "or identified via operationRef. The key is "
                                 "the parameter name to be used, whereas the "
                                 "value can be a constant or an expression "
                                 "to be evaluated and passed to the linked "
                                 "operation. The parameter name can be "
                                 "qualified using the parameter location [{"
                                 "in}.]{name} for operations that use the "
                                 "same parameter name in different locations "
                                 "(e.g. path.id)."),
        OpenAPIField(name="requestBody", type=OneOf([RequestBody, Referance]),
                     description="A literal value or to use as a request "
                                 "body when calling the target operation."),
        OpenAPIField(name="description", type=str,
                     description="	A description of the link. CommonMark "
                                 "syntax MAY be used for rich text "
                                 "representation."),
        OpenAPIField(name="server", type=Server,
                     description="A server object to be used by the target "
                                 "operation.")
    ]


class Response(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="description", type=str, required=True,
                     description="A short description of the response. "
                                 "CommonMark syntax MAY be used for rich "
                                 "text representation."),
        OpenAPIField(name="headers", type=Map(str,
                                              OneOf([Referance,
                                                     DynamicType("Header")])
                                              ),
                     description="Maps a header name to its definition. "
                                 "RFC7230 states header names are case "
                                 "insensitive. If a response header is "
                                 "defined with the name 'Content-Type', "
                                 "it SHALL be ignored."),
        OpenAPIField(name="content", type=Map(str, Media),
                     description="A map containing descriptions of potential "
                                 "response payloads. The key is a media type "
                                 "or media type range and the value "
                                 "describes it. For responses that match "
                                 "multiple keys, only the most specific key "
                                 "is applicable. e.g. text/plain overrides "
                                 "text/*"),
        OpenAPIField(name="links", type=Map(str, OneOf([Referance,
                                                        Link])),
                     description="A map of operations links that can be "
                                 "followed from the response. The key of the "
                                 "map is a short name for the link, "
                                 "following the naming constraints of the "
                                 "names for Component Objects.")
    ]


class Responses(PatternedStaticOpenAPIObject):
    patterns = [
        OpenAPIPattern(pattern=r"\d{3}", type=OneOf([Response, Referance]),
                       description="Any HTTP status code can be used as the "
                                   "property name, but only one property per "
                                   "code, to describe the expected response "
                                   "for that HTTP status code. A Reference "
                                   "Object can link to a response that is "
                                   "defined in the OpenAPI Object's "
                                   "components/responses section. This field "
                                   "MUST be enclosed in quotation marks (for "
                                   "example, '200') for compatibility "
                                   "between JSON and YAML. To define a range "
                                   "of response codes, this field MAY "
                                   "contain the uppercase wildcard character "
                                   "X. For example, 2XX represents all "
                                   "response codes between [200-299]. The "
                                   "following range definitions are allowed: "
                                   "1XX, 2XX, 3XX, 4XX, and 5XX. If a "
                                   "response range is defined using an "
                                   "explicit code, the explicit code "
                                   "definition takes precedence over the "
                                   "range definition for that code.")
    ]
    fields = [
        OpenAPIField(name="default", type=OneOf([Response, Referance]),
                     description="The documentation of responses other than "
                                 "the ones declared for specific HTTP "
                                 "response codes. Use this field to cover "
                                 "undeclared responses. A Reference Object "
                                 "can link to a response that the OpenAPI "
                                 "Object's components/responses section "
                                 "defines.")
    ]


class CallBack(PatternedOpenAPIObject):
    patterns = [
        OpenAPIPattern(pattern=r".*", type=DynamicType("Path"),
                       description="A Path Item Object used to define a "
                                   "callback request and expected responses. "
                                   "A complete example is available.")
    ]


class SecurityRequirement(PatternedOpenAPIObject):
    patterns = [
        OpenAPIPattern(pattern=r".*", type=List(str),
                       description='Each name MUST correspond to a security '
                                   'scheme which is declared in the Security '
                                   'Schemes under the Components Object. If '
                                   'the security scheme is of type "oauth2" '
                                   'or "openIdConnect", then the value is a '
                                   'list of scope names required for the '
                                   'execution. For other security scheme '
                                   'types, the array MUST be empty.')
    ]


class Operation(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="tags", type=List(str),
                     description="A list of tags for API documentation "
                                 "control. Tags can be used for logical "
                                 "grouping of operations by resources or any "
                                 "other qualifier."),
        OpenAPIField(name="summary", type=str,
                     description="A short summary of what the operation "
                                 "does."),
        OpenAPIField(name="description", type=str,
                     description="	A verbose explanation of the operation "
                                 "behavior. CommonMark syntax MAY be used "
                                 "for rich text representation."),
        OpenAPIField(name="externalDocs", type=ExternalDocumentation,
                     description="Additional external documentation for this "
                                 "operation."),
        OpenAPIField(name="operationId", type=str,
                     description="Unique string used to identify the "
                                 "operation. The id MUST be unique among all "
                                 "operations described in the API. Tools and "
                                 "libraries MAY use the operationId to "
                                 "uniquely identify an operation, therefore, "
                                 "it is RECOMMENDED to follow common "
                                 "programming naming conventions."),
        OpenAPIField(name="parameters",
                     type=MultiTypeList([Parameter, Referance]),
                     description="A list of parameters that are applicable "
                                 "for this operation. If a parameter is "
                                 "already defined at the Path Item, the new "
                                 "definition will override it but can never "
                                 "remove it. The list MUST NOT include "
                                 "duplicated parameters. A unique parameter "
                                 "is defined by a combination of a name and "
                                 "location. The list can use the Reference "
                                 "Object to link to parameters that are "
                                 "defined at the OpenAPI Object's "
                                 "components/parameters."),
        OpenAPIField(name="responses",
                     type=OneOf([Responses, Referance]),
                     description="REQUIRED. The list of possible responses "
                                 "as they are returned from executing this "
                                 "operation."),
        OpenAPIField(name="requestBody", type=OneOf([RequestBody, Operation]),
                     description="The request body applicable for this "
                                 "operation. The requestBody is only "
                                 "supported in HTTP methods where the HTTP "
                                 "1.1 specification RFC7231 has explicitly "
                                 "defined semantics for request bodies. In "
                                 "other cases where the HTTP spec is vague, "
                                 "requestBody SHALL be ignored by consumers."),
        OpenAPIField(name="callBacks", type=Map(str, OneOf([CallBack,
                                                            Referance])),
                     description="A map of possible out-of band callbacks "
                                 "related to the parent operation. The key "
                                 "is a unique identifier for the Callback "
                                 "Object. Each value in the map is a "
                                 "Callback Object that describes a request "
                                 "that may be initiated by the API provider "
                                 "and the expected responses. The key value "
                                 "used to identify the callback object is an "
                                 "expression, evaluated at runtime, "
                                 "that identifies a URL to use for the "
                                 "callback operation."),
        OpenAPIField(name="deprecated", type=bool, default=False,
                     description="Declares this operation to be deprecated. "
                                 "Consumers SHOULD refrain from usage of the "
                                 "declared operation. Default value is "
                                 "false."),
        OpenAPIField(name="security", type=SecurityRequirement,
                     description="A declaration of which security mechanisms "
                                 "can be used for this operation. The list "
                                 "of values includes alternative security "
                                 "requirement objects that can be used. Only "
                                 "one of the security requirement objects "
                                 "need to be satisfied to authorize a "
                                 "request. This definition overrides any "
                                 "declared top-level security. To remove a "
                                 "top-level security declaration, an empty "
                                 "array can be used."),
        OpenAPIField(name="servers", type=List(Server),
                     description="An alternative server array to service "
                                 "this operation. If an alternative server "
                                 "object is specified at the Path Item "
                                 "Object or Root level, it will be "
                                 "overridden by this value.")
    ]


class Path(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="$ref", type=str,
                     description="Allows for an external definition of this "
                                 "path item. The referenced structure MUST "
                                 "be in the format of a Path Item Object. If "
                                 "there are conflicts between the referenced "
                                 "definition and this Path Item's "
                                 "definition, the behavior is undefined."),
        OpenAPIField(name="summary", type=str,
                     description="An optional, string summary, intended to "
                                 "apply to all operations in this path."),
        OpenAPIField(name="description", type=str,
                     description="An optional, string description, intended "
                                 "to apply to all operations in this path. "
                                 "CommonMark syntax MAY be used for rich "
                                 "text representation."),
        OpenAPIField(name="get", type=Operation,
                     description="A definition of a GET operation on this "
                                 "path."),
        OpenAPIField(name="post", type=Operation,
                     description="A definition of a POST operation on this "
                                 "path."),
        OpenAPIField(name="put", type=Operation,
                     description="A definition of a PUT operation on this "
                                 "path."),
        OpenAPIField(name="delete", type=Operation,
                     description="A definition of a DELETE operation on this "
                                 "path."),
        OpenAPIField(name="options", type=Operation,
                     description="A definition of a OPTIONS operation on this "
                                 "path."),
        OpenAPIField(name="head", type=Operation,
                     description="A definition of a HEAD operation on this "
                                 "path."),
        OpenAPIField(name="patch", type=Operation,
                     description="A definition of a PATCH operation on this "
                                 "path."),
        OpenAPIField(name="trace", type=Operation,
                     description="A definition of a TRACE operation on this "
                                 "path."),
        OpenAPIField(name="servers", type=List(Server),
                     description="An alternative server array to service all "
                                 "operations in this path."),
        OpenAPIField(name="parameters",
                     type=MultiTypeList([Parameter, Referance]),
                     description="A list of parameters that are applicable "
                                 "for all the operations described under "
                                 "this path. These parameters can be "
                                 "overridden at the operation level, "
                                 "but cannot be removed there. The list MUST "
                                 "NOT include duplicated parameters. A "
                                 "unique parameter is defined by a "
                                 "combination of a name and location. The "
                                 "list can use the Reference Object to link "
                                 "to parameters that are defined at the "
                                 "OpenAPI Object's components/parameters."),
        OpenAPIField(name="schema", type=OneOf((Schema, Referance)),
                     description="The schema defining the type used for the "
                                 "parameter.")
    ]


class Paths(PatternedOpenAPIObject):
    patterns = [
        OpenAPIPattern(pattern=r"^/.*", type=Path,
                       description="A relative path to an individual "
                                   "endpoint. The field name MUST "
                                   " with a slash. The path is "
                                   "appended (no relative URL "
                                   "resolution) to the expanded "
                                   "URL from the Server Object's "
                                   "url field in order to construct "
                                   "the full URL. Path templating is "
                                   "allowed. When matching URLs, "
                                   "concrete (non-templated) paths "
                                   "would be matched before their "
                                   "templated counterparts. "
                                   "Templated paths with the same "
                                   "hierarchy but different templated "
                                   "names MUST NOT exist as they are "
                                   "identical. In case of ambiguous "
                                   "matching, it's up to the tooling "
                                   "to decide which one to use.")
    ]


class OAuthFlow(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="authorizationUrl", type=str, required=True,
                     description="The authorization URL to be used for this "
                                 "flow. This MUST be in the form of a URL."),
        OpenAPIField(name="tokenUrl", type=str, required=True,
                     description="The token URL to be used for this flow. "
                                 "This MUST be in the form of a URL."),
        OpenAPIField(name="refreshUrl", type=str,
                     description="The URL to be used for obtaining refresh "
                                 "tokens. This MUST be in the form of a URL."),
        OpenAPIField(name="scopes", type=Map(str, str), required=True,
                     description="The available scopes for the OAuth2 "
                                 "security scheme. A map between the scope "
                                 "name and a short description for it.")
    ]


class OAuthFlows(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="implicit", type=OAuthFlow,
                     description="Configuration for the OAuth Implicit flow"),
        OpenAPIField(name="password", type=OAuthFlow,
                     description="Configuration for the OAuth Resource Owner "
                                 "Password flow"),
        OpenAPIField(name="clientCredentials", type=OAuthFlow,
                     description="Configuration for the OAuth Client "
                                 "Credentials flow. Previously called "
                                 "application in OpenAPI 2.0."),
        OpenAPIField(name="authorizationCode", type=OAuthFlow,
                     description="Configuration for the OAuth Authorization "
                                 "Code flow. Previously called accessCode in "
                                 "OpenAPI 2.0.")
    ]


class SecurityScheme(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="type", required=True,
                     type=Enum(["apiKey", "http", "oauth2", "openIdConnect"]),
                     description='The type of the security scheme. Valid '
                                 'values are "apiKey", "http", "oauth2", '
                                 '"openIdConnect".'),
        OpenAPIField(name="description", type=str,
                     description="	A short description for security scheme. "
                                 "CommonMark syntax MAY be used for rich "
                                 "text representation."),
        OpenAPIField(name="name", type=str,
                     description="The name of the header, query or cookie "
                                 "parameter to be used."),
        OpenAPIField(name="in", type=Enum(["query", "header", "cookie"]),
                     description='The location of the API key. Valid values '
                                 'are "query", "header" or "cookie".'),
        OpenAPIField(name="scheme", type=str,
                     description="The name of the HTTP Authorization scheme "
                                 "to be used in the Authorization header as "
                                 "defined in RFC7235."),
        OpenAPIField(name="bearerFormat", type=str,
                     description="A hint to the client to identify how the "
                                 "bearer token is formatted. Bearer tokens "
                                 "are usually generated by an authorization "
                                 "server, so this information is primarily "
                                 "for documentation purposes."),
        OpenAPIField(name="flows", type=OAuthFlows, required=True,
                     description="An object containing configuration "
                                 "information for the flow types supported."),
        OpenAPIField(name="openIdConnectUrl", type=str, required=True,
                     description="OpenId Connect URL to discover OAuth2 "
                                 "configuration values. This MUST be in the "
                                 "form of a URL.")
    ]


class Componenets(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="schemas",
                     type=Map(str, OneOf([Schema, Referance])),
                     description="An object to hold reusable Schema Objects."),
        OpenAPIField(name="responses",
                     type=Map(str, OneOf([Response, Referance])),
                     description="An object to hold reusable Response "
                                 "Objects."),
        OpenAPIField(name="parameters",
                     type=Map(str, OneOf([Parameter, Referance])),
                     description="An object to hold reusable Parameter "
                                 "Objects."),
        OpenAPIField(name="examples",
                     type=Map(str, OneOf([Example, Referance])),
                     description="An object to hold reusable Example "
                                 "Objects."),
        OpenAPIField(name="requestBodies",
                     type=Map(str, OneOf([RequestBody, Referance])),
                     description="An object to hold reusable Request Body "
                                 "Objects."),
        OpenAPIField(name="headers",
                     type=Map(str, OneOf([Header, Referance])),
                     description="An object to hold reusable Header Objects."),
        OpenAPIField(name="securitySchemes",
                     type=Map(str, OneOf([SecurityScheme, Referance])),
                     description="An object to hold reusable Security Scheme "
                                 "Objects."),
        OpenAPIField(name="links",
                     type=Map(str, OneOf([Link, Referance])),
                     description="An object to hold reusable Link Objects."),
        OpenAPIField(name="callbacks",
                     type=Map(str, OneOf([CallBack, Referance])),
                     description="An object to hold reusable Callback "
                                 "Objects."),
    ]


class OpenAPI(StaticOpenAPIObject):
    fields = [
        OpenAPIField(name="openapi", type=str, required=True,
                     description="This string MUST be the semantic version "
                                 "number of the OpenAPI Specification "
                                 "version that the OpenAPI document uses. "
                                 "The openapi field SHOULD be used by "
                                 "tooling specifications and clients to "
                                 "interpret the OpenAPI document. This is "
                                 "not related to the API info.version "
                                 "string."),
        OpenAPIField(name="info", type=Info, required=True,
                     description="Provides metadata about the API. The "
                                 "metadata MAY be used by tooling as "
                                 "required."),
        OpenAPIField(name="servers", type=List(Server),
                     description="An array of Server Objects, which provide "
                                 "connectivity information to a target "
                                 "server. If the servers property is not "
                                 "provided, or is an empty array, "
                                 "the default value would be a Server Object "
                                 "with a url value of /."),
        OpenAPIField(name="paths", type=Paths, required=True,
                     description="The available paths and operations for the "
                                 "API."),
        OpenAPIField(name="components", type=Componenets,
                     description="An element to hold various schemas for the "
                                 "specification."),
        OpenAPIField(name="security", type=List(SecurityRequirement),
                     description="A declaration of which security mechanisms "
                                 "can be used across the API. The list of "
                                 "values includes alternative security "
                                 "requirement objects that can be used. Only "
                                 "one of the security requirement objects "
                                 "need to be satisfied to authorize a "
                                 "request. Individual operations can "
                                 "override this definition."),
        OpenAPIField(name="tags", type=List(Tag),
                     description="A list of tags used by the specification "
                                 "with additional metadata. The order of the "
                                 "tags can be used to reflect on their order "
                                 "by the parsing tools. Not all tags that "
                                 "are used by the Operation Object must be "
                                 "declared. The tags that are not declared "
                                 "MAY be organized randomly or based on the "
                                 "tools' logic. Each tag name in the list "
                                 "MUST be unique."),
        OpenAPIField(name="externalDocs", type=ExternalDocumentation,
                     description="Additional external documentation.")
    ]
