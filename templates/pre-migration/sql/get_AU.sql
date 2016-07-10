select
    NETWORK,
    CABIN_CODE,
    BOOKING_CLASS_CODE,
    avg(AUTHORISATION_LEVEL) as AU
from
    KPI_FACT_BOOKING_CLASS
join
    KPI_SAT_NETWORK using ('AIRLINE_CODE','FLIGHT_NUMBER','FLIGHT_DATE')
where
    AIRLINE_CODE        = '{{airline}}'
    and PHASE           = '{{phase}}'
    and EXTRACTION_DATE = '{{ed:%d-%b-%Y}}'
    -- and NETWORK not in ('EXCLUDED')
group by
    NETWORK,
    CABIN_CODE,
    BOOKING_CLASS_CODE
