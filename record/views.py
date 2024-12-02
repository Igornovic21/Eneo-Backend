import pytz
from datetime import datetime
from django.utils.timezone import make_aware

from rest_framework.decorators import authentication_classes

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authorization.authentication import ExpiringTokenAuthentication

from constants.config import DATETIME_FORMAT
from record.serializers.output_serializer import RecordSerializer

from utils.logger import logger
from utils.pagination import PaginationHandlerMixin, BasicPagination

from region.models import Region
from record.models import Record

@authentication_classes([ExpiringTokenAuthentication])
class RecordViewSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = RecordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk:str):
        try:
            return Record.objects.get(pk=pk)
        except Record.DoesNotExist:
            data = {
                "status": False,
                "message": "This record does not exist"
            }
            logger.warning("This record does not exist")
            return Response(data, status=status.HTTP_404_NOT_FOUND)

    def get_region_object(self, pk:str):
        try:
            return Region.objects.get(pk=pk)
        except Region.DoesNotExist:
            data = {
                "status": False,
                "message": "This region does not exist"
            }
            logger.warning("This region does not exist")
            return Response(data, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        region = self.get_region_object(pk=pk)
        if type(region) is Response : return region

        records = Record.objects.only('itinary').filter(itinary__region=region)
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(records, many=True)
        logger.warning("Records stats loaded")
        return Response({
            "status": True,
            "message": "Records stats loaded",
            "detail": serializer.data
        }, status=status.HTTP_200_OK)


@authentication_classes([ExpiringTokenAuthentication])
class RecordFilterSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = RecordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk:str):
        try:
            return Record.objects.get(pk=pk)
        except Record.DoesNotExist:
            data = {
                "status": False,
                "message": "This region does not exist"
            }
            logger.warning("This region does not exist")
            return Response(data, status=status.HTTP_404_NOT_FOUND)

    def get_region_object(self, pk:str):
        try:
            return Region.objects.get(pk=pk)
        except Region.DoesNotExist:
            data = {
                "status": False,
                "message": "This region does not exist"
            }
            logger.warning("This region does not exist")
            return Response(data, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        region = self.get_region_object(pk=pk)
        if type(region) is Response : return region

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

        records = Record.objects.only("itinary").filter(itinary__region=region)
        
        if action is not None:
            records = records.only("action").filter(action__name=action)
        if collector is not None:
            records = records.only("collector").filter(collector__name=collector)
        if enterprise is not None:
            records = records.only("enterprise").filter(enterprise__name=enterprise)
        if min_date is not None:
            date = datetime.strptime(min_date, DATETIME_FORMAT)
            records = records.only("date").filter(date__gt=make_aware(date, timezone=pytz.UTC))
        if max_date is not None:
            date = datetime.strptime(max_date, DATETIME_FORMAT)
            records = records.only("date").filter(date__lt=make_aware(date, timezone=pytz.UTC))
            
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(records, many=True)
        logger.warning("Filtered records stats loaded")
        return Response({
            "status": True,
            "message": "Filtered records stats loaded",
            "detail": serializer.data
        }, status=status.HTTP_200_OK)