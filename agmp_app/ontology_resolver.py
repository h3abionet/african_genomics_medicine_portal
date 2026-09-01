

import requests
import urllib.parse
import logging
from django.core.cache import cache
from django.db.models import Q

logger = logging.getLogger(__name__)

OLS_BASE = "https://www.ebi.ac.uk/ols4/api"
OXO_BASE = "https://www.ebi.ac.uk/spot/oxo/api"
REQUEST_TIMEOUT = 10


class OntologyResolver:
    """
    Fully config-driven ontology resolution.
    Reads all behaviour from the database — ontologies to query,
    fields to match, hierarchy depth, cache duration, etc.
    """

    def __init__(self, category):
        from .models import OntologyConfig, SearchFieldMapping, OxOMapping

        self.category = category
        self._configs = list(
            OntologyConfig.objects
            .filter(category=category, enabled=True)
            .order_by('priority')
        )
        self._field_mappings = list(
            SearchFieldMapping.objects
            .filter(category=category, enabled=True)
            .order_by('is_fallback')
        )
        self._oxo_targets = list(
            OxOMapping.objects
            .filter(source_category=category, enabled=True)
        )

    @property
    def ontology_ids(self):
        return ','.join(c.ols_id for c in self._configs)

    @property
    def _cache_ttl(self):
        if self._configs:
            return self._configs[0].cache_duration
        return 86400

    @property
    def _max_hits(self):
        if self._configs:
            return max(c.max_search_hits for c in self._configs)
        return 5

    # ── OLS4 calls ──────────────────────────

    @staticmethod
    def _double_encode(iri):
        return urllib.parse.quote(
            urllib.parse.quote(iri, safe=''), safe=''
        )

    def _ols_search(self, query):
        ontologies = self.ontology_ids
        if not ontologies:
            return []

        cache_key = f"ols:s:{self.category}:{query.lower().strip()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            resp = requests.get(f"{OLS_BASE}/search", params={
                'q': query,
                'ontology': ontologies,
                'rows': self._max_hits,
                'exact': 'false',
                'queryFields': 'label,synonym',
                'fieldList': 'label,synonym,iri,ontology_name,short_form',
            }, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            hits = resp.json().get('response', {}).get('docs', [])
            cache.set(cache_key, hits, timeout=self._cache_ttl)
            return hits
        except Exception as e:
            logger.warning(f"OLS search failed [{self.category}] '{query}': {e}")
            return []

    def _ols_get_children(self, iri, ontology_id, config):
        if not config.expand_children:
            return []

        cache_key = f"ols:c:{ontology_id}:{iri}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            encoded = self._double_encode(iri)
            resp = requests.get(
                f"{OLS_BASE}/ontologies/{ontology_id}/terms/{encoded}/children",
                params={'size': config.max_children},
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            children = resp.json().get('_embedded', {}).get('terms', [])
            cache.set(cache_key, children, timeout=config.cache_duration)
            return children
        except Exception as e:
            logger.warning(f"OLS children failed {ontology_id}:{iri}: {e}")
            return []

    def _walk_children(self, iri, ontology_id, config, current_depth=1):
        """Recursively walk children up to config.child_depth."""
        if current_depth > config.child_depth:
            return []
        children = self._ols_get_children(iri, ontology_id, config)
        all_terms = list(children)
        if current_depth < config.child_depth:
            for child in children:
                child_iri = child.get('iri', '')
                if child_iri:
                    all_terms.extend(
                        self._walk_children(child_iri, ontology_id, config, current_depth + 1)
                    )
        return all_terms

    # ── OxO calls ───────────────────────────

    def _oxo_cross_map(self, term_ids):
        if not self._oxo_targets or not term_ids:
            return set()

        targets = [t.target_ontology_prefix for t in self._oxo_targets]
        max_distance = max(t.distance for t in self._oxo_targets)

        cache_key = f"oxo:{self.category}:{','.join(sorted(term_ids))}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            resp = requests.post(f"{OXO_BASE}/search", json={
                'ids': list(term_ids),
                'mappingTarget': targets,
                'distance': max_distance,
            }, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            results = data.get('_embedded', {}).get('searchResults', [])
            labels = set()
            for r in results:
                for m in r.get('mappingResponseList', []):
                    label = m.get('label', '')
                    if label:
                        labels.add(label)
            cache.set(cache_key, labels, timeout=self._cache_ttl)
            return labels
        except Exception as e:
            logger.warning(f"OxO cross-map failed [{self.category}]: {e}")
            return set()

    # ── Main resolution ─────────────────────

    def resolve(self, user_input):
        """
        Resolve user input to:
          - all_names: set of strings to match against the DB
          - expansion_info: list of human-readable expansion steps
        """
        user_input = user_input.strip()
        all_names = {user_input}
        expansion_info = []
        collected_term_ids = set()

        # Build a lookup: ontology_id → config
        config_by_ontology = {c.ols_id: c for c in self._configs}

        hits = self._ols_search(user_input)

        for hit in hits:
            label = hit.get('label', '')
            synonyms = hit.get('synonym', []) or []
            ontology = hit.get('ontology_name', '')
            iri = hit.get('iri', '')
            short_form = hit.get('short_form', '')

            if label:
                all_names.add(label)
                expansion_info.append(f"{label} ({ontology})")

            for syn in synonyms:
                all_names.add(syn)

            # Track term IDs for OxO cross-mapping
            if short_form:
                # Convert e.g. "DOID_9352" → "DOID:9352"
                if '_' in short_form:
                    collected_term_ids.add(short_form.replace('_', ':', 1))
                else:
                    collected_term_ids.add(short_form)

            # Walk children if config allows
            config = config_by_ontology.get(ontology)
            if config and iri:
                children = self._walk_children(iri, ontology, config)
                for child in children:
                    child_label = child.get('label', '')
                    child_syns = child.get('synonym', []) or []
                    if child_label:
                        all_names.add(child_label)
                        expansion_info.append(f"  ↳ {child_label}")
                    for cs in child_syns:
                        all_names.add(cs)

        # OxO cross-mapping (if configured)
        oxo_labels = self._oxo_cross_map(collected_term_ids)
        for label in oxo_labels:
            all_names.add(label)
        if oxo_labels:
            expansion_info.append(f"  + {len(oxo_labels)} cross-ontology mappings")

        return all_names, expansion_info

    # ── Build Django Q ──────────────────────

    def build_q(self, user_input):
        """
        Build a Django Q object from resolved names,
        using the field mappings defined in the admin.
        """
        names, info = self.resolve(user_input)
        q = Q()

        for mapping in self._field_mappings:
            if mapping.is_fallback:
                # Fallback: match raw input loosely
                q |= Q(**{f"{mapping.lookup_field}__{mapping.lookup_type}": user_input})
            else:
                # Exact/precise match for each resolved name
                for name in names:
                    q |= Q(**{f"{mapping.lookup_field}__{mapping.lookup_type}": name})

        # Safety net: if no field mappings configured, return empty Q
        if not self._field_mappings:
            logger.warning(f"No SearchFieldMapping for category '{self.category}'")

        return q, info