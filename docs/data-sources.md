# Data sources and provenance

Inside Airbnb source-file and Census audit: October 8, 2026 Pacific. Housing and regulatory research below was checked October 7; those sources have not been freshly revalidated by the geography work. Snapshot dates are distinct from retrieval dates.

## Inside Airbnb

[Get the Data](https://insideairbnb.com/get-the-data/) supplies **Clark County, NV, 2026-09-20**. Credit Inside Airbnb and [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); our filtering, private research allowlist and derived geography are modifications. Consult its [policies](https://insideairbnb.com/data-policies/) and [assumptions](https://insideairbnb.com/data-assumptions/) before changing interpretation.

Source base: https://data.insideairbnb.com/united-states/nv/clark-county-nv/2026-09-20/

All seven supplied files are downloaded in ignored data/raw/2026-09-20/. Detailed listings and source polygons were retrieved October 7 Pacific; the other five files October 8. The manifest records each exact URL, UTC retrieval time, bytes and SHA-256. Its public copy contains provenance only, not raw rows.

| Source path below base | Private local filename | Rows / features | Bytes | Purpose |
| --- | --- | ---: | ---: | --- |
| data/listings.csv.gz | listings.csv.gz | 20,651 rows | 10,743,024 | Detailed listing characteristics; current asking-price target |
| data/calendar.csv.gz | calendar.csv.gz | 7,537,733 rows | 18,168,245 | Availability and minimum/maximum stay research |
| data/reviews.csv.gz | reviews.csv.gz | 744,753 rows | 71,471,251 | Private source archive; reviewer identity/text excluded from research feature table |
| visualisations/listings.csv | listings-summary.csv | 20,651 rows | 3,908,942 | Redundant summary, not extra observations |
| visualisations/reviews.csv | reviews-summary.csv | 744,753 rows | 18,554,934 | Listing ID/date summary, not extra reviews |
| visualisations/neighbourhoods.csv | neighbourhoods.csv | 7 rows | 163 | Broad source label list |
| visualisations/neighbourhoods.geojson | neighbourhoods.geojson | 7 features | 677,305 | Valid Polygon/MultiPolygon source areas |

The calendar's actual header is listing_id,date,available,minimum_nights,maximum_nights. **This snapshot has no calendar price column.** Do not claim date-specific rates, realized earnings or confirmed bookings from it. Summary files must not be concatenated with their detailed equivalents.

### Relevant field coverage

Detailed listings already contained richer fields than the public explorer. Private data/research/2026-09-20/listing-features.csv retains string source values for ID, coordinates, asking price, room type, property type, bedrooms, beds, accommodates, numeric bathrooms, bathroom description, amenities, minimum/maximum nights and source neighborhood. Empty values stay empty; this is a candidate research table, not normalized training data. Host/reviewer fields and review text are excluded. coverage.json audits headers, row counts and empty-value counts for every downloaded CSV.

| Field | Empty values / 20,651 source rows | Research implications |
| --- | ---: | --- |
| property_type, room_type, accommodates | 0 each | Property type helps distinguish hotel/resort inventory from residential comparables; room type alone is insufficient |
| bedrooms | 12 | Keep unknown separate; zero bedrooms is not missing |
| beds | 516 | Distinct from bedrooms; do not silently substitute |
| bathrooms (numeric) | 20,651 | Unusable as supplied in this snapshot |
| bathrooms_text | 148 | Candidate for reviewed parsing; private/shared bathroom semantics must survive normalization |
| amenities | 0 empty strings | Nonempty JSON can still be an empty list; vocabulary/encoding remains future work |
| minimum_nights | 134 | Review stay-length cohorts before calling every listing short term |
| price | 3,195 | Missing targets excluded from current public sample |
| neighbourhood, neighbourhood_group_cleansed | 20,651 each | No finer named neighborhood can simply be recovered from these fields |

These counts use the full source, not the retained comparison sample. A nonempty field is not evidence of correctness or comparable property quality. Source ratings and activity measures remain in the raw archive; whether to use them requires prediction-time availability and leakage review. Do not infer lot size, renovation quality, horse-property status, property purchase cost or occupancy from these files.

### Public artifacts and refresh commands

Base listings.json remains schema version 1 with 17,212 usable rows: string ID, rounded approximate coordinates, asking price, room type, bedrooms and original source neighborhood. It is 2,809,128 bytes; source boundaries.geojson is 677,108 bytes. quality.json, manifest.json and index.json complete the base release. No raw CSV, host/reviewer information, review text or private research features are deployed.

Source label counts: Unincorporated Areas 13,490; City of Las Vegas 2,119; City of North Las Vegas 800; City of Henderson 784; Boulder City 15; Nellis AFB 4. These labels are not verified parcel/municipal assignments.

From repository root, after uv sync --project pipeline --locked:

~~~powershell
# Network ingestion: download all seven files; publish only the existing base allowlist.
uv run --project pipeline python pipeline/ingest.py --snapshot 2026-09-20 --all
# Verify manifest hashes and regenerate base artifacts without network.
uv run --project pipeline python pipeline/ingest.py --snapshot 2026-09-20 --offline
# Private candidate features and complete-source coverage audit; no model.
uv run --project pipeline python scripts/audit_sources.py --snapshot 2026-09-20
~~~

Default ingestion downloads only detailed listings and source polygons. --calendar / --reviews remain optional; --all adds the supporting tables too. Raw and research directories are ignored. The audit requires all seven filenames in the manifest before writing anything; incomplete default/optional downloads fail with an instruction to rerun --all. It then verifies every checksum. The audit deliberately streams full CSVs locally; CI never downloads them. Reprocessing resets the index to the base release: rebuild ZCTA enrichment below before building/deploying an enriched release. Do not run processing inside a live serving directory.

## Census ZIP-area research layer

[Census ZCTAs](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html) approximate the geographic distribution of ZIP codes; they are not USPS address verification, named neighborhoods or regulatory jurisdictions. Use source-qualified identity census:2020:zcta:{five-digit code} in future models/joins; the current sidecar carries the vintage and string codes separately.

Source: [Census 2020 TIGERweb ZCTA layer 2](https://tigerweb.geo.census.gov/arcgis/rest/services/Census2020/PUMA_TAD_TAZ_UGA_ZCTA/MapServer/2), January 1, 2020 vintage, WGS84 output. The pinned query retrieves complete polygons intersecting the existing study bounding box, not clipped polygons. October 8 retrieval returned 66 valid features; an independent returnCountOnly query also returned 66. U.S. Census Bureau attribution is displayed. The raw response and checksum manifest are private under data/raw/geography/; the public geography provenance contains their URL, date, byte size, hash and expected count.

~~~powershell
# First retrieval or deliberate geography refresh: pinned 2020 source, completeness validation.
uv run --project pipeline python scripts/build_geography.py --snapshot 2026-09-20 --download
# Rebuild from previously downloaded, checksum-verified source.
uv run --project pipeline python scripts/build_geography.py --snapshot 2026-09-20
node scripts/check_geography.mjs
~~~

geography.json is an optional schema-version-1 sidecar, SHA-256 pinned to the exact base listing bytes. Its allowlisted assignment rows contain only string ID, five-digit ZCTA or null, assigned/ambiguous/unassigned status and a boolean near_boundary. index.json declares enrichment only after both outputs are written. The frontend rejects snapshot/hash mismatches, missing/duplicate IDs and invalid assignments. It preserves original source neighborhoods.

Only exactly one covering polygon is assigned; shared edges or overlaps stay ambiguous and unmatched points are retained. Current counts: **17,211 assigned, one unmatched, zero ambiguous; 61 represented ZCTAs**. All base records remain available. Source coordinates were rounded to five decimals by base ingestion; that does not correct anonymization.

Inside Airbnb reports approximate displacement up to 150 m and independently scattered locations within buildings. **Dots cannot identify a specific house; do not apply a uniform directional shift or join to parcels.** A regional equirectangular distance approximation at latitude 36.15 flags assigned points within approximately 150 m of their polygon edge: **3,614 flagged**. This is an optional sensitivity exclusion, not a guaranteed true-location confidence radius; unflagged points are not certified correct. Full source geometry is used for assignment and distance checks. Public map outlines are simplified with topology preservation at 0.00001 degrees for display, not assignment.

ZIP-area tables use the same active room-type, exact-bedroom, source-area, ZCTA, price and edge filters as the map and listing browser. Medians below n=20 are withheld in this table; counts remain visible. Twenty is a display-support threshold, not a significance test. Overall filtered median remains descriptive. No outliers are removed. Mixed property types, platform selection, missing targets and clustered/multiunit inventory remain confounders. This first layer does not implement a matched-comparable algorithm or ML.

## Housing acquisition costs — unresolved

No housing-price data is ingested or displayed. Accessibility does not establish redistribution rights. Before integration, record the exact release, earliest/latest dates, nonempty Clark County coverage, geographic identifier mappings, applicable terms, update schedule and benchmark-to-property limitations.

| Candidate | Coverage / geography / dates | Access and license status | Limitations and next step |
| --- | --- | --- | --- |
| [Zillow Research ZHVI](https://www.zillow.com/research/data/) | Historical monthly series across multiple regional levels and housing segments. [Source description](https://www.zillow.com/research/contact-us/) lists county, city, ZIP and neighborhood coverage; individual Las Vegas-area series and latest CSV dates remain to verify. | Free research downloads; [general terms](https://www.zillow.com/corporate/terms-of-use/) are not an explicit open-data license. Obtain/confirm terms applicable to this public application before redistribution. | Modeled typical value, not a transaction price or exact acquisition quote. [Methodology](https://www.zillow.com/research/zhvi-methodology/) uses neural Zestimates. Candidate first regional benchmark only after licensing and coverage checks. |
| [Redfin Data Center](https://www.redfin.com/news/data-center/) / [downloads](https://www.redfin.com/news/data-center/downloads/) | National housing market releases, including weekly/monthly trackers and property-type comparisons. Clark County/city/ZIP availability, suppression and latest rows need file-level inspection. | Public downloadable releases; copyright and Terms of Use apply. No permissive redistribution license confirmed in this review. | Closed-sale medians vary with composition and sparse sales; cannot attach a regional median to one listing as its purchase price. Confirm selected geography, period, sample counts and reuse terms. |
| [Clark County NV Assessor transaction lookup](https://maps.clarkcountynv.gov/assessor/AssessorParcelDetail/ParcelSales.aspx?instance=pcl2&parcel=12624612037) | Local parcel transaction dates/prices and nearby sales, including 2026 records in inspected examples. Bulk historical coverage and refresh cadence unresolved. | Public lookup verified; bulk export/API and redistribution permissions not confirmed. Avoid scraping owner information. | Separate recorded sale price from assessed/taxable value. Screen transfers, distressed and non-arm-length transactions. Approximate rental coordinates cannot support definitive parcel joins. Investigate authorized bulk sales access. |
| [FHFA HPI](https://www.fhfa.gov/data/hpi) | Public price-change indexes; national/state/metro/county/ZIP/tract products with history from the mid-1970s for some products. Dates and coverage vary. | Government downloadable series; verify selected product reuse/attribution notices at integration. | Index measures price changes, not dollar acquisition costs; unsuitable as a purchase-price substitute. Can contextualize date adjustments once a dollar benchmark exists. |

Proposed next milestone: validate licensing and actual geographic coverage for ZHVI and Redfin, then select one regional benchmark with type/date alignment. If permission or coverage fails, keep cost fields absent and request a user-provided purchase-price scenario rather than inventing a benchmark.

## Regulatory context by jurisdiction

These are dated source pointers, checked October 7, 2026; the application does not encode eligibility rules. Confirm the current ordinance, parcel jurisdiction, zoning, licensing and HOA conditions independently.

- [City of Las Vegas](https://www.lasvegasnevada.gov/Business/Planning-Zoning/Code-Enforcement/Short-Term-Rentals): its licensing guidance addresses owner occupancy and local eligibility conditions.
- [Unincorporated Clark County](https://www.clarkcountynv.gov/business/doing_business_with_clark_county/divisions/regulated_business/short_term_rentals/): distinct county application/license process under Chapter 7.100.
- [Henderson](https://www.cityofhenderson.com/government/departments/community-development-and-services/short-term-vacation-rentals): annual STVR registration and local regulations.
- [North Las Vegas](https://www.cityofnorthlasvegas.com/business/short-term-rentals): conditional-use approval before business licensing, per the city page.

An Airbnb listing is not evidence of a valid license. Legal jurisdiction is not synonymous with postal city, source neighborhood, or approximate map point.

## Private comparable-data normalization

The [Phase 1 contract](../specs/001-comparable-price-baseline/data-model.md) and [reproduction guide](../specs/001-comparable-price-baseline/quickstart.md) define scripts/normalize_research.py. It rechecks all seven archive hashes, verifies the existing usable cohort/geographic join, preserves allowlisted source strings and creates ignored normalized.json with typed characteristics and audit. Only [aggregate evidence](../specs/001-comparable-price-baseline/phase1-audit.json) is published. It adds no public capacity/property/stay fields and trains no model.
