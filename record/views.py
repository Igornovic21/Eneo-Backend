import pytz
from datetime import datetime
from django.utils.timezone import make_aware
from django.db.models import Count

from rest_framework.decorators import authentication_classes, action

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authorization.authentication import ExpiringTokenAuthentication

from constants.config import DATETIME_FORMAT
from record.serializers.output_serializer import RecordSerializer, ActionStatSerializer, EnterpriseStatSerializer, CollectorStatSerializer

from utils.logger import logger
from utils.pagination import PaginationHandlerMixin, BasicPagination

from region.models import Region
from record.models import Record

@authentication_classes([ExpiringTokenAuthentication])
class RecordViewSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = RecordSerializer
    action_stat_serializer_class = ActionStatSerializer
    enterprise_stat_serializer_class = EnterpriseStatSerializer
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

        action_stats = records.values("action__name").annotate(total=Count("action"))
        enterprise_stats = records.values("enterprise__name").annotate(total=Count("enterprise"))
        serializer_action_stats = self.action_stat_serializer_class(action_stats, many=True)
        serializer_enterprise_stats = self.enterprise_stat_serializer_class(enterprise_stats, many=True)
        logger.warning("Records stats loaded")
        return Response({
            "status": True,
            "message": "Records stats loaded",
            "statistics": {
                "action": serializer_action_stats.data,
                "enterprise": serializer_enterprise_stats.data,
            },
            "detail": serializer.data
        }, status=status.HTTP_200_OK)


@authentication_classes([ExpiringTokenAuthentication])
class RecordFilterSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    serializer_class = RecordSerializer
    action_stat_serializer_class = ActionStatSerializer
    enterprise_stat_serializer_class = EnterpriseStatSerializer
    collector_stat_serializer_class = CollectorStatSerializer
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

        # if action is None and collector is None and enterprise is None and min_date is None and max_date is None:
        #     logger.error("Provide at least one filter params (params, collector, enterprise, start_date, end_date)")
        #     return Response({
        #         "status": False,
        #         "message": "Provide at least one filter params (params, collector, enterprise, start_date, end_date)",
        #     }, status=status.HTTP_400_BAD_REQUEST)

        records = Record.objects.only("itinary").filter(itinary__region=region)
        
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

        action_stats = records.values("action__name").annotate(total=Count("action"))
        enterprise_stats = records.values("enterprise__name").annotate(total=Count("enterprise"))
        serializer_action_stats = self.action_stat_serializer_class(action_stats, many=True)
        serializer_enterprise_stats = self.enterprise_stat_serializer_class(enterprise_stats, many=True)

        active_records = records.only("data").filter(data__contains='"pl/info_pl/status": "actif"')

        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(records, many=True)
        logger.warning("Filtered records stats loaded")
        return Response({
            "status": True,
            "message": "Filtered records stats loaded",
            "percentage": round(len(active_records) / len(records), 2) * 100,
            "statistics": {
                "action": serializer_action_stats.data,
                "enterprise": serializer_enterprise_stats.data,
            },
            "detail": serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], name='compare', url_name='compare', permission_classes=[IsAuthenticated])
    def compare(self, request):
        min_date = request.GET.get("min_date", None)
        max_date = request.GET.get("max_date", None)

        region = request.GET.get("region-id", None)

        if min_date is None or max_date is None:
            logger.error("Provide min_date and max_date required params")
            return Response({
                "status": False,
                "message": "Provide min_date and max_date required params",
            }, status=status.HTTP_400_BAD_REQUEST)

        records = Record.objects.all()
        
        if region is not None:
            records = records.only("itinary").filter(itinary__region=region)
        
        
        min_date = datetime.strptime(min_date, DATETIME_FORMAT)
        max_date = datetime.strptime(max_date, DATETIME_FORMAT)
        min_records = records.only("date").filter(date__gt=make_aware(min_date, timezone=pytz.UTC))
        max_records = records.only("date").filter(date__gt=make_aware(max_date, timezone=pytz.UTC))
            
        min_action_stats = min_records.values("action__name").annotate(total=Count("action")).exclude(action__name=None)
        min_enterprise_stats = min_records.values("enterprise__name").annotate(total=Count("enterprise")).exclude(enterprise__name=None)
        max_action_stats = max_records.values("action__name").annotate(total=Count("action")).exclude(action__name=None)
        max_enterprise_stats = max_records.values("enterprise__name").annotate(total=Count("enterprise")).exclude(enterprise__name=None)
        
        serializer_min_action_stats = self.action_stat_serializer_class(min_action_stats, many=True)
        serializer_min_enterprise_stats = self.enterprise_stat_serializer_class(min_enterprise_stats, many=True)
        serializer_max_action_stats = self.action_stat_serializer_class(max_action_stats, many=True)
        serializer_max_enterprise_stats = self.enterprise_stat_serializer_class(max_enterprise_stats, many=True)

        logger.warning("Comparaison stats loaded")
        return Response({
            "status": True,
            "message": "Comparaison stats loaded",
            "detail": {
                "min_date": {
                    "action": serializer_min_action_stats.data,
                    "enterprise": serializer_min_enterprise_stats.data,
                },
                "max_date": {
                    "action": serializer_max_action_stats.data,
                    "enterprise": serializer_max_enterprise_stats.data,
                }
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], name='ranking', url_name='ranking', permission_classes=[IsAuthenticated])
    def ranking(self, request):
        region = request.GET.get("region-id", None)
        itinary = request.GET.get("itinary-id", None)

        records = Record.objects.all()
        
        if region is not None:
            records = records.only("itinary").filter(itinary__region=region)
        elif itinary is not None:
            records = records.only("itinary").filter(itinary=itinary)
        
        action_stats = records.values("action__name").annotate(total=Count("action")).exclude(action__name=None).order_by("-total")[:4]
        enterprise_stats = records.values("enterprise__name").annotate(total=Count("enterprise")).exclude(enterprise__name=None).order_by("-total")[:4]
        collector_stats = records.values("collector__name").annotate(total=Count("collector")).exclude(collector__name=None).order_by("-total")[:4]
        
        serializer_action_stats = self.action_stat_serializer_class(action_stats, many=True)
        serializer_enterprise_stats = self.enterprise_stat_serializer_class(enterprise_stats, many=True)
        serializer_collector_stats = self.collector_stat_serializer_class(collector_stats, many=True)

        logger.warning("Ranking stats loaded")
        return Response({
            "status": True,
            "message": "Ranking stats loaded",
            "detail": {
                "action": serializer_action_stats.data,
                "enterprise": serializer_enterprise_stats.data,
                "collector": serializer_collector_stats.data,
            }
        }, status=status.HTTP_200_OK)