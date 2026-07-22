with trips as (
    select * from {{ ref('int_trips_enriched') }}
),

by_group as (
    select
        pickup_borough,
        payment_method,
        pickup_hour,
        count(*)                  as total_trips,
        round(avg(tip_amount), 2) as avg_tip_usd,
        round(avg(tip_pct), 4)    as avg_tip_pct
    from trips
    group by 1, 2, 3
)

select
    pickup_borough,
    payment_method,
    pickup_hour,
    total_trips,
    avg_tip_usd,
    avg_tip_pct,
    round(
        total_trips / sum(total_trips) over (partition by pickup_borough, pickup_hour), 4
    ) as payment_share
from by_group
order by pickup_borough, pickup_hour, payment_method
