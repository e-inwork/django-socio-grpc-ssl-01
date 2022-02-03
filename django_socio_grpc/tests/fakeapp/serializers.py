from typing import Dict, List

from rest_framework import serializers

import fakeapp.grpc.fakeapp_pb2 as fakeapp_pb2
from django_socio_grpc import proto_serializers

from .models import (
    ForeignModel,
    ImportStructEvenInArrayModel,
    ManyManyModel,
    RelatedFieldModel,
    SpecialFieldsModel,
    UnitTestModel,
)


class ForeignModelRetrieveCustomProtoSerializer(proto_serializers.ProtoSerializer):

    name = serializers.CharField()
    custom = serializers.SerializerMethodField()

    def get_custom(self, obj) -> str:
        return f"{obj.uuid} - {obj.name}"

    class Meta:
        model = ForeignModel
        proto_class = fakeapp_pb2.ForeignModelRetrieveCustomResponse
        fields = ["uuid", "name"]


class ForeignModelSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = ForeignModel
        proto_class = fakeapp_pb2.ForeignModelResponse
        proto_class_list = fakeapp_pb2.ForeignModelListResponse
        fields = "__all__"


class UnitTestModelSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = UnitTestModel
        proto_class = fakeapp_pb2.UnitTestModelResponse
        proto_class_list = fakeapp_pb2.UnitTestModelListResponse
        fields = "__all__"


class UnitTestModelListExtraArgsSerializer(proto_serializers.ProtoSerializer):
    count = serializers.IntegerField()
    query_fetched_datetime = serializers.DateTimeField()
    results = UnitTestModelSerializer(many=True)

    class Meta:
        proto_class = fakeapp_pb2.UnitTestModelListExtraArgsResponse


class ManyManyModelSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = ManyManyModel
        proto_class = fakeapp_pb2.ManyManyModelResponse
        fields = "__all__"


class RelatedFieldModelSerializer(proto_serializers.ModelProtoSerializer):
    foreign_obj = ForeignModelSerializer(read_only=True)
    many_many_obj = ManyManyModelSerializer(read_only=True, many=True)

    slug_test_model = serializers.SlugRelatedField(slug_field="special_number", read_only=True)
    slug_reverse_test_model = serializers.SlugRelatedField(
        slug_field="is_active", read_only=True
    )

    custom_field_name = serializers.CharField()

    class Meta:
        model = RelatedFieldModel
        proto_class = fakeapp_pb2.RelatedFieldModelResponse
        proto_class_list = fakeapp_pb2.RelatedFieldModelListResponse
        message_list_attr = "list_custom_field_name"
        fields = "__all__"


class SpecialFieldsModelSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = SpecialFieldsModel
        proto_class = fakeapp_pb2.SpecialFieldsModelResponse
        proto_class_list = fakeapp_pb2.SpecialFieldsModelListResponse
        fields = "__all__"


class ImportStructEvenInArrayModelSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = ImportStructEvenInArrayModel
        proto_class = fakeapp_pb2.ImportStructEvenInArrayModelResponse
        fields = "__all__"


class CustomRetrieveResponseSpecialFieldsModelSerializer(
    proto_serializers.ModelProtoSerializer
):

    default_method_field = serializers.SerializerMethodField()

    custom_method_field = serializers.SerializerMethodField(method_name="custom_method")

    def get_default_method_field(self, obj) -> int:
        return 3

    def custom_method(self, obj) -> List[Dict]:
        return [{"test": "test"}]

    class Meta:
        model = SpecialFieldsModel
        proto_class = fakeapp_pb2.RelatedFieldModelResponse
        fields = ["uuid", "default_method_field", "custom_method_field"]


class BasicServiceSerializer(proto_serializers.ProtoSerializer):

    user_name = serializers.CharField()
    user_data = serializers.DictField()
    user_password = serializers.CharField(write_only=True)

    class Meta:
        proto_class = fakeapp_pb2.BasicServiceResponse
        proto_class_list = fakeapp_pb2.BasicGetMultipleListResponse
        fields = ["user_name", "user_data"]
