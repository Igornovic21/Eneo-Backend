import pytz
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Count

from rest_framework.decorators import authentication_classes, action

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authorization.authentication import ExpiringTokenAuthentication

from constants.config import DATETIME_FORMAT
from statistic.serializers.output_serializer import ActionStatSerializer, EnterpriseStatSerializer, CollectorStatSerializer

from utils.logger import logger
from utils.pagination import PaginationHandlerMixin

from region.models import Region
from record.models import Record, Action, DeliveryPoint
from itinary.models import Itinary

# Create your views here.
@authentication_classes([ExpiringTokenAuthentication])
class StatFilterSet(ViewSet, PaginationHandlerMixin):
    action_stat_serializer_class = ActionStatSerializer
    enterprise_stat_serializer_class = EnterpriseStatSerializer
    collector_stat_serializer_class = CollectorStatSerializer
    permission_classes = [IsAuthenticated]

    def get_itinary_object(self, block_code:str):
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
        records = Record.objects.only("itinary").filter(itinary__region__in=request.user.region.all())

        itinary = request.GET.get("itinary", None)
        agency = request.GET.get("agency", None)
        action = request.GET.get("action", None)
        collector = request.GET.get("collector", None)
        enterprise = request.GET.get("enterprise", None)
        min_date = request.GET.get("min_date", None)
        max_date = request.GET.get("max_date", None)
        
        if itinary is not None:
            records = records.only("itinary").filter(itinary__block_code=itinary)
        elif agency is not None:
            records = records.only("itinary").filter(itinary__agency=agency)
        if action is not None:
            records = records.only("action").filter(action__in=action.split(";"))
        if collector is not None:
            records = records.only("collector").filter(collector__in=collector.split(";"))
        if enterprise is not None:
            records = records.only("enterprise").filter(enterprise__in=enterprise.split(";"))
        if min_date is not None:
            date = datetime.strptime(min_date, DATETIME_FORMAT)
            records = records.only("date").filter(date__date__gte=make_aware(date, timezone=pytz.UTC))
        if max_date is not None:
            date = datetime.strptime(max_date, DATETIME_FORMAT)
            records = records.only("date").filter(date__date__lte=make_aware(date, timezone=pytz.UTC))

        total_pl = DeliveryPoint.objects.filter(record__in=records)

        action_stats = total_pl.values("record__action__name").annotate(total=Count("record__action"))
        enterprise_stats = total_pl.values("record__enterprise__name").annotate(total=Count("record__enterprise"))
        serializer_action_stats = self.action_stat_serializer_class(action_stats, many=True)
        serializer_enterprise_stats = self.enterprise_stat_serializer_class(enterprise_stats, many=True)
        active_pl = total_pl.only("status").filter(status="actif")
        inactive_pl = total_pl.only("status").filter(status="inactif")
        active_postpaid = total_pl.only("type").filter(type__icontains="po")
        active_prepaid = total_pl.only("type").filter(type__icontains="pr")
        active_public_lighting = total_pl.only("type").filter(type__icontains="eclairage")
        not_accessible_pl = total_pl.only("type").filter(type="")

        logger.warning("Filtered records stats loaded")
        return Response({
            "status": True,
            "message": "Filtered records stats loaded",
            "detail": {
                "inactive_delivery_points": inactive_pl.count(),
                "active_postpaid_points": active_postpaid.count(),
                "active_prepaid_points": active_prepaid.count(),
                "active_public_lighting_points": active_public_lighting.count(),
                "not_accessible_pl": not_accessible_pl.count(),
                "total": total_pl.count(),
                "percentage": 0 if records.count() == 0 else round(active_pl.count() / (total_pl.count() - not_accessible_pl.count()), 2) * 100,
                "statistics": {
                    "action": serializer_action_stats.data,
                    "enterprise": serializer_enterprise_stats.data,
                },
            }
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

        records = Record.objects.only("itinary").filter(itinary__region__in=request.user.region.all())
        
        if region is not None:
            if region not in request.user.region.all():
                return Response({
                    "status": False,
                    "message": "This region is not assigned to this user"
                }, status=status.HTTP_403_FORBIDDEN)
            records = records.only("itinary").filter(itinary__region=region)
        
        
        min_date = datetime.strptime(min_date, DATETIME_FORMAT)
        max_date = datetime.strptime(max_date, DATETIME_FORMAT)
        min_records = records.only("date").filter(date__gte=make_aware(min_date, timezone=pytz.UTC))
        max_records = records.only("date").filter(date__gte=make_aware(max_date, timezone=pytz.UTC))
            
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
        # itinary = request.GET.get("itinary-id", None)

        records = Record.objects.only("itinary").filter(itinary__region__in=request.user.region.all())
        
        if region is not None:
            if region not in request.user.region.all():
                return Response({
                    "status": False,
                    "message": "This region is not assigned to this user"
                }, status=status.HTTP_403_FORBIDDEN)
            records = records.only("itinary").filter(itinary__region=region)
        # elif itinary is not None:
        #     records = records.only("itinary").filter(itinary=itinary)
        
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
    
    @action(detail=False, methods=['get'], name='dtd_ytd', url_name='dtd_ytd', permission_classes=[IsAuthenticated])
    def dtd_ytd(self, request):
        date = request.GET.get("date", None)
        if date is None:
            return Response({
                "status": False,
                "message": "Please provide the 'date' params"
            }, status=status.HTTP_404_NOT_FOUND)
        date = datetime.strptime(date, DATETIME_FORMAT)
        first_day = datetime(datetime.now().year, 1, 1)
        
        datas = []
        records = []
        regions = []

        if request.user.is_superuser:
            regions = Region.objects.all()
            records = Record.objects.all()
        else:
            regions = request.user.region.all()
            records = Record.objects.filter(itinary__region__in=regions)

        for region in regions:
            min = make_aware(date, timezone=pytz.UTC) - timedelta(days=1)
            max = make_aware(date, timezone=pytz.UTC) + timedelta(days=1)
            records_dtd = records.only("itinary").filter(itinary__region=region, date__range=(min, max))
            min = make_aware(first_day, timezone=pytz.UTC) - timedelta(days=1)
            records_ytd = records.only("itinary").filter(itinary__region=region, date__range=(min, max))
            dtd_stats = records_dtd.values("action__name").annotate(total=Count("action"))
            ytd_stats = records_ytd.values("action__name").annotate(total=Count("action"))
            dtd_totals = 0
            ytd_totals = 0
            for stat in dtd_stats:
                dtd_totals += stat["total"]
            for stat in ytd_stats:
                ytd_totals += stat["total"]
            # total_pl = DeliveryPoint.objects.filter(record__in=records)
            # active_pl = records.filter(pl__status="actif")
            datas.append({
                "region": region.name,
                "dtd": dtd_stats,
                "ytd": ytd_stats,
                "totals": {
                    "dtd": dtd_totals,
                    "ytd": ytd_totals
                },
                # "customers": total_pl.count(),
                # "active": 0 if len(total_pl) == 0 else round(len(active_pl) / len(total_pl), 2) * 100,
            })

        logger.warning("YTD - DTD datas loaded")
        return Response({
            "status": True,
            "message": "YTD - DTD datas loaded",
            "detail": datas
        }, status=status.HTTP_200_OK)