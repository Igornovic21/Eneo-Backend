import pytz, openpyxl, requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from django.utils.timezone import make_aware
from django.http import HttpResponse

from rest_framework.decorators import authentication_classes, action
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from authorization.authentication import ExpiringTokenAuthentication

from constants.config import DATETIME_FORMAT
from record.serializers.output_serializer import ActionSerializer, CollectorSerializer, EnterpriseSerializer, RecordSerializer
from region.serializers.output_serializer import RegionSerializer

from utils.logger import logger
from utils.pagination import PaginationHandlerMixin, BasicPagination

from region.models import Region
from itinary.models import Itinary
from record.models import Collector, Action, Enterprise, Record, DeliveryPoint

@authentication_classes([ExpiringTokenAuthentication])
class ConfigViewSet(ViewSet, PaginationHandlerMixin):
    pagination_class = BasicPagination
    region_serializer_class = RegionSerializer
    action_serializer_class = ActionSerializer
    collector_serializer_class = CollectorSerializer
    enterprise_serializer_class = EnterpriseSerializer
    record_serializer_class = RecordSerializer
    permission_classes = [IsAuthenticated]

    def get_itinary_object(self, pk:str):
        try:
            return Itinary.objects.get(pk=pk)
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
        regions = request.user.region.all()
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
    
    @action(detail=False, methods=['get'], name='image_proxy', url_name='image_proxy', permission_classes=[AllowAny])
    def image_proxy(self, request, pk=None):
        url = request.GET.get("url", None)
        username = 'if.geosm@gmail.com'
        password = 'IgorOdk.237'

        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        return HttpResponse(response.content, content_type='image/jpeg')
    
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
    
    @action(detail=True, methods=['get'], name='export', url_name='export', permission_classes=[AllowAny])
    def export(self, request, pk=None):
        region = self.get_region_object(pk=pk)
        if type(region) is Response : return region
        # if region not in request.user.region.all():
        #     return Response({
        #         "status": False,
        #         "message": "This region is not assigned to this user"
        #     }, status=status.HTTP_403_FORBIDDEN)
        
        itinary = request.GET.get("itinary", None)
        agency = request.GET.get("agency", None)
        action = request.GET.get("action", None)
        collector = request.GET.get("collector", None)
        enterprise = request.GET.get("enterprise", None)
        min_date = request.GET.get("min_date", None)
        max_date = request.GET.get("max_date", None)

        records = Record.objects.only("itinary").filter(itinary__region=region)
        
        if action is not None:
            records = records.only("action").filter(action__in=action.split(";"))
        if collector is not None:
            records = records.only("collector").filter(collector__in=collector.split(";"))
        if enterprise is not None:
            records = records.only("enterprise").filter(enterprise__in=enterprise.split(";"))
        if agency is not None:
            records = records.only("itinary").filter(itinary__agency=agency)
        if itinary is not None:
            records = records.only("itinary").filter(itinary__block_code=itinary)
        if min_date is not None:
            date = datetime.strptime(min_date, DATETIME_FORMAT)
            records = records.only("date").filter(date__date__gte=make_aware(date, timezone=pytz.UTC))
        if max_date is not None:
            date = datetime.strptime(max_date, DATETIME_FORMAT)
            records = records.only("date").filter(date__date__lte=make_aware(date, timezone=pytz.UTC))

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        
        if not records.exists():
            sheet.title = region.name
        else:
            sheet.title = records[0].itinary.region.name

        headers = [
            'ID',
            'Matricule_co',
            'Collecteur',
            'Entreprise',
            'Action',
            'Nbre_PL',
            'Type_PL',
            'No_Serie_PL',
            'Code_Barre_PL',
            'Raison_PL',
            'Batiment_PL',
            'Status_PL',
            'Images_PL',
            'Activite_PL',
            'Lattitude',
            'Longitude',
            'Contrat',
            'Montant',
            'Accessibilite',
            'Anomalie',
            'No_scelle',
            'Action_coupure',
            'Banoc_code',
            'Date'
        ]
        sheet.append(headers)
        for record in records:
            images = []
            types = []
            no_series = []
            bar_codes = []
            reasons = []
            batiments = []
            status = []
            activities = []
            delivery_points = DeliveryPoint.objects.only("record").filter(record=record)
            for delivery_point in delivery_points:
                images.append(delivery_point.image_url if delivery_point.image_url != "" else "")
                types.append(delivery_point.type)
                no_series.append(delivery_point.serial_number)
                bar_codes.append(delivery_point.code_bare)
                reasons.append(delivery_point.reason)
                batiments.append(delivery_point.batiment)
                status.append(delivery_point.status)
                activities.append(delivery_point.activite)
            sheet.append([
                record.ona_id,
                record.collector.matricule,
                record.collector.name,
                record.enterprise.name,
                record.action.name,
                len(delivery_points),
                ";".join(types),
                ";".join(no_series),
                ";".join(bar_codes),
                ";".join(reasons),
                ";".join(batiments),
                ";".join(status),
                ";".join(images),
                ";".join(activities),
                record.location.coordinates.x,
                record.location.coordinates.y,
                record.contrat,
                record.amount,
                record.accessibility,
                record.code_anomaly,
                record.sealed_number,
                record.cut_action,
                record.banoc_code,
                record.date.strftime("%d/%m/%Y, %H:%M:%S")
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="data_exported.xlsx"'
        workbook.save(response)
        return response