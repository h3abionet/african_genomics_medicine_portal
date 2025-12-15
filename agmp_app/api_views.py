from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Variantagmp
from .serializers import VariantagmpSerializer


class VariantagmpViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Variantagmp
    Supports:
    - GET (list, retrieve)
    - PUT / PATCH (update)
    - DELETE (delete)
    """

    serializer_class = VariantagmpSerializer

    # 🔹 Allow only safe methods
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options']

    # Enable search for other fields (partial match)
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'allele',
        'variant_type',
        'source_db'
    ]

    def get_queryset(self):
        """
        Override to allow exact match search by rs_id using query param:
        /api/variants/?rs_id=rs7
        """
        qs = Variantagmp.objects.select_related(
            'geneagmp',
            'drugagmp',
            'studyagmp',
            'phenotypeagmp'
        ).all()

        rs_id = self.request.query_params.get('rs_id')
        if rs_id:
            qs = qs.filter(rs_id=rs_id)  # exact match

        return qs

    @action(detail=False, methods=['get'])
    def check_exists(self, request):
        """
        Custom endpoint:
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
