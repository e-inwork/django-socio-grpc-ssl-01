from typing import Dict, List

from django_socio_grpc.decorators import grpc_action
from django_socio_grpc.grpc_actions.actions import GRPCActionMixin
from django_socio_grpc.grpc_actions.placeholders import AttrPlaceholder


class ListIdsMixin(GRPCActionMixin, abstract=True):
    @grpc_action(request=[], response=[{"name": "ids", "type": "repeated int32"}])
    async def ListIds(self, request, context):
        pass


class ListNameMixin(GRPCActionMixin, abstract=True):
    _list_name_response: List[Dict[str, str]]

    @grpc_action(request=[], response=AttrPlaceholder("_list_name_response"))
    async def ListName(self, request, context):
        pass