-- fails if (pickup_borough, payment_method, pickup_hour) is not unique in mart_payment_mix
select pickup_borough, payment_method, pickup_hour, count(*) as row_count
from {{ ref('mart_payment_mix') }}
group by 1, 2, 3
having count(*) > 1
