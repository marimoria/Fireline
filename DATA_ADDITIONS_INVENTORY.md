# Phase 1 — Data Additions Inventory

Generated from the files in `data/additions` on 13 September 2026.

## Boundary inventory

| Province | Features | Geometry | CRS | Invalid/empty geometries | Administrative fields |
|---|---:|---|---|---:|---|
| Kalimantan Barat | 14 | MultiPolygon | EPSG:4326 | 0 / 0 | `kode_kk`, `kode_prov`, `kab_kota`, `provinsi` |
| Kalimantan Selatan | 13 | MultiPolygon | EPSG:4326 | 0 / 0 | `kode_kk`, `kode_prov`, `kab_kota`, `provinsi` |
| Kalimantan Tengah | 14 | MultiPolygon | EPSG:4326 | 0 / 0 | `kode_kk`, `kode_prov`, `kab_kota`, `provinsi` |
| Kalimantan Timur | 10 | MultiPolygon | EPSG:4326 | 0 / 0 | `kode_kk`, `kode_prov`, `kab_kota`, `provinsi` |
| Kalimantan Utara | 5 | MultiPolygon | EPSG:4326 | 0 / 0 | `kode_kk`, `kode_prov`, `kab_kota`, `provinsi` |

Total: 56 kabupaten/kota features.

The boundary files already provide a stable-looking administrative code in `kode_kk`. The observed values follow province prefixes such as `61.xx`, `62.xx`, `63.xx`, `64.xx`, and `65.xx`. The implementation should validate uniqueness and province consistency before using this field as the canonical kabupaten ID.

All files are WGS84 (`EPSG:4326`) and contain valid, non-empty `MultiPolygon` geometries in the current validation pass.

Other properties present in every file are `fid`, `nama`, and `label`. They are not yet designated as analytical fields.

## Population inventory

| File | Format | Apparent coverage | Important observations |
|---|---|---|---|
| `Jumlah Penduduk menurut Kabupaten_Kota di Provinsi Kalimantan Timur, 2024.csv` | CSV | Kabupaten/kota in Kalimantan Timur | Population is expressed in thousands; header has a two-row title structure. |
| `Jumlah Penduduk Menurut Kabupaten_Kota, 2024.csv` | CSV | Province-level Kalimantan totals | This is not kabupaten-level data; it should not be joined to kabupaten boundaries. |
| `Penduduk, ... di Provinsi Kalimantan Selatan, 2024.csv` | CSV | Kabupaten/kota in Kalimantan Selatan | Includes population, growth, population share, density, and sex ratio. |
| `Penduduk, ... di Provinsi Kalimantan Utara, 2024.csv` | CSV | Kabupaten/kota in Kalimantan Utara | Includes population, growth, population share, density, and sex ratio. |
| `jumlah-penduduk-menurut-kabupaten-kota-di-provinsi-kalimantan-tengah-ribu-2020-2025(1).xlsx` | XLSX | Kabupaten/kota in Kalimantan Tengah | One sheet; includes 2020, 2024, and 2025 population in thousands. Requires header-row normalization. |

No kabupaten-level population file for Kalimantan Barat was identified in this directory. The generic CSV contains province totals and must not be treated as a substitute.

## Canonical field decisions for the next phase

Boundary fields:

```text
province_code  <- kode_prov
province_name  <- provinsi
kabupaten_code <- kode_kk
kabupaten_name <- kab_kota
geometry       <- geometry
```

Population fields should eventually normalize to:

```text
population
population_density
population_year
population_source
```

Population values expressed in thousands must be converted to people and retain the original unit/source in metadata.

## Known limitations and follow-ups

1. The population sources use different layouts and units, so they require separate parsing rules before joining.
2. The generic 2024 CSV is province-level and should be excluded from kabupaten enrichment.
3. Kalimantan Barat currently has boundary data but no matching kabupaten-level population input in this folder.
4. Names still need normalization and join-coverage validation against `kode_kk`.
5. Boundary geometries are valid, but spatial assignment tests for border points have not yet been run.
6. File SHA-256 fingerprints and full machine-readable details are stored in `review_outputs/phase1_data_inventory.json`.

## Phase 1 acceptance result

The files are sufficiently understood to proceed to the canonical administrative model and boundary loader. Population enrichment should remain optional until the normalization and coverage checks are implemented.
