"""
AGMP REST API ViewSets
======================
Read-only API for the African Genomics Medicine Portal.

All list endpoints are paginated (default 25, max 100).
Use ``?page=N&page_size=M`` query parameters.

Authentication
--------------
- ``check_exists``, ``stats``, ``search`` actions: **public** (AllowAny)
- All other list / retrieve endpoints: **authenticated** (session or token)

Filtering / Search / Ordering
-----------------------------
Every viewset supports:
- ``?search=<term>``  — full-text search across key fields
- ``?ordering=<field>`` — sort ascending; prefix with ``-`` for descending
- Field-level filters via query params (see each viewset's ``filterset_fields``)
"""

import logging

from django.db.models import Count, Q
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .pagination import StandardResultsSetPagination
from .models import (
    Variantagmp, Geneagmp, Drugagmp, Studyagmp,
    Phenotypeagmp, VariantStudyagmp,
)
from .serializers import (
    # List (compact) serializers
    VariantagmpListSerializer,
    GeneagmpListSerializer,
    DrugagmpListSerializer,
    PhenotypeagmpListSerializer,
    StudyagmpListSerializer,
    VariantStudyagmpListSerializer,
    # Detail (full) serializers
    VariantagmpDetailSerializer,
    GeneagmpDetailSerializer,
    DrugagmpDetailSerializer,
    PhenotypeagmpDetailSerializer,
    StudyagmpDetailSerializer,
    VariantStudyagmpDetailSerializer,
    # Stats
    DatabaseStatsSerializer,
)

logger = logging.getLogger(__name__)


# ============================================================
# MIXINS
# ============================================================

class ReadOnlyWithSearchMixin:
    """Common config shared by every AGMP viewset."""
    http_method_names = ['get', 'head', 'options']
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    permission_classes = [AllowAny]


# ============================================================
# VARIANT VIEWSET
# ============================================================

