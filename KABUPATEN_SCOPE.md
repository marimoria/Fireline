# Kabupaten/Kota Drill-Down — Phase 0 Scope

Status: agreed implementation scope for the next phases.

## Objective

Extend the current province-level FIRELINE view with a more detailed kabupaten/kota view while preserving the existing grid-day priority model.

## Geographic hierarchy

```text
Kalimantan
└── Province
    └── Kabupaten/kota
        └── Grid area
            └── Satellite observations
```

The dashboard should support navigation from a broad administrative scope to a specific grid area.

## Scope decisions

1. The five kabupaten/kota GeoJSON files in `data/additions` become the intended primary boundary source.
2. The existing grid-day score remains unchanged.
3. Kabupaten/kota values are aggregations and navigation aids; they are not new fire-risk scores.
4. Population is contextual metadata only. It does not affect activity, persistence, intensity, priority score, or priority level.
5. The representative observation point remains the basis for assigning a grid-day to a kabupaten/kota.
6. A grid crossing an administrative boundary is not split. Its assignment must be deterministic and visibly qualified when ambiguous.
7. Missing data must be shown as “tidak tersedia” or “tidak ada area terpilih”; it must never be presented as safe or risk-free.
8. Existing province-level totals, grid scores, and Top 10 results must remain unchanged after the feature is added.

## Target navigation

The dashboard will support these filters and transitions:

```text
Tanggal → Provinsi → Kabupaten/kota → Area grid → Detail area
```

- Selecting a province limits the kabupaten/kota choices.
- Selecting a kabupaten/kota zooms the map and limits grid results to that area.
- Clicking a kabupaten/kota polygon selects the same area as the dropdown.
- Clearing the kabupaten/kota selection returns to the selected province view.
- Clicking a grid marker continues to open the existing grid-level detail view.
- Reset restores the default date and the all-province scope.

## Kabupaten/kota summary

At a selected date, the kabupaten/kota view should expose these contextual metrics:

- total satellite detections
- number of active grid areas
- number of P1, P2, and P3 grid areas
- highest grid priority score
- average grid priority score
- median valid FRP
- latest observation time
- seven-day activity context
- population, when the population join is available

These metrics must be labeled as summaries of grid areas. They must not be described as an independently calibrated kabupaten risk score.

## Score semantics

The existing score remains relative to all active Kalimantan grid areas on the same date:

```text
score = 40% activity + 35% persistence + 25% intensity
```

Filtering by province or kabupaten/kota must not silently recalculate the score against only the filtered area.

The UI should distinguish:

- grid priority score: existing analytical score
- highest grid score: maximum score among grids in the kabupaten/kota
- average grid score: descriptive aggregation only
- P1/P2/P3 count: count of grid areas in each existing category

## Empty and exceptional states

The implementation must explicitly handle:

- kabupaten/kota with no detections on the selected date
- dates with no data
- representative points outside all kabupaten polygons
- points on or near shared boundaries
- missing population data
- unavailable map tiles or Leaflet assets
- incomplete early seven-day windows

None of these states should be interpreted as proof that no fire exists or that an area is safe.

## Phase 0 acceptance criteria

Phase 0 is complete when:

- the hierarchy is documented;
- the boundary source decision is recorded;
- score and population responsibilities are separated;
- grid-to-kabupaten attribution semantics are defined;
- the intended filter and click behavior is defined;
- empty-state behavior is defined;
- regression expectations are documented.

No pipeline, data, or UI implementation is included in this phase.
