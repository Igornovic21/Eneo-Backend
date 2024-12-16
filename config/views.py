import pytz, json, openpyxl
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
from constants.ona_api import ONA_BASE_URL
from record.serializers.output_serializer import ActionSerializer, CollectorSerializer, EnterpriseSerializer, RecordSerializer
from region.serializers.output_serializer import RegionSerializer

from utils.logger import logger
from utils.pagination import PaginationHandlerMixin, BasicPagination

from region.models import Region
from itinary.models import Itinary
from record.models import Collector, Action, Enterprise, Record

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
    
    @action(detail=False, methods=['get'], name='export', url_name='export', permission_classes=[AllowAny])
    def export(self, request):
        region = request.GET.get("region", None)
        # # itinary = request.GET.get("itinary", None)
        # action = request.GET.get("action", None)
        # collector = request.GET.get("collector", None)
        # enterprise = request.GET.get("enterprise", None)
        # min_date = request.GET.get("min_date", None)
        # max_date = request.GET.get("max_date", None)

        # records = Record.objects.all()
        
        # if region is not None:
        #     records = records.only("itinary").filter(itinary__region=region)
        # if action is not None:
        #     records = records.only("action").filter(action__in=action.split(";"))
        # if collector is not None:
        #     records = records.only("collector").filter(collector__in=collector.split(";"))
        # if enterprise is not None:
        #     records = records.only("enterprise").filter(enterprise__in=enterprise.split(";"))
        # if min_date is not None:
        #     date = datetime.strptime(min_date, DATETIME_FORMAT)
        #     records = records.only("date").filter(date__gt=make_aware(date, timezone=pytz.UTC))
        # if max_date is not None:
        #     date = datetime.strptime(max_date, DATETIME_FORMAT)
        #     records = records.only("date").filter(date__lt=make_aware(date, timezone=pytz.UTC))

        # page = self.paginate_queryset(records)
        # if page is not None:
        #     serializer = self.get_paginated_response(self.record_serializer_class(page, many=True).data)
        # else:
        #     serializer = self.record_serializer_class(records, many=True)
        # # serializer = self.record_serializer_class(records, many=True)
        # logger.warning("Export data successfully")
        # return Response({
        #     "status": True,
        #     "message": "Export data successfully",
        #     "detail": serializer.data
        # }, status=status.HTTP_200_OK)
        region = request.GET.get("region", None)
        
        if region not in request.user.region.all():
            return Response({
                "status": False,
                "message": "This region is not assigned to this user"
            }, status=status.HTTP_403_FORBIDDEN)
        
        records = Record.objects.only("itinary").filter(itinary__region=region)

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = records[0].itinary.region.name

        headers = [
            'ID',
            'Matricule_co',
            'Collecteur',
            'Entreprise',
            'Action',
            'Nbre_PL',
            'Type_PL',
            'No_PL',
            'Status_PL',
            'Lattitude',
            'Longitude',
            'Contrat',
            'Montant',
            'Accessibilite',
            'Anomalie',
            'No_scelle',
            'Action_coupure',
            'images'
        ]
        sheet.append(headers)

        # id: submission.data.id,
        # matricule_co: submission.data.matricule_co,
        # collecteur: submission.data.Collecteur,
        # entreprise: submission.data.entreprise_collecteur,
        # action: submission.data.action,
        # nbre_pl: submission.data.nbr_pl,
        # contrat: submission.data.contrat,
        # montant: submission.data.montant,
        # accessibilite: submission.data.accesibilite,
        # anomalie: submission.data.code_anomaly,
        # no_scelle: submission.data.numero_scelle,
        # action_coupure: submission.data.action_coupure,
        # lat_long: submission.data._geolocation.join(';'),
        # images: imgs.join(';'),

        headers = [
            'ID',
            'Matricule_co',
            'Collecteur',
            'Entreprise',
            'Action',
            'Nbre_PL',
            'Type_PL',
            'No_PL',
            'Status_PL',
            'Lattitude',
            'Longitude',
            'Contrat',
            'Montant',
            'Accessibilite',
            'Anomalie',
            'No_scelle',
            'Action_coupure',
            'Images',
            'Date'
        ]
        for record in records:
            data = json.loads(record.data)
            images = []
            types = []
            no_series = []
            status = []
            for pl in data["pl"]:
                types.append(pl["pl/info_pl/type_compteur"])
                no_series.append(pl["pl/info_pl/serial_number"])
                status.append(pl["pl/info_pl/status"])
            for img in data["_attachments"]:
                images.append(ONA_BASE_URL + img["download_url"])
            sheet.append([
                data["id"],
                data["matricule_co"],
                data["Collecteur"],
                data["entreprise_collecteur"],
                data["action"],
                data["nbr_pl"],
                ";".join(types),
                ";".join(no_series),
                ";".join(status),
                data["_geolocation"][0],
                data["_geolocation"][1],
                data["contrat"],
                data["montant"],
                data["accesibilite"],
                data["code_anomaly"],
                data["numero_scelle"],
                data["action_coupure"],
                ";".join(images),
                record.date.strftime("%d/%m/%Y, %H:%M:%S")
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="data_exported.xlsx"'
        workbook.save(response)
        return response