-- edge case: nullif() guards the trip_distance / trip_duration_minutes division,
-- so a zero-duration trip (real in this data, ~4.8k rows) must yield a null
-- speed rather than a divide-by-zero error or a bogus zero/infinite value
select *
from {{ ref('int_trips_enriched') }}
where trip_duration_minutes = 0
  and avg_speed_mph is not null
