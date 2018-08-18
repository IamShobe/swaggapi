from __future__ import absolute_import

from swaggapi.api.builder.utils import get_schema
from swaggapi.api.builder.common.model import AbstractAPIModel
from swaggapi.api.openapi.models import Example, Response, Media


class AbstractResponse(AbstractAPIModel):
    EXAMPLES = {}

    @classmethod
    def examples(cls, schema_bank, index):
        return Example(value=cls.EXAMPLES[index])

    @classmethod
    def get_examples(cls, schema_bank):
        return {key: get_schema(cls, schema_bank, "examples", index=key)
                for key in cls.EXAMPLES.keys()}

    @classmethod
    def responses(cls, schema_bank, index):
        return Response(description=cls.__doc__,
                        content={
                            "application/json":
                                Media(schema=cls.schemas(schema_bank, index),
                                      examples=cls.get_examples(schema_bank))
                        })

    @classmethod
    def encode(cls, schema_bank):
        return get_schema(cls, schema_bank, "responses")


class NoContentResponse(AbstractResponse):
    pass