class VariantagmpViewSet(ReadOnlyWithSearchMixin, viewsets.ReadOnlyModelViewSet):
    """
    Genomic variants in the AGMP database.

    list:
    Returns paginated variants with compact gene/drug names.
    Supports full-text search, field filters, and ordering.

    retrieve:
    Full variant detail with nested gene, drug, phenotype objects and study count.

    check_exists:
    Public endpoint to check if a variant ID exists in the database.
    No authentication required.

    studies:
    Paginated list of studies associated with this variant.

    drugs:
    Paginated list of drugs associated with this variant.

    phenotypes:
    Paginated list of phenotypes/diseases associated with this variant.
    """
    lookup_field = 'rs_id'
    lookup_url_kwarg = 'rs_id'

    search_fields = [
        'rs_id', 'allele', 'variant_type', 'source_db',
        'geneagmp__gene_name', 'geneagmp__gene_id',
        'id_in_source_db',
    ]
    ordering_fields = ['rs_id', 'variant_type', 'source_db', 'allele']
    ordering = ['rs_id']
    filterset_fields = {
        'rs_id': ['exact', 'icontains'],
        'variant_type': ['exact', 'icontains'],
        'source_db': ['exact', 'icontains'],
        'allele': ['exact', 'icontains'],
        'id_in_source_db': ['exact', 'icontains'],
        'geneagmp__gene_id': ['exact'],
        'geneagmp__gene_name': ['exact', 'icontains'],
        'drugagmp__drug_bank_id': ['exact'],
        'drugagmp__drug_name': ['exact', 'icontains'],
        'phenotypeagmp__name': ['exact', 'icontains'],
    }

    def get_queryset(self):
        return Variantagmp.objects.select_related(
            'geneagmp', 'drugagmp', 'studyagmp', 'phenotypeagmp',
        ).all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VariantagmpDetailSerializer
        return VariantagmpListSerializer

    # ── Custom actions ────────────────────────

    @action(detail=False, methods=['get'], permission_classes=[AllowAny],
            url_path='check_exists', url_name='check-exists')
    def check_exists(self, request):
        """
        Public lookup: does a variant exist?

        Query params:
            rs_id (required): The variant RS ID to check, e.g. ``rs1045642``

        Returns:
            exists (bool), count (int), rs_id (str), url (str|null)
        """
        rs_id = request.query_params.get('rs_id')
        if not rs_id:
            return Response(
                {'error': 'Please provide rs_id parameter'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        qs = Variantagmp.objects.filter(rs_id=rs_id)
        exists = qs.exists()
        url = request.build_absolute_uri(
            f'/api/variants/{rs_id}/'
        ) if exists else None

        return Response({
            'exists': exists,
            'count': qs.count(),
            'rs_id': rs_id,
            'url': url,
        })

    @action(detail=True, methods=['get'], url_path='studies', url_name='studies')
    def studies(self, request, rs_id=None):
        """Paginated studies associated with this variant."""
        variant_studies = VariantStudyagmp.objects.filter(
            variantagmp__rs_id=rs_id
        ).select_related('studyagmp', 'variantagmp', 'variantagmp__geneagmp')
        page = self.paginate_queryset(variant_studies)
        if page is not None:
            serializer = VariantStudyagmpListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = VariantStudyagmpListSerializer(variant_studies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='drugs', url_name='drugs')
    def drugs(self, request, rs_id=None):
        """Paginated drugs associated with this variant (via PharmGKB records)."""
        drugs = Drugagmp.objects.filter(
            drugs__rs_id=rs_id  # related_name="drugs" on Variantagmp.drugagmp
        ).distinct()
        page = self.paginate_queryset(drugs)
        if page is not None:
            serializer = DrugagmpListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = DrugagmpListSerializer(drugs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='phenotypes', url_name='phenotypes')
    def phenotypes(self, request, rs_id=None):
        """Paginated phenotypes/diseases associated with this variant."""
        phenotypes = Phenotypeagmp.objects.filter(
            variantagmp__rs_id=rs_id
        ).distinct()
        page = self.paginate_queryset(phenotypes)
        if page is not None:
            serializer = PhenotypeagmpListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PhenotypeagmpListSerializer(phenotypes, many=True)
        return Response(serializer.data)


# ============================================================
# GENE VIEWSET
# ============================================================

class GeneagmpViewSet(ReadOnlyWithSearchMixin, viewsets.ReadOnlyModelViewSet):
    """
    Genes in the AGMP database.

    list:
    Paginated gene list with search and chromosome filtering.

    retrieve:
    Full gene detail including function, UniProt accession,
    and computed counts of associated variants, drugs, phenotypes, and studies.

    variants:
    Paginated variants for this gene.

    drugs:
    Paginated drugs associated via this gene's variants.
    """
    lookup_field = 'gene_id'
    lookup_url_kwarg = 'gene_id'

    search_fields = ['gene_id', 'gene_name', 'chromosome', 'function', 'uniprot_ac']
    ordering_fields = ['gene_id', 'gene_name', 'chromosome']
    ordering = ['gene_id']
    filterset_fields = {
        'gene_id': ['exact', 'icontains'],
        'gene_name': ['exact', 'icontains'],
        'chromosome': ['exact'],
        'uniprot_ac': ['exact'],
    }

    def get_queryset(self):
        return Geneagmp.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GeneagmpDetailSerializer
        return GeneagmpListSerializer

    @action(detail=True, methods=['get'], url_path='variants', url_name='variants')
    def variants(self, request, gene_id=None):
        """Paginated variants for this gene."""
        variants = Variantagmp.objects.filter(
            geneagmp__gene_id=gene_id
        ).select_related('geneagmp', 'drugagmp', 'phenotypeagmp')
        page = self.paginate_queryset(variants)
        if page is not None:
            serializer = VariantagmpListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = VariantagmpListSerializer(variants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='drugs', url_name='drugs')
    def drugs(self, request, gene_id=None):
        """Paginated drugs associated with this gene's variants."""
        drugs = Drugagmp.objects.filter(
            drugs__geneagmp__gene_id=gene_id
        ).distinct()
        page = self.paginate_queryset(drugs)
        if page is not None:
            serializer = DrugagmpListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = DrugagmpListSerializer(drugs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='phenotypes', url_name='phenotypes')
    def phenotypes(self, request, gene_id=None):
        """Paginated phenotypes associated with this gene's variants."""
        phenotypes = Phenotypeagmp.objects.filter(
            variantagmp__geneagmp__gene_id=gene_id
        ).distinct()
        page = self.paginate_queryset(phenotypes)
        if page is not None:
            serializer = PhenotypeagmpListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PhenotypeagmpListSerializer(phenotypes, many=True)
        return Response(serializer.data)


# ============================================================
# DRUG VIEWSET
# ============================================================

class DrugagmpViewSet(ReadOnlyWithSearchMixin, viewsets.ReadOnlyModelViewSet):
    """
    Drugs in the AGMP database.

    list:
    Paginated drug list with search and field filtering.

    retrieve:
    Full drug detail including indication, IUPAC name, and counts.

    variants:
    Paginated variants associated with this drug.

    genes:
    Paginated genes associated with this drug's variants.
    """
    lookup_field = 'drug_bank_id'
    lookup_url_kwarg = 'drug_bank_id'

    search_fields = ['drug_name', 'drug_bank_id', 'drug_id', 'state', 'indication']
    ordering_fields = ['drug_name', 'drug_bank_id', 'state']
    ordering = ['drug_name']
    filterset_fields = {
        'drug_name': ['exact', 'icontains'],
        'drug_bank_id': ['exact'],
        'drug_id': ['exact'],
        'state': ['exact', 'icontains'],
    }

    def get_queryset(self):
        return Drugagmp.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DrugagmpDetailSerializer
        return DrugagmpListSerializer

    @action(detail=True, methods=['get'], url_path='variants', url_name='variants')
    def variants(self, request, drug_bank_id=None):
        """Paginated variants associated with this drug."""
        variants = Variantagmp.objects.filter(
            drugagmp__drug_bank_id=drug_bank_id
        ).select_related('geneagmp', 'drugagmp', 'phenotypeagmp')
        page = self.paginate_queryset(variants)
        if page is not None:
            serializer = VariantagmpListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = VariantagmpListSerializer(variants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='genes', url_name='genes')
    def genes(self, request, drug_bank_id=None):
        """Paginated genes associated with this drug's variants."""
        genes = Geneagmp.objects.filter(
            variantagmp__drugagmp__drug_bank_id=drug_bank_id
        ).distinct()
        page = self.paginate_queryset(genes)
        if page is not None:
            serializer = GeneagmpListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = GeneagmpListSerializer(genes, many=True)
        return Response(serializer.data)


# ============================================================
# PHENOTYPE VIEWSET
# ============================================================

class PhenotypeagmpViewSet(ReadOnlyWithSearchMixin, viewsets.ReadOnlyModelViewSet):
    """
    Phenotypes / diseases in the AGMP database.

    list:
    Paginated phenotype list with search and name filtering.

    retrieve:
    Full phenotype detail with variant, gene, and study counts.

    variants:
    Paginated variants associated with this phenotype.
    """
    search_fields = ['name']
    ordering_fields = ['name', 'id']
    ordering = ['name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    def get_queryset(self):
        return Phenotypeagmp.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PhenotypeagmpDetailSerializer
        return PhenotypeagmpListSerializer

    @action(detail=True, methods=['get'], url_path='variants', url_name='variants')
    def variants(self, request, pk=None):
        """Paginated variants associated with this phenotype."""
        variants = Variantagmp.objects.filter(
            phenotypeagmp_id=pk
        ).select_related('geneagmp', 'drugagmp', 'phenotypeagmp')
        page = self.paginate_queryset(variants)
        if page is not None:
            serializer = VariantagmpListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = VariantagmpListSerializer(variants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='genes', url_name='genes')
    def genes(self, request, pk=None):
        """Paginated genes associated with this phenotype's variants."""
        genes = Geneagmp.objects.filter(
            variantagmp__phenotypeagmp_id=pk
        ).distinct()
        page = self.paginate_queryset(genes)
        if page is not None:
            serializer = GeneagmpListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = GeneagmpListSerializer(genes, many=True)
        return Response(serializer.data)


# ============================================================
# STUDY VIEWSET
# ============================================================

class StudyagmpViewSet(ReadOnlyWithSearchMixin, viewsets.ReadOnlyModelViewSet):
    """
    Studies / publications in the AGMP database.

    list:
    Paginated study list, newest first by default.
    Supports year-range filtering with ``publication_year__gte`` and ``__lte``.

    retrieve:
    Full study detail including data accession, publication type, and variant count.

    variants:
    Paginated variants linked to this study via the VariantStudyagmp table.
    """
    lookup_field = 'publication_id'
    lookup_url_kwarg = 'publication_id'

    search_fields = ['publication_id', 'title', 'study_type', 'publication_year', 'data_ac']
    ordering_fields = ['publication_id', 'publication_year', 'study_type', 'title']
    ordering = ['-publication_year']
    filterset_fields = {
        'publication_id': ['exact'],
        'study_type': ['exact', 'icontains'],
        'publication_type': ['exact', 'icontains'],
        'publication_year': ['exact', 'gte', 'lte'],
        'data_ac': ['exact'],
    }

    def get_queryset(self):
        return Studyagmp.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudyagmpDetailSerializer
        return StudyagmpListSerializer

    @action(detail=True, methods=['get'], url_path='variants', url_name='variants')
    def variants(self, request, publication_id=None):
        """Paginated variants linked to this study."""
        variants = Variantagmp.objects.filter(
            variantstudyagmp__studyagmp__publication_id=publication_id
        ).select_related('geneagmp', 'drugagmp', 'phenotypeagmp').distinct()
        page = self.paginate_queryset(variants)
        if page is not None:
            serializer = VariantagmpListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = VariantagmpListSerializer(variants, many=True)
        return Response(serializer.data)


# ============================================================
# VARIANT-STUDY VIEWSET (the join/association table)
# ============================================================

class VariantStudyagmpViewSet(ReadOnlyWithSearchMixin, viewsets.ReadOnlyModelViewSet):
    """
    Variant-study associations with country/location and population data.

    Each record links a variant to a study and includes up to 30 participant
    countries with coordinates, plus ethnicity, p-value, and population notes.

    list:
    Compact representation with RS ID, publication ID, country, and p-value.

    retrieve:
    Full detail with nested variant/study objects and a ``countries`` array
    that collects all 30 denormalised country columns into a clean list.
    """
    search_fields = [
        'variantagmp__rs_id', 'studyagmp__publication_id',
        'studyagmp__title', 'country_participant', 'ethnicity',
    ]
    ordering_fields = ['id', 'studyagmp__publication_year', 'p_value']
    ordering = ['-studyagmp__publication_year']
    filterset_fields = {
        'variantagmp__rs_id': ['exact'],
        'studyagmp__publication_id': ['exact'],
        'studyagmp__study_type': ['exact'],
        'country_participant': ['exact', 'icontains'],
        'ethnicity': ['exact', 'icontains'],
        'mixed_population': ['exact'],
    }

    def get_queryset(self):
        return VariantStudyagmp.objects.select_related(
            'variantagmp', 'studyagmp',
            'variantagmp__geneagmp', 'variantagmp__drugagmp',
        ).all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VariantStudyagmpDetailSerializer
        return VariantStudyagmpListSerializer


# ============================================================
# DATABASE-WIDE STATISTICS (public)
# ============================================================

class StatsViewSet(viewsets.ViewSet):
    """
    Aggregate database statistics — publicly accessible.

    list:
    Returns counts of genes, drugs, variants, phenotypes, and studies,
    plus the list of source databases represented in the data.
    """
    permission_classes = [AllowAny]

    def list(self, request):
        data = {
            'gene_count': (
                Geneagmp.objects
                .exclude(gene_id__iexact='')
                .exclude(gene_id__iexact='nan')
                .values('gene_id').distinct().count()
            ),
            'drug_count': (
                Drugagmp.objects
                .exclude(drug_bank_id__iexact='')
                .exclude(drug_bank_id__iexact='nan')
                .values('drug_bank_id').distinct().count()
            ),
            'variant_count': (
                Variantagmp.objects
                .exclude(rs_id__iexact='')
                .exclude(rs_id__iexact='nan')
                .values('rs_id').distinct().count()
            ),
            'phenotype_count': (
                Variantagmp.objects
                .values('phenotypeagmp__name').distinct().count()
            ),
            'study_count': (
                Studyagmp.objects
                .exclude(publication_id__iexact='')
                .exclude(publication_id__iexact='nan')
                .values('publication_id').distinct().count()
            ),
            'source_databases': list(
                Variantagmp.objects
                .exclude(source_db__isnull=True)
                .values_list('source_db', flat=True)
                .distinct().order_by('source_db')
            ),
        }
        serializer = DatabaseStatsSerializer(data)
        return Response(serializer.data)