from django.core.validators import MaxLengthValidator
from django.utils.translation import gettext as _
from google.protobuf.pyext._message import RepeatedCompositeContainer
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    LIST_SERIALIZER_KWARGS,
    BaseSerializer,
    Field,
    ListSerializer,
    ModelSerializer,
    Serializer,
)
from rest_framework.settings import api_settings
from rest_framework.utils.formatting import lazy_format

from django_socio_grpc.protobuf.json_format import message_to_dict, parse_dict

LIST_PROTO_SERIALIZER_KWARGS = (*LIST_SERIALIZER_KWARGS, "message_list_attr", "message")


class BaseProtoSerializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        message = kwargs.pop("message", None)
        self.stream = kwargs.pop("stream", None)
        self.message_list_attr = kwargs.pop("message_list_attr", None)
        if message is not None:
            self.initial_message = message
            kwargs["data"] = self.message_to_data(message)
        super().__init__(*args, **kwargs)

    def message_to_data(self, message):
        """Protobuf message -> Dict of python primitive datatypes."""
        return message_to_dict(message)

    def data_to_message(self, data):
        """Protobuf message <- Dict of python primitive datatypes."""
        assert hasattr(
            self, "Meta"
        ), 'Class {serializer_class} missing "Meta" attribute'.format(
            serializer_class=self.__class__.__name__
        )
        assert hasattr(
            self.Meta, "proto_class"
        ), 'Class {serializer_class} missing "Meta.proto_class" attribute'.format(
            serializer_class=self.__class__.__name__
        )
        return parse_dict(data, self.Meta.proto_class())

    @property
    def message(self):
        if not hasattr(self, "_message"):
            self._message = self.data_to_message(self.data)
        return self._message

    @classmethod
    def many_init(cls, *args, **kwargs):
        allow_empty = kwargs.pop("allow_empty", None)
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {"child": child_serializer}
        if allow_empty is not None:
            list_kwargs["allow_empty"] = allow_empty
        list_kwargs.update(
            {
                key: value
                for key, value in kwargs.items()
                if key in LIST_PROTO_SERIALIZER_KWARGS
            }
        )
        meta = getattr(cls, "Meta", None)
        list_serializer_class = getattr(meta, "list_serializer_class", ListProtoSerializer)
        return list_serializer_class(*args, **list_kwargs)


class ProtoSerializer(BaseProtoSerializer, Serializer):
    pass


class ListProtoSerializer(ListSerializer, BaseProtoSerializer):
    def message_to_data(self, message):
        """
        List of protobuf messages -> List of dicts of python primitive datatypes.
        """

        assert hasattr(
            self.child, "Meta"
        ), f'Class {self.__class__.__name__} missing "Meta" attribute'

        message_list_attr = getattr(self.child.Meta, "message_list_attr", None)
        if not message_list_attr and self.message_list_attr:
            message_list_attr = self.message_list_attr

        if message_list_attr is None:
            raise TypeError("message_list_attr is NoneType")

        repeated_message = getattr(message, message_list_attr, "")
        if not isinstance(repeated_message, RepeatedCompositeContainer):
            error_message = self.default_error_messages["not_a_list"].format(
                input_type=repeated_message.__class__.__name__
            )
            raise ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: [error_message]}, code="not_a_list"
            )
        ret = []
        for item in repeated_message:
            ret.append(self.child.message_to_data(item))
        return ret

    def data_to_message(self, data):
        """
        List of protobuf messages <- List of dicts of python primitive datatypes.
        """

        assert hasattr(
            self.child, "Meta"
        ), f'Class {self.__class__.__name__} missing "Meta" attribute'
        assert hasattr(
            self.child.Meta, "proto_class_list"
        ), f'Class {self.__class__.__name__} missing "Meta.proto_class_list" attribute'

        if getattr(self.child, "stream", False):
            return [self.child.data_to_message(item) for item in data]
        else:
            response = self.child.Meta.proto_class_list()
            response.results.extend([self.child.data_to_message(item) for item in data])
            return response


class ModelProtoSerializer(ProtoSerializer, ModelSerializer):
    pass


class BinaryField(Field):

    default_error_messages = {
        "max_length": _("Ensure this field has no more than {max_length} characters."),
    }

    def __init__(self, **kwargs):
        self.max_length = kwargs.pop("max_length", None)
        super().__init__(**kwargs)
        if self.max_length is not None:
            message = lazy_format(
                self.error_messages["max_length"], max_length=self.max_length
            )
            self.validators.append(MaxLengthValidator(self.max_length, message=message))

    def to_internal_value(self, data):
        # INFO - AM - 03/02/2022 - For now as we do not know what to do because we miss some use cas we just return the data and let the user to whatever he want
        # Some idea is to pass extra kwargs to convert string into bytes. We can use base64 or directly bytes(value)
        return data

    def to_representation(self, value):
        # INFO - AM - 03/02/2022 - For now as we do not know what to do because we miss some use cas we just return the value and let the user to whatever he want
        # Some idea is to pass extra kwargs to convert bytes into string. We can use base64 or unicode(value)
        return value
