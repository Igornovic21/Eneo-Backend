import pytz
from datetime import datetime
from django.utils.timezone import make_aware

from rest_framework.decorators import action, authentication_classes
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authorization.authentication import ExpiringTokenAuthentication

from constants.config import DATETIME_FORMAT
from region.serializers.output_serializer import RegionSerializer

from utils.logger import logger
from utils.pagination import PaginationHandlerMixin, BasicPagination

from region.models import Region
from record.models import Record

@authentication_classes([ExpiringTokenAuthentication])
class RegionViewSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk:str):
        try:
            return Region.objects.get(pk=pk)
        except Region.DoesNotExist:
            data = {
                "status": False,
                "message": "This region does not exist"
            }
            logger.warning("This region does not exist")
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
    def list(self, request):
        datas = []
        regions = Region.objects.all()
        for region in regions:
            records = Record.objects.only('form').filter(form__region=region)
            datas.append({
                "id": region.id,
                "name": region.name,
                "records": len(records)
            })
            
        serializer = self.serializer_class(datas, many=True)
        logger.warning("Basic regions stats loaded")
        return Response({
            "status": True,
            "message": "Basic regions stats loaded",
            "detail": serializer.data
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        region = self.get_object(pk=pk)
        if type(region) is Response : return region

    
@authentication_classes([ExpiringTokenAuthentication])
class RegionFilterSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk:str):
        try:
            return Region.objects.get(pk=pk)
        except Region.DoesNotExist:
            data = {
                "status": False,
                "message": "This region does not exist"
            }
            logger.warning("This region does not exist")
            return Response(data, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        action = request.GET.get("action", None)
        collector = request.GET.get("collector", None)
        enterprise = request.GET.get("enterprise", None)
        min_date = request.GET.get("min_date", None)
        max_date = request.GET.get("max_date", None)

        if action is None and collector is None and enterprise is None and min_date is None and max_date is None:
            logger.error("Provide at least one filter params (params, collector, enterprise, start_date, end_date)")
            return Response({
                "status": False,
                "message": "Provide at least one filter params (params, collector, enterprise, start_date, end_date)",
            }, status=status.HTTP_400_BAD_REQUEST)

        datas = []
        regions = Region.objects.all()

        for region in regions:
            records = Record.objects.all()
            
            if action is not None:
                records = records.only("action").filter(action=action)
            if collector is not None:
                records = records.only("collector").filter(collector=collector)
            if enterprise is not None:
                records = records.only("enterprise").filter(enterprise=enterprise)
            if min_date is not None:
                date = datetime.strptime(min_date, DATETIME_FORMAT)
                records = records.only("date").filter(date__gt=make_aware(date, timezone=pytz.UTC))
            if max_date is not None:
                date = datetime.strptime(max_date, DATETIME_FORMAT)
                records = records.only("date").filter(date__lt=make_aware(date, timezone=pytz.UTC))

            datas.append({
                "id": region.id,
                "name": region.name,
                "records": len(records)
            })
            
        serializer = self.serializer_class(datas, many=True)
        logger.warning("Basic regions stats loaded")
        return Response({
            "status": True,
            "message": "Basic regions stats loaded",
            "detail": serializer.data
        }, status=status.HTTP_200_OK)
    
    # @action(detail=False, methods=['post'], name='action', url_name='action')
    # def action(self, request):
    #     print(request.headers.get("action"))
    #     print(request.headers.get("start_date"))
    #     datas = []
    #     regions = Region.objects.all()
    #     for region in regions:
    #         records = Record.objects.only('action').filter(action=region)
    #         datas.append({
    #             "id": region.id,
    #             "name": region.name,
    #             "records": len(records)
    #         })
            
    #     serializer = self.serializer_class(datas, many=True)
    #     logger.warning("Basic regions stats loaded")
    #     return Response({
    #         "status": True,
    #         "message": "Basic regions stats loaded",
    #         "detail": serializer.data
    #     }, status=status.HTTP_200_OK)