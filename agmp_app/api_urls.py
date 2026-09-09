"""
AGMP API URL Configuration
==========================

All API endpoints live under ``/api/`` (matching the existing URL structure).

Integration with your existing urls.py
---------------------------------------
Replace the existing router + ``path('api/', include(router.urls))`` block with::

    from .api_urls import urlpatterns as api_urls

    urlpatterns = [
        ...
        path('api/', include(api_urls)),
        ...
    ]

Interactive documentation (requires ``drf-spectacular``):
    - Swagger UI:  /api/docs/
    - ReDoc:       /api/docs/redoc/
    - OpenAPI JSON: /api/schema/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    VariantagmpViewSet,
    GeneagmpViewSet,
    DrugagmpViewSet,
    PhenotypeagmpViewSet,
    StudyagmpViewSet,
    VariantStudyagmpViewSet,
    StatsViewSet,
)

app_name = 'agmp-api'

router = DefaultRouter()
router.register(r'variants',        VariantagmpViewSet,      basename='variant')
router.register(r'genes',           GeneagmpViewSet,         basename='gene')
router.register(r'drugs',           DrugagmpViewSet,         basename='drug')
router.register(r'phenotypes',      PhenotypeagmpViewSet,    basename='phenotype')
router.register(r'studies',         StudyagmpViewSet,        basename='study')
router.register(r'variant-studies', VariantStudyagmpViewSet, basename='variant-study')
router.register(r'stats',           StatsViewSet,            basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]

# ── Optional: drf-spectacular docs ────────────────────────
# Wrapped in try/except so the app works before you install drf-spectacular.
try:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularSwaggerView,
        SpectacularRedocView,
    )
    urlpatterns += [
        path('schema/',      SpectacularAPIView.as_view(),                          name='schema'),
        path('docs/',        SpectacularSwaggerView.as_view(url_name='agmp-api:schema'), name='swagger-ui'),
        path('docs/redoc/',  SpectacularRedocView.as_view(url_name='agmp-api:schema'),   name='redoc'),
    ]
except ImportError:
    pass