# Data sources and provenance

Research checked October 7, 2026. Source dates refer to data snapshots, not retrieval time.

## Inside Airbnb

[Get the Data](https://insideairbnb.com/get-the-data/) lists **Clark County, NV** with snapshot **2026-09-20**. Its [data policies](https://insideairbnb.com/data-policies/) and [assumptions](https://insideairbnb.com/data-assumptions/) should be revisited before methodological changes. The page licenses downloads under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Credit Inside Airbnb, link the license, and identify our filtering/allowlisting as changes.

Verified source base: https://data.insideairbnb.com/united-states/nv/clark-county-nv/2026-09-20/

| File | Path below base | Status |
| --- | --- | --- |
| Detailed listings | data/listings.csv.gz | Retrieved, validated, processed |
| Boundaries | visualisations/neighbourhoods.geojson | Retrieved; seven valid polygon/multipolygon features |
| Detailed calendar | data/calendar.csv.gz | Link verified; optional, not downloaded |
| Detailed reviews | data/reviews.csv.gz | Link verified; optional, not downloaded |

Retrieval occurred October 7 Pacific time (2026-10-08T05:15:57–58 UTC). Raw listings: 10,743,024 bytes; boundaries: 677,305 bytes. The generated manifest records original URLs, snapshot, UTC timestamps, exact bytes and SHA-256 checksums. Raw copies and manifest live in ignored data/raw/2026-09-20/. A public copy of the manifest accompanies the outputs in web/static/data/2026-09-20/. Offline reprocessing verifies every downloaded file checksum.

Public derived artifacts: listings.json (2,809,128 bytes), boundaries.geojson (677,108 bytes), quality.json, manifest.json, and data/index.json. Records expose only string listing ID, rounded approximate coordinates, asking price, room type, bedrooms and source neighborhood. No names, host IDs, license strings, reviews, reviewer data, or listing descriptions are exported.

Source labels in retained records: Unincorporated Areas 13,490; City of Las Vegas 2,119; City of North Las Vegas 800; City of Henderson 784; Boulder City 15; Nellis AFB 4. The seventh boundary has no retained Valley listings. Keep these source labels distinct; do not reinterpret them as authoritative municipal/parcel assignments. Dedicated official jurisdiction boundaries and provenance remain a future dependency.

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
