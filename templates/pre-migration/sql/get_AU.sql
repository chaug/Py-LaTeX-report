with
{{# local.queries }}
-- ------- {{name}} SUB QUERY -------
( {{> AU_cabin.sql }} ) as {{name}}_AUS
{{# last }}-- ---------------------{{/ last }}{{^ last }},{{/ last }}
{{/ local.queries }}
    select
        *
    from
        LEGACY_AUS
    left outer join
        SHADOW_AUS using (NETWORK,CABIN_CODE,BOOKING_CLASS_CODE)
