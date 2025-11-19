from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Variantagmp
from .serializers import VariantagmpSerializer


class VariantagmpViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Variantagmp.objects.select_related(
        'geneagmp', 'drugagmp', 'studyagmp', 'phenotypeagmp'
    ).all()
    serializer_class = VariantagmpSerializer
    filter_backends = [filters.SearchFilter]  # Remove DjangoFilterBackend for now
    
    # Search only in fields that DEFINITELY exist
    search_fields = ['rs_id', 'allele', 'variant_type', 'source_db']
    
    @action(detail=False, methods=['get'])
    def check_exists(self, request):
        rs_id = request.query_params.get('rs_id', None)
        
        if not rs_id:
            return Response({'error': 'Please provide rs_id parameter'}, status=400)
        
        exists = Variantagmp.objects.filter(rs_id=rs_id).exists()
        count = Variantagmp.objects.filter(rs_id=rs_id).count()
        
        return Response({
            'exists': exists,
            'count': count,
            'rs_id': rs_id
        })