select
    NETWORK
from
    KPI_SAT_NETWORK
where
    AIRLINE_CODE = '{{airline}}'
    {{ network_sql_condition }}
