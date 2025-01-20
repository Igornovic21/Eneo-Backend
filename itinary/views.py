import pytz
from datetime import datetime
from django.utils.timezone import make_aware
from django.db.models import Count
from django.contrib.gis.geos import Point

from rest_framework.decorators import authentication_classes, action

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authorization.authentication import ExpiringTokenAuthentication

from constants.config import DATETIME_FORMAT
from record.serializers.output_serializer import RecordSerializer
from statistic.serializers.output_serializer import ActionStatSerializer, EnterpriseStatSerializer
from itinary.serializers.output_serializer import ItinarySerializer

from region.constants import SRID
from utils.logger import logger
from utils.pagination import PaginationHandlerMixin, BasicPagination

from region.models import Region
from record.models import Record
from itinary.models import Itinary

@authentication_classes([ExpiringTokenAuthentication])
class ItinaryViewSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = RecordSerializer
    itinary_serializer = ItinarySerializer
    action_stat_serializer_class = ActionStatSerializer
    enterprise_stat_serializer_class = EnterpriseStatSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, block_code:str):
        try:
            return Itinary.objects.get(block_code=block_code)
        except Itinary.DoesNotExist:
            data = {
                "status": False,
                "message": "This itinary does not exist"
            }
            logger.warning("This itinary does not exist")
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

    def list(self, request):
        itinaries = Itinary.objects.only("itinary").filter(itinary__region__in=request.user.region.all()).order_by("name")
        
        query = request.GET.get("query", None)
        print(query)
        if query is not None:
            itinaries = itinaries.only("block_code").filter(block_code=query)

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

    def retrieve(self, request, pk=None):
        itinary = self.get_object(block_code=pk)
        if type(itinary) is Response : return itinary

        records = Record.objects.only('itinary').filter(itinary=itinary)
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(records, many=True)

        # action_stats = records.values("action__name").annotate(total=Count("action"))
        # enterprise_stats = records.values("enterprise__name").annotate(total=Count("enterprise"))
        # serializer_action_stats = self.action_stat_serializer_class(action_stats, many=True)
        # serializer_enterprise_stats = self.enterprise_stat_serializer_class(enterprise_stats, many=True)
        logger.warning("Itinary stats loaded")
        return Response({
            "status": True,
            "message": "Itinary stats loaded",
            # "statistics": {
            #     "action": serializer_action_stats.data,
            #     "enterprise": serializer_enterprise_stats.data,
            # },
            "detail": serializer.data
        }, status=status.HTTP_200_OK)


@authentication_classes([ExpiringTokenAuthentication])
class ItinaryFilterSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = RecordSerializer
    itinary_serializer = ItinarySerializer
    action_stat_serializer_class = ActionStatSerializer
    enterprise_stat_serializer_class = EnterpriseStatSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, block_code:str):
        try:
            return Itinary.objects.get(block_code=block_code)
        except Itinary.DoesNotExist:
            data = {
                "status": False,
                "message": "This itinary does not exist"
            }
            logger.warning("This itinary does not exist")
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

    def list(self, request):
        itinaries = Itinary.objects.only("region").filter(region__in=request.user.region.all()).order_by("name")
        
        query = request.GET.get("query", None)
        if query is not None:
            itinaries = itinaries.only("block_code").filter(block_code=query)

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

    def retrieve(self, request, pk=None):
        itinary = self.get_object(block_code=pk)
        if type(itinary) is Response : return itinary
        if itinary.region not in request.user.region.all():
            return Response({
                "status": False,
                "message": "This region is not assigned to this user"
            }, status=status.HTTP_403_FORBIDDEN)

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

        records = Record.objects.only("itinary").filter(itinary=itinary)
        
        if action is not None:
            records = records.only("action").filter(action__in=action.split(";"))
        if collector is not None:
            records = records.only("collector").filter(collector__in=collector.split(";"))
        if enterprise is not None:
            records = records.only("enterprise").filter(enterprise__in=enterprise.split(";"))
        if min_date is not None:
            date = datetime.strptime(min_date, DATETIME_FORMAT)
            records = records.only("date").filter(date__gt=make_aware(date, timezone=pytz.UTC))
        if max_date is not None:
            date = datetime.strptime(max_date, DATETIME_FORMAT)
            records = records.only("date").filter(date__lt=make_aware(date, timezone=pytz.UTC))

        # action_stats = records.values("action__name").annotate(total=Count("action"))
        # enterprise_stats = records.values("enterprise__name").annotate(total=Count("enterprise"))
        # serializer_action_stats = self.action_stat_serializer_class(action_stats, many=True)
        # serializer_enterprise_stats = self.enterprise_stat_serializer_class(enterprise_stats, many=True)

        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(records, many=True)
        logger.warning("Filtered itinary stats loaded")
        return Response({
            "status": True,
            "message": "Filtered itinary stats loaded",
            # "statistics": {
            #     "action": serializer_action_stats.data,
            #     "enterprise": serializer_enterprise_stats.data,
            # },
            "detail": serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], name='coords', url_name='coords', permission_classes=[IsAuthenticated])
    def coords(self, request):
        action = request.GET.get("action", None)
        collector = request.GET.get("collector", None)
        enterprise = request.GET.get("enterprise", None)
        min_date = request.GET.get("min_date", None)
        max_date = request.GET.get("max_date", None)
        longitude = request.GET.get("lng", None)
        latitude = request.GET.get("lat", None)
        
        if longitude is None or latitude is None:
            logger.error("Provide lng and lat required params")
            return Response({
                "status": False,
                "message": "Provide lng and lat required params",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        point = Point(float(latitude), float(longitude), srid=SRID)
        itinaries = Itinary.objects.only("boundary").filter(boundary__contains=point)
        
        if not itinaries.exists():
            logger.error("No itinary found for this point")
            return Response({
                "status": False,
                "message": "No itinary found for this point",
            }, status=status.HTTP_404_NOT_FOUND)
        
        itinary = itinaries[0]
        
        records = Record.objects.only("itinary").filter(itinary=itinary)
        
        if action is not None:
            records = records.only("action").filter(action__in=action.split(";"))
        if collector is not None:
            records = records.only("collector").filter(collector__in=collector.split(";"))
        if enterprise is not None:
            records = records.only("enterprise").filter(enterprise__in=enterprise.split(";"))
        if min_date is not None:
            date = datetime.strptime(min_date, DATETIME_FORMAT)
            records = records.only("date").filter(date__gt=make_aware(date, timezone=pytz.UTC))
        if max_date is not None:
            date = datetime.strptime(max_date, DATETIME_FORMAT)
            records = records.only("date").filter(date__lt=make_aware(date, timezone=pytz.UTC))

        # action_stats = records.values("action__name").annotate(total=Count("action"))
        # enterprise_stats = records.values("enterprise__name").annotate(total=Count("enterprise"))
        # serializer_action_stats = self.action_stat_serializer_class(action_stats, many=True)
        # serializer_enterprise_stats = self.enterprise_stat_serializer_class(enterprise_stats, many=True)

        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(records, many=True)

        logger.warning("Pl records stats loaded")
        return Response({
            "status": True,
            "message": "Pl records stats loaded",
            # "statistics": {
            #     "action": serializer_action_stats.data,
            #     "enterprise": serializer_enterprise_stats.data,
            # },
            "detail": serializer.data
        }, status=status.HTTP_200_OK)