from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Variantagmp
from .serializers import VariantagmpSerializer


class VariantagmpViewSet(viewsets.ModelViewSet):
    serializer_class = VariantagmpSerializer
    http_method_names = ['get', 'head', 'options']
    filter_backends = [filters.SearchFilter]
    search_fields = ['allele', 'variant_type', 'source_db']
    
    # Use rs_id as the lookup field instead of pk
    lookup_field = 'rs_id'
    lookup_url_kwarg = 'rs_id'

    def get_permissions(self):
        """
        Custom permissions per action:
        - check_exists: public access
        - list/retrieve: authenticated users
        """
        if self.action == 'check_exists':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Variantagmp.objects.select_related(
            'geneagmp',
            'drugagmp',
            'studyagmp',
            'phenotypeagmp'
        ).all()
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
        exists = qs.exists()
        
        if exists:
            url = request.build_absolute_uri(f'/variant-phenotype/{rs_id}/')
        else:
            url = None
        
        return Response({
            'exists': exists,
            'count': qs.count(),
            'rs_id': rs_id,
            'url': url
        })