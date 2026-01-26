from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from .models import Variantagmp
from .serializers import VariantagmpSerializer


class VariantagmpViewSet(viewsets.ModelViewSet):
    serializer_class = VariantagmpSerializer
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options']
    filter_backends = [filters.SearchFilter]
    search_fields = ['allele', 'variant_type', 'source_db']

    def get_permissions(self):
        """
        Custom permissions per action:
        - check_exists: public access
        - list/retrieve: authenticated users
        - update/delete: admin only
        """
        if self.action == 'check_exists':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Variantagmp.objects.select_related(
            'geneagmp',
            'drugagmp',
            'studyagmp',
            'phenotypeagmp'
        ).all()

        rs_id = self.request.query_params.get('rs_id')
        if rs_id:
            qs = qs.filter(rs_id=rs_id)
        return qs

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def check_exists(self, request):
        """
        Public endpoint:
        /api/variants/check_exists/?rs_id=rs123
        """
        rs_id = request.query_params.get('rs_id')
        if not rs_id:
            return Response(
                {'error': 'Please provide rs_id parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = Variantagmp.objects.filter(rs_id=rs_id)
        return Response({
            'exists': qs.exists(),
            'count': qs.count(),
            'rs_id': rs_id
        })