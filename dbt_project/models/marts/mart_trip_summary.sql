with trips as (
    select * from {{ ref('stg_yellow_trips') }}
),

zones as (
    select * from {{ ref('stg_taxi_zones') }}
),

daily_zone_stats as (
    select
        cast(pickup_at as date)             as trip_date,
        pickup_location_id,
        count(*)                            as total_trips,
        round(avg(trip_distance), 2)        as avg_distance_miles,
        round(avg(trip_duration_minutes), 1) as avg_duration_minutes,
        round(avg(fare_amount), 2)          as avg_fare_usd,
        round(avg(tip_amount), 2)           as avg_tip_usd,
        round(sum(total_amount), 2)         as total_revenue_usd,
        round(avg(passenger_count), 1)      as avg_passengers
    from trips
    group by 1, 2
)

select
    s.trip_date,
    s.pickup_location_id,
    z.zone_name                             as pickup_zone,
    z.borough                               as pickup_borough,
    s.total_trips,
    s.avg_distance_miles,
    s.avg_duration_minutes,
    s.avg_fare_usd,
    s.avg_tip_usd,
    s.total_revenue_usd,
    s.avg_passengers
from daily_zone_stats s
left join zones z
    on s.pickup_location_id = z.location_id
order by s.trip_date, s.total_trips desc
