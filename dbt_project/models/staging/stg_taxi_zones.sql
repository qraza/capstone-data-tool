with source as (
    select * from {{ source('nyc_tlc', 'taxi_zones') }}
),

cleaned as (
    select
        LocationID      as location_id,
        Borough         as borough,
        Zone            as zone_name,
        service_zone
    from source
)

select * from cleaned
