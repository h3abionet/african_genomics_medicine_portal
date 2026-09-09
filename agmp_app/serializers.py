"""
AGMP REST API Serializers
=========================
Serializers for all AGMP models, in two tiers:

- **List** (compact) — used in paginated list endpoints and nested references.
- **Detail** (full) — used in retrieve endpoints, includes computed counts
  and nested related objects.
"""

from rest_framework import serializers
from .models import (
    Variantagmp, Geneagmp, Drugagmp, Studyagmp,
    Phenotypeagmp, VariantStudyagmp,
)


# ============================================================
# LIGHTWEIGHT (LIST) SERIALIZERS — used for nested references
# ============================================================

class GeneagmpListSerializer(serializers.ModelSerializer):
    """Compact gene representation for embedding in other responses."""

    class Meta:
        model = Geneagmp
        fields = ['id', 'gene_id', 'gene_name', 'chromosome']


class DrugagmpListSerializer(serializers.ModelSerializer):
    """Compact drug representation for embedding in other responses."""

    class Meta:
        model = Drugagmp
        fields = ['id', 'drug_id', 'drug_bank_id', 'drug_name', 'state']


class PhenotypeagmpListSerializer(serializers.ModelSerializer):
    """Compact phenotype representation."""

    class Meta:
        model = Phenotypeagmp
        fields = ['id', 'name']


class StudyagmpListSerializer(serializers.ModelSerializer):
    """Compact study representation."""

    class Meta:
        model = Studyagmp
        fields = [
            'id', 'publication_id', 'title',
            'publication_year', 'study_type', 'publication_type',
        ]


class VariantagmpListSerializer(serializers.ModelSerializer):
    """Compact variant representation for embedding."""
    gene_name = serializers.CharField(
        source='geneagmp.gene_name', read_only=True, default='',
    )
    gene_id = serializers.CharField(
        source='geneagmp.gene_id', read_only=True, default='',
    )

    class Meta:
        model = Variantagmp
        fields = [
            'id', 'rs_id', 'variant_type', 'allele', 'source_db',
            'gene_name', 'gene_id',
        ]


# ============================================================
# FULL (DETAIL) SERIALIZERS — rich nested data
# ============================================================

class GeneagmpDetailSerializer(serializers.ModelSerializer):
    """Full gene detail with association counts."""
    variant_count = serializers.SerializerMethodField()
    drug_association_count = serializers.SerializerMethodField()
    phenotype_association_count = serializers.SerializerMethodField()
    study_count = serializers.SerializerMethodField()

    class Meta:
        model = Geneagmp
        fields = [
            'id', 'gene_id', 'gene_name', 'chromosome', 'function',
            'uniprot_ac',
            'variant_count', 'drug_association_count',
            'phenotype_association_count', 'study_count',
        ]

    def get_variant_count(self, obj):
        return (Variantagmp.objects.filter(geneagmp=obj)
                .values('rs_id').distinct().count())

    def get_drug_association_count(self, obj):
        return (Variantagmp.objects.filter(geneagmp=obj)
                .exclude(drugagmp__isnull=True).count())

    def get_phenotype_association_count(self, obj):
        return (Variantagmp.objects.filter(geneagmp=obj)
                .exclude(phenotypeagmp__isnull=True).count())

    def get_study_count(self, obj):
        return (VariantStudyagmp.objects
                .filter(variantagmp__geneagmp=obj)
                .values('studyagmp__publication_id').distinct().count())


class DrugagmpDetailSerializer(serializers.ModelSerializer):
    """Full drug detail with association counts."""
    variant_count = serializers.SerializerMethodField()
    gene_count = serializers.SerializerMethodField()
    study_count = serializers.SerializerMethodField()

    class Meta:
        model = Drugagmp
        fields = [
            'id', 'drug_id', 'drug_bank_id', 'drug_name', 'state',
            'indication', 'iupac_name_seq',
            'variant_count', 'gene_count', 'study_count',
        ]

    def get_variant_count(self, obj):
        return (Variantagmp.objects.filter(drugagmp=obj)
                .values('rs_id').distinct().count())

    def get_gene_count(self, obj):
        return (Variantagmp.objects.filter(drugagmp=obj)
                .values('geneagmp__gene_id').distinct().count())

    def get_study_count(self, obj):
        return (VariantStudyagmp.objects
                .filter(variantagmp__drugagmp=obj)
                .values('studyagmp__publication_id').distinct().count())


class PhenotypeagmpDetailSerializer(serializers.ModelSerializer):
    """Full phenotype detail with association counts."""
    variant_count = serializers.SerializerMethodField()
    gene_count = serializers.SerializerMethodField()
    study_count = serializers.SerializerMethodField()

    class Meta:
        model = Phenotypeagmp
        fields = ['id', 'name', 'variant_count', 'gene_count', 'study_count']

    def get_variant_count(self, obj):
        return (Variantagmp.objects.filter(phenotypeagmp=obj)
                .values('rs_id').distinct().count())

    def get_gene_count(self, obj):
        return (Variantagmp.objects.filter(phenotypeagmp=obj)
                .values('geneagmp__gene_id').distinct().count())

    def get_study_count(self, obj):
        return (VariantStudyagmp.objects
                .filter(variantagmp__phenotypeagmp=obj)
                .values('studyagmp__publication_id').distinct().count())


class StudyagmpDetailSerializer(serializers.ModelSerializer):
    """Full study detail with variant count."""
    variant_count = serializers.SerializerMethodField()

    class Meta:
        model = Studyagmp
        fields = [
            'id', 'data_ac', 'publication_id', 'publication_type',
            'publication_year', 'study_type', 'title',
            'variant_count',
        ]

    def get_variant_count(self, obj):
        return VariantStudyagmp.objects.filter(studyagmp=obj).count()


class VariantagmpDetailSerializer(serializers.ModelSerializer):
    """Full variant detail with nested gene, drug, phenotype info."""
    gene = GeneagmpListSerializer(source='geneagmp', read_only=True)
    drug = DrugagmpListSerializer(source='drugagmp', read_only=True)
    phenotype = PhenotypeagmpListSerializer(source='phenotypeagmp', read_only=True)
    study = StudyagmpListSerializer(source='studyagmp', read_only=True)
    study_count = serializers.SerializerMethodField()

    class Meta:
        model = Variantagmp
        fields = [
            'id', 'rs_id', 'variant_type', 'allele', 'source_db',
            'id_in_source_db', 'rs_id_star_annotation',
            'gene', 'drug', 'phenotype', 'study', 'study_count',
        ]

    def get_study_count(self, obj):
        return VariantStudyagmp.objects.filter(variantagmp=obj).count()


# ============================================================
# VARIANT-STUDY SERIALIZER (the join table)
# ============================================================

class CountryParticipantSerializer(serializers.Serializer):
    """One country-participant entry extracted from the denormalised columns."""
    country = serializers.CharField()
    latitude = serializers.CharField(allow_blank=True, allow_null=True)
    longitude = serializers.CharField(allow_blank=True, allow_null=True)


class VariantStudyagmpListSerializer(serializers.ModelSerializer):
    """Compact variant-study association for list endpoints."""
    rs_id = serializers.CharField(source='variantagmp.rs_id', read_only=True, default='')
    publication_id = serializers.CharField(
        source='studyagmp.publication_id', read_only=True, default='',
    )
    study_title = serializers.CharField(
        source='studyagmp.title', read_only=True, default='',
    )
    study_type = serializers.CharField(
        source='studyagmp.study_type', read_only=True, default='',
    )

    class Meta:
        model = VariantStudyagmp
        fields = [
            'id', 'rs_id', 'publication_id', 'study_title', 'study_type',
            'country_participant', 'ethnicity', 'p_value',
        ]


class VariantStudyagmpDetailSerializer(serializers.ModelSerializer):
    """Full variant-study association with nested objects and all countries."""
    variant = VariantagmpListSerializer(source='variantagmp', read_only=True)
    study = StudyagmpListSerializer(source='studyagmp', read_only=True)
    countries = serializers.SerializerMethodField()

    class Meta:
        model = VariantStudyagmp
        fields = [
            'id',
            'variant', 'study',
            'country_participant', 'latitude', 'longitude',
            'mixed_population', 'ethnicity', 'geographical_regions',
            'notes', 'p_value',
            'countries',
        ]

    def get_countries(self, obj):
        """
        Collect all country_participant_* / latitude_* / longitude_*
        columns into a clean list, skipping blanks.
        """
        countries = []
        # Primary country
        if obj.country_participant:
            countries.append({
                'country': obj.country_participant,
                'latitude': obj.latitude or '',
                'longitude': obj.longitude or '',
            })
        # Numbered columns 01-09 use zero-padded suffixes
        for i in range(1, 10):
            suffix = f'_{i:02d}'
            country = getattr(obj, f'country_participant{suffix}', None)
            if country:
                countries.append({
                    'country': country,
                    'latitude': getattr(obj, f'latitude{suffix}', '') or '',
                    'longitude': getattr(obj, f'longitude{suffix}', '') or '',
                })
        # 010-019 use _0XX for country but _XX for lat/lng
        for i in range(10, 20):
            country = getattr(obj, f'country_participant_0{i}', None)
            lat = getattr(obj, f'latitude_{i}', None)
            lng = getattr(obj, f'longitude_{i}', None)
            if country:
                countries.append({
                    'country': country,
                    'latitude': lat or '',
                    'longitude': lng or '',
                })
        # 20-30 use plain _XX suffixes
        for i in range(20, 31):
            country = getattr(obj, f'country_participant_{i}', None)
            lat = getattr(obj, f'latitude_{i}', None)
            lng = getattr(obj, f'longitude_{i}', None)
            if country:
                countries.append({
                    'country': country,
                    'latitude': lat or '',
                    'longitude': lng or '',
                })
        return countries


# ============================================================
# STATS / SUMMARY SERIALIZER (for /api/stats/ endpoint)
# ============================================================

class DatabaseStatsSerializer(serializers.Serializer):
    """Read-only stats summary of the entire AGMP database."""
    gene_count = serializers.IntegerField()
    drug_count = serializers.IntegerField()
    variant_count = serializers.IntegerField()
    phenotype_count = serializers.IntegerField()
    study_count = serializers.IntegerField()
    source_databases = serializers.ListField(child=serializers.CharField())