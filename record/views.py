from rest_framework.decorators import action, authentication_classes

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authorization.authentication import ExpiringTokenAuthentication

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

    def list(self, request):
        records = Record.objects.filter(status="Active")
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(records, many=True)
            
        serializer = self.serializer_class(records, many=True)
        logger.warning("Records list loaded")
        return Response({
            "status": True,
            "message": "Records list loaded",
            "detail": serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        region = self.get_region_object(pk=pk)
        if type(region) is Response : return region

        records = Record.objects.only('itinary').filter(itinary__region=region)
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(records, many=True)
        logger.warning("Records list loaded")
        return Response({
            "status": True,
            "message": "Records list loaded",
            "detail": serializer.data
        }, status=status.HTTP_200_OK)