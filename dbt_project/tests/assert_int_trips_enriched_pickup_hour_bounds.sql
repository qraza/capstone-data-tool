-- edge case: extract(hour from ...) must always land in the valid 0-23 range,
-- guarding against a timestamp parsing/timezone regression upstream
select *
from {{ ref('int_trips_enriched') }}
where pickup_hour is null
   or pickup_hour < 0
   or pickup_hour > 23
