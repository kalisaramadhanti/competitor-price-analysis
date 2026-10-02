WITH platforms AS (

    SELECT DISTINCT platform
    FROM {{ ref('stg_competitor_products') }}
    WHERE platform IS NOT NULL

)

SELECT
    MD5(platform) AS platform_id,
    platform AS platform_name

FROM platforms