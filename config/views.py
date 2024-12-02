from rest_framework.decorators import authentication_classes, action

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authorization.authentication import ExpiringTokenAuthentication

from constants.config import DATETIME_FORMAT
from record.serializers.output_serializer import ActionSerializer, CollectorSerializer, EnterpriseSerializer
from region.serializers.output_serializer import RegionSerializer

from utils.logger import logger
from utils.pagination import PaginationHandlerMixin, BasicPagination

from region.models import Region
from record.models import Collector, Action, Enterprise

@authentication_classes([ExpiringTokenAuthentication])
class ConfigViewSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    region_serializer_class = RegionSerializer
    action_serializer_class = ActionSerializer
    collector_serializer_class = CollectorSerializer
    enterprise_serializer_class = EnterpriseSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        regions = Region.objects.all()
        actions = Action.objects.all()
        enterprises = Enterprise.objects.all()

        logger.warning("Configurations loaded")
        return Response({
            "status": True,
            "message": "Configurations loaded",
            "detail": {
                "regions": self.region_serializer_class(regions, many=True).data,
                "actions": self.action_serializer_class(actions, many=True).data,
                "enterprises": self.enterprise_serializer_class(enterprises, many=True).data,
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], name='collector', url_name='collector', permission_classes=[IsAuthenticated])
    def collector(self, request):
        collectors = Collector.objects.all()

        query = request.GET.get("query", None)
        if query is not None:
            collectors = collectors.only("name").filter(name__icontains=query)
        
        page = self.paginate_queryset(collectors)
        if page is not None:
            serializer = self.get_paginated_response(self.collector_serializer_class(page, many=True).data)
        else:
            serializer = self.collector_serializer_class(collectors, many=True)

        logger.warning("Actions loaded")
        return Response({
            "status": True,
            "message": "Actions loaded",
            "detail": serializer.data,
        }, status=status.HTTP_200_OK)