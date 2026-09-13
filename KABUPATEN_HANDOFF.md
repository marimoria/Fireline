# Kabupaten/Kota Drill-Down — Phase 11 Handoff

## Current status

The kabupaten/kota drill-down data path is complete through dashboard artifact generation.

The single working notebook is:

`notebooks/07_FIRELINE_Kabupaten_Drilldown.ipynb`

## Canonical administrative model

The five GeoJSON files in `data/additions` provide 56 valid kabupaten/kota features.

```text
kode_prov → province_code
provinsi  → province_name
kode_kk   → kabupaten_code
kab_kota  → kabupaten_name
```

All geometries use EPSG:4326 and passed validity checks.

## Attribution rules

Each grid-day is assigned to a kabupaten using its representative observed point.

The grid is not split at administrative boundaries. Attribution status is retained as:

```text
assigned
boundary_ambiguous
unmatched
```

The existing grid-day priority score remains unchanged.

## Population context

Population values are normalized to people and joined to all 56 kabupaten/kota records.

Name normalization includes administrative aliases and formatting variants such as:

- `KotawaringinTimur` → `Kotawaringin Timur`
- `Palangka Raya` → `Palangkaraya`
- `Kota Banjar Baru` → `Kota Banjarbaru`
- `Kota Baru` → `Kotabaru`
- city names with or without the `Kota` prefix

Population is contextual metadata only. It does not affect priority scores, rankings, or P1/P2/P3 levels.

Population density remains unavailable where the source did not provide it.

## Main outputs

- `review_outputs/kabupaten_admin_lookup.csv`
- `review_outputs/grid_day_kabupaten_attribution.csv`
- `review_outputs/kabupaten_day_summary.csv`
- `review_outputs/kabupaten_day_enriched.csv`
- `review_outputs/kabupaten_population_context.csv`
- `review_outputs/kabupaten_dashboard_payload.json`
- `review_outputs/FIRELINE_Priority_Map.html`

## Dashboard contract

Payload version:

```text
kabupaten-drilldown-1.0
```

The intended navigation is:

```text
Date → Province → Kabupaten/kota → Grid area
```

Filtering limits displayed rows only. It does not recalculate the score percentile universe.

No data must be presented as “no selected area” or “data unavailable,” never as proof that an area is safe.

## Reproducibility

Run the notebook from the project environment. It regenerates validation outputs, the dashboard payload, and the portable HTML artifact. Each meaningful milestone is saved in local Git history.

Latest checkpoint before this handoff: Phase 10 dashboard artifact integration.
