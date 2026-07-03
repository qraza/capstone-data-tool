with trips as (
    select * from {{ ref('int_trips_enriched') }}
)

select
    trip_date,
    pickup_location_id,
    pickup_zone,
    pickup_borough,
    count(*)                             as total_trips,
    round(avg(trip_distance), 2)         as avg_distance_miles,
    round(avg(trip_duration_minutes), 1) as avg_duration_minutes,
    round(avg(fare_amount), 2)           as avg_fare_usd,
    round(avg(tip_amount), 2)            as avg_tip_usd,
    round(sum(total_amount), 2)          as total_revenue_usd,
    round(avg(passenger_count), 1)       as avg_passengers
from trips
group by 1, 2, 3, 4
order by trip_date, total_trips desc
