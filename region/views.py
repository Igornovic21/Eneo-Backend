import pytz
from datetime import datetime
from django.utils.timezone import make_aware

from rest_framework.decorators import authentication_classes, action
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authorization.authentication import ExpiringTokenAuthentication

from region.serializers.output_serializer import RegionStatSerializer
from itinary.serializers.output_serializer import ItinarySerializer

from constants.config import DATETIME_FORMAT
from utils.logger import logger
from utils.pagination import PaginationHandlerMixin, BasicPagination

from region.models import Region
from record.models import Record
from itinary.models import Itinary

@authentication_classes([ExpiringTokenAuthentication])
class RegionViewSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = RegionStatSerializer
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
        regions = request.user.region.all()
        for region in regions:
            records = Record.objects.only('itinary').filter(itinary__region=region)
            datas.append({
                "id": region.id,
                "name": region.name,
                "ona_name": region.ona_name,
                "records": len(records)
            })
            
        serializer = self.serializer_class(datas, many=True)
        logger.warning("Regions stats loaded")
        return Response({
            "status": True,
            "message": "Regions stats loaded",
            "detail": serializer.data
        }, status=status.HTTP_200_OK)

    
@authentication_classes([ExpiringTokenAuthentication])
class RegionFilterSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    itinary_serializer = ItinarySerializer
    serializer_class = RegionStatSerializer
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

        # if action is None and collector is None and enterprise is None and min_date is None and max_date is None:
        #     logger.error("Provide at least one filter params (params, collector, enterprise, start_date, end_date)")
        #     return Response({
        #         "status": False,
        #         "message": "Provide at least one filter params (params, collector, enterprise, start_date, end_date)",
        #     }, status=status.HTTP_400_BAD_REQUEST)

        datas = []
        regions = request.user.region.all()

        for region in regions:
            records = Record.objects.only("itinary").filter(itinary__region=region)
        
            if action is not None:
                records = records.only("action").filter(action__in=action.split(";"))
            if collector is not None:
                records = records.only("collector").filter(collector__in=collector.split(";"))
            if enterprise is not None:
                records = records.only("enterprise").filter(enterprise__in=enterprise.split(";"))
            if min_date is not None:
                date = datetime.strptime(min_date, DATETIME_FORMAT)
                records = records.only("date").filter(date__gt=make_aware(date, timezone=pytz.UTC)).only("itinary").filter(itinary__region=region)
            if max_date is not None:
                date = datetime.strptime(max_date, DATETIME_FORMAT)
                records = records.only("date").filter(date__lt=make_aware(date, timezone=pytz.UTC)).only("itinary").filter(itinary__region=region)

            datas.append({
                "id": region.id,
                "name": region.name,
                "records": len(records)
            })
            
        serializer = self.serializer_class(datas, many=True)
        logger.warning("Filtered regions stats loaded")
        return Response({
            "status": True,
            "message": "Filtered regions stats loaded",
            "detail": serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], name='itinary', url_name='itinary', permission_classes=[IsAuthenticated])
    def itinary(self, request, pk=None):
        region = self.get_object(pk=pk)
        if type(region) is Response : return region
        if region not in request.user.region.all():
            return Response({
                "status": False,
                "message": "This region is not assigned to this user"
            }, status=status.HTTP_403_FORBIDDEN)
        
        itinaries = Itinary.objects.only("region").filter(region=region).order_by("name")
        
        query = request.GET.get("query", None)
        if query is not None:
            itinaries = itinaries.only("name").filter(name__icontains=query)

        page = self.paginate_queryset(itinaries)
        if page is not None:
            serializer = self.get_paginated_response(self.itinary_serializer(page, many=True).data)
        else:
            serializer = self.itinary_serializer(itinaries, many=True)
        logger.warning("Itinary list loaded")
        return Response({
            "status": True,
            "message": "Itinary list loaded",
            "detail": serializer.data
        }, status=status.HTTP_200_OK)
