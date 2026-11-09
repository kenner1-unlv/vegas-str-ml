# Source audit and research decisions

Audited 2026-11-08 from the public [Inside Airbnb catalog](https://insideairbnb.com/get-the-data/)
and locally downloaded detailed `listings.csv.gz` archives under ignored `data/raw/multi-city/`.
Clark County used the existing ignored archive. All four URLs and headers were checked live;
all four local archives were streamed to compute the aggregate counts below. These are
**source** counts, not normalized usable cohort sizes or model results.

| Market/source area | Snapshot | Rows | Missing `price` | Missing overall rating | Hotel-room rows | Archive bytes | SHA-256 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Clark County, NV | 2026-09-20 | 20,651 | 3,195 | 6,091 | 330 | 10,743,024 | `98bf79593638dc0f8638cd538ec9293efb65cd9af01b5f34f335e2ea9e371cb1` |
| New York City, NY | 2026-09-14 | 29,918 | 10,512 | 8,114 | 463 | 16,005,851 | `a67bf574e47aa6eba5b2262987dbd9684f206d5cd0183470056f9c936b8e7ae1` |
| Los Angeles, CA | 2026-09-14 | 43,781 | 7,094 | 10,845 | 412 | 26,795,298 | `83de2cb0188c058a839cc0533bef3d2725b59c51ac7e83c049dc2e2c69edf1bf` |
| Nashville, TN | 2026-09-19 | 10,133 | 814 | 1,296 | 73 | 6,053,738 | `cb528c862fd11ced99eafd2d8d6e21a1f0918e082388299cccde7061a791b24b` |

The first private normalization retained 17,456 Clark County, 19,406 NYC, 36,687 LA and
9,319 Nashville rows with a parsed positive price and valid coordinates: **82,868 of
104,483 source rows**. The 21,615 exclusions all have a missing asking price in these
snapshots. These are broad source-area cohorts, not final modeling cohorts; further
feature and geographic support rules are pending. NYC excludes 10,512 of 29,918 rows,
so selection bias is a material cross-market limitation. Extreme positive advertised
rates remain in the private cohort for diagnosis rather than being silently capped.
The [aggregate source audit](source-audit.json) records all 90 columns' missing counts,
selected field statuses, source room support, price tails and candidate spatial support.
Two local normalization runs on the same pinned inputs produced byte-identical private
rows and private audits for all four markets. This checks repeatability on the current
Windows environment, not across all platforms. No model training or final evaluation
has run.

Detailed source URLs:

- Clark County: https://data.insideairbnb.com/united-states/nv/clark-county-nv/2026-09-20/data/listings.csv.gz
- New York City: https://data.insideairbnb.com/united-states/ny/new-york-city/2026-09-14/data/listings.csv.gz
- Los Angeles: https://data.insideairbnb.com/united-states/ca/los-angeles/2026-09-14/data/listings.csv.gz
- Nashville: https://data.insideairbnb.com/united-states/tn/nashville/2026-09-19/data/listings.csv.gz

Each archive has 90 columns with the same header SHA-256
`061445eae4bb06f8e0275de05af3ea20c2205078f98f350709debefc99a84cd1`.
The [source manifest](source-manifest.json) records explicit successful local retrieval
events on 2026-11-09 UTC for the three new markets. Clark County retains the earlier
retrieval timestamp from its verified private manifest. Retrieval and provider snapshot
dates are distinct.
Core fields `id`, `last_scraped`, `price`, `room_type`, `property_type`, `bedrooms`,
`beds`, `accommodates`, coordinates and selected review fields are present. No duplicate
listing IDs or malformed nonempty prices were found by the preliminary scan; this does not
replace full row validation. Source `last_scraped` values span multiple days around each
catalog snapshot date; retain both values rather than silently equating them. All four have
Entire home/apt, Private room, Shared room and Hotel room. Nashville has only seven source
Shared room rows and 73 Hotel room rows; subgroup inference will be limited.

## Decisions and limits

1. Use the four owner-approved areas as source markets. Clark County is not a Las Vegas city
   boundary; public copy must call it Clark County/Las Vegas Valley where appropriate.
2. The main target is positive, parseable advertised USD nightly price. Missing target rows
   remain in the private source audit but cannot be supervised training examples. Do not cap
   high prices merely for convenience. Report target missingness and cohort selection by city.
3. Source hotel-room labels remain distinct. No separate hotel dataset is necessary.
4. The current catalog HTML exposes only the listed September 2026 snapshots for these areas.
   Do not promise temporal evaluation until a separately sourced, licensed, hashed later
   snapshot is available. The historical Las Vegas Phase 3 final holdout is already inspected.
5. Use development geography for model and feature selection. Freeze new city/geographic
   final partitions before fitting in NYC, LA and Nashville; never reuse tuning-fold scores
   as final evidence. This same-snapshot Clark County data is historical/development only.
6. Review ratings/counts describe established listings. They are optional predictors only
   after prediction-time availability and leakage review. Counts are not bookings.
7. The [Inside Airbnb policy](https://insideairbnb.com/data-policies/) describes current
   public downloads as CC BY 4.0 and asks users not to republish its dataset. Keep source
   tables local. Public research outputs require provider, market/date, source/license links,
   modification notes and a reviewed field/granularity contract.

## Remaining source checks before training

- Recheck source policy and URL at each deliberate download, record retrieval UTC time and
  hash, and verify full row-level fields and missing/invalid statuses by market.
- Audit market-specific property labels, price tails, geographic support and source-date
  consistency; document exclusions without fitting encoders on all rows.
- Obtain later snapshots deliberately if temporal generalization becomes a release claim;
  do not infer bookings from calendar availability or review counts.
