# Airbnb feature menu

Snapshot **2026-09-20**; **20,651 source rows**, 90 detailed-listing columns. Generated from hash-verified inputs by scripts/review_features.py. Coverage here is source-wide, not the modeling cohort; typed review coverage and cohort exclusions are in the [experiment results](../specs/002-review-features/development-results.json).

## Choices for neighborhood comparable research

| Group | Available fields | Current use / owner choice |
| --- | --- | --- |
| Property and capacity | Property/room type, bedrooms, beds, accommodates (sleeps) | Current model; distinct property and room groups |
| Geography | Approximate latitude/longitude, source neighborhoods; derived Census ZCTA | ZCTA model category and buffered geographic evaluation |
| Guest ratings | Overall, accuracy, cleanliness, check-in, communication, location, value | Added to selectable review experiment; value also tested separately |
| Review history | Total reviews, last 12 months, last 30 days, previous year, reviews/month | Added to selectable review experiment; not bookings or occupancy |
| Bathrooms | Numeric bathrooms and shared/private bathroom description | Available; deferred by owner pending this audit |
| Amenities | Source amenity list, potential pool/hot-tub/kitchen/parking indicators | Available; not yet encoded; deferred by owner |
| Stay/booking rules | Minimum/maximum nights and forward restrictions, instant booking | Current stay cohort uses minimum nights; additional predictors deferred |
| Availability | 30/60/90/365-day and end-of-year availability | Candidate only; unavailable does not mean booked |
| Review timing | First and last review dates | Candidate recency/establishment measures; not yet encoded |
| Host operational attributes | Superhost flag, response/acceptance rates, listing counts | Source fields exist but current research allowlist omits them; a separate private-use decision is required. Host values cannot be published. |
| Lot size, living area, condition, renovation cost | Not provided as structured fields in this source | Property-source/owner-assumption work remains separate |

The owner chose **review features first**. Candidate means available for consideration, not developer approval or an implemented predictor. Use the [custom feature command](../specs/002-review-features/quickstart.md) to choose review inputs explicitly. Scores characterize existing comps, not guaranteed results from renovation. Review-count weighting and review-based comp filters are not implemented here; counts are ordinary selectable model inputs.

## Complete source catalog

`current` = existing input directly or via a derived group. `review_experiment` = selectable now. `candidate` = available but not implemented. Other roles explain why a field is metadata, target-related, estimated or restricted. Only field names and aggregate coverage are shown; no host/reviewer values, free text or source records are published.

| Source field | Present | Missing | Role | Interpretation |
| --- | ---: | ---: | --- | --- |
| `accommodates` | 20,651 | 0 | current | Existing model input, directly or through property/stay grouping. |
| `amenities` | 20,651 | 0 | candidate | Physical/amenity feature; parsing and shared/private semantics require owner review. |
| `availability_30` | 20,651 | 0 | candidate | Calendar availability, not confirmed bookings; future research only. |
| `availability_365` | 20,651 | 0 | candidate | Calendar availability, not confirmed bookings; future research only. |
| `availability_60` | 20,651 | 0 | candidate | Calendar availability, not confirmed bookings; future research only. |
| `availability_90` | 20,651 | 0 | candidate | Calendar availability, not confirmed bookings; future research only. |
| `availability_eoy` | 20,651 | 0 | candidate | Calendar availability, not confirmed bookings; future research only. |
| `bathrooms` | 0 | 20,651 | candidate | Physical/amenity feature; parsing and shared/private semantics require owner review. |
| `bathrooms_text` | 20,503 | 148 | candidate | Physical/amenity feature; parsing and shared/private semantics require owner review. |
| `bedrooms` | 20,639 | 12 | current | Existing model input, directly or through property/stay grouping. |
| `beds` | 20,135 | 516 | current | Existing model input, directly or through property/stay grouping. |
| `calculated_host_listings_count` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `calculated_host_listings_count_entire_homes` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `calculated_host_listings_count_private_rooms` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `calculated_host_listings_count_shared_rooms` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `calendar_last_scraped` | 20,651 | 0 | provenance | Identifier/link/scrape metadata; not a predictor. |
| `calendar_updated` | 0 | 20,651 | provenance | Identifier/link/scrape metadata; not a predictor. |
| `description` | 20,598 | 53 | restricted | Text/images excluded from this experiment; may expose personal or identifying details. |
| `estimated_occupancy_l365d` | 20,651 | 0 | source_estimate | Provider estimate, not observed bookings/revenue; excluded from model inputs. |
| `estimated_revenue_l365d` | 17,456 | 3,195 | source_estimate | Provider estimate, not observed bookings/revenue; excluded from model inputs. |
| `first_review` | 14,560 | 6,091 | candidate | Review dates could support age/recency features; not occupancy labels. |
| `has_availability` | 20,538 | 113 | candidate | Calendar availability, not confirmed bookings; future research only. |
| `host_about` | 11,598 | 9,053 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_acceptance_rate` | 0 | 20,651 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_has_profile_pic` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_id` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_identity_verified` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_is_superhost` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_listings_count` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_location` | 14,769 | 5,882 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_name` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_neighbourhood` | 0 | 20,651 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_picture_url` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_profile_id` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_profile_url` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_response_rate` | 0 | 20,651 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_response_time` | 0 | 20,651 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_since` | 0 | 20,651 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_thumbnail_url` | 0 | 20,651 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_total_listings_count` | 0 | 20,651 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_url` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `host_verifications` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `hosts_time_as_host_months` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `hosts_time_as_host_years` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `hosts_time_as_user_months` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `hosts_time_as_user_years` | 20,651 | 0 | restricted | Not retained by the current research allowlist; host values cannot be published. Separate private-use decision required. |
| `id` | 20,651 | 0 | provenance | Identifier/link/scrape metadata; not a predictor. |
| `instant_bookable` | 0 | 20,651 | candidate | Booking setting; future feature choice. |
| `last_review` | 14,560 | 6,091 | candidate | Review dates could support age/recency features; not occupancy labels. |
| `last_scraped` | 20,651 | 0 | provenance | Identifier/link/scrape metadata; not a predictor. |
| `latitude` | 20,651 | 0 | geographic_input | Approximate coordinates derive ZCTA/buffers; not parcel matching or direct model inputs. |
| `license` | 6,967 | 13,684 | restricted | Reported license is not verified legal eligibility; excluded. |
| `listing_url` | 20,651 | 0 | provenance | Identifier/link/scrape metadata; not a predictor. |
| `longitude` | 20,651 | 0 | geographic_input | Approximate coordinates derive ZCTA/buffers; not parcel matching or direct model inputs. |
| `maximum_maximum_nights` | 20,517 | 134 | candidate | Stay restriction, not observed occupancy; future feature choice. |
| `maximum_minimum_nights` | 20,517 | 134 | candidate | Stay restriction, not observed occupancy; future feature choice. |
| `maximum_nights` | 20,517 | 134 | candidate | Stay restriction, not observed occupancy; future feature choice. |
| `maximum_nights_avg_ntm` | 20,651 | 0 | candidate | Stay restriction, not observed occupancy; future feature choice. |
| `minimum_maximum_nights` | 20,517 | 134 | candidate | Stay restriction, not observed occupancy; future feature choice. |
| `minimum_minimum_nights` | 20,517 | 134 | candidate | Stay restriction, not observed occupancy; future feature choice. |
| `minimum_nights` | 20,517 | 134 | current | Existing model input, directly or through property/stay grouping. |
| `minimum_nights_avg_ntm` | 20,651 | 0 | candidate | Stay restriction, not observed occupancy; future feature choice. |
| `name` | 20,651 | 0 | restricted | Text/images excluded from this experiment; may expose personal or identifying details. |
| `neighborhood_overview` | 0 | 20,651 | restricted | Text/images excluded from this experiment; may expose personal or identifying details. |
| `neighbourhood` | 0 | 20,651 | candidate | Source neighborhood context; differs from Census ZCTA and verified legal jurisdiction. |
| `neighbourhood_cleansed` | 20,651 | 0 | candidate | Source neighborhood context; differs from Census ZCTA and verified legal jurisdiction. |
| `neighbourhood_group_cleansed` | 0 | 20,651 | candidate | Source neighborhood context; differs from Census ZCTA and verified legal jurisdiction. |
| `number_of_reviews` | 20,651 | 0 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `number_of_reviews_l30d` | 20,651 | 0 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `number_of_reviews_ltm` | 20,651 | 0 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `number_of_reviews_ly` | 20,651 | 0 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `picture_url` | 20,651 | 0 | restricted | Text/images excluded from this experiment; may expose personal or identifying details. |
| `price` | 17,456 | 3,195 | target | Advertised price; prediction target, not a predictor or realized revenue. |
| `price_quote_checkin_date` | 18,589 | 2,062 | target_related | Price-derived quote; excluded as a predictor to avoid predicting price from price. |
| `price_quote_checkout_date` | 18,589 | 2,062 | target_related | Price-derived quote; excluded as a predictor to avoid predicting price from price. |
| `price_quote_price_per_night` | 17,388 | 3,263 | target_related | Price-derived quote; excluded as a predictor to avoid predicting price from price. |
| `price_quote_raw` | 18,589 | 2,062 | target_related | Price-derived quote; excluded as a predictor to avoid predicting price from price. |
| `price_quote_total_price` | 17,388 | 3,263 | target_related | Price-derived quote; excluded as a predictor to avoid predicting price from price. |
| `property_type` | 20,651 | 0 | current | Existing model input, directly or through property/stay grouping. |
| `review_scores_accuracy` | 14,560 | 6,091 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `review_scores_checkin` | 14,558 | 6,093 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `review_scores_cleanliness` | 14,560 | 6,091 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `review_scores_communication` | 14,560 | 6,091 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `review_scores_location` | 14,558 | 6,093 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `review_scores_rating` | 14,560 | 6,091 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `review_scores_value` | 14,558 | 6,093 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `reviews_per_month` | 14,560 | 6,091 | review_experiment | Selectable review experiment input; scores/counts describe established rentals. |
| `room_type` | 20,651 | 0 | current | Existing model input, directly or through property/stay grouping. |
| `scrape_id` | 20,651 | 0 | provenance | Identifier/link/scrape metadata; not a predictor. |
| `source` | 3,051 | 17,600 | provenance | Identifier/link/scrape metadata; not a predictor. |
