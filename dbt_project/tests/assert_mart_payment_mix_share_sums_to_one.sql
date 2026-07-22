-- fails if payment_share across payment methods doesn't sum to ~1 for a given
-- (pickup_borough, pickup_hour) bucket
select pickup_borough, pickup_hour, round(sum(payment_share), 2) as total_share
from {{ ref('mart_payment_mix') }}
group by 1, 2
having round(sum(payment_share), 2) != 1.0
