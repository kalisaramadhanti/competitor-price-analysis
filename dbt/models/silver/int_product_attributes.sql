WITH products AS (

    SELECT DISTINCT
        normalised_name
    FROM {{ ref('int_product_normalisation') }}

),

extracted AS (

    SELECT
        normalised_name,

        CASE
            WHEN normalised_name ~ '^dove\y'
                THEN 'Dove'
            WHEN normalised_name ~ '^lifebuoy\y'
                THEN 'Lifebuoy'
            WHEN normalised_name ~ '^sunsilk\y'
                THEN 'Sunsilk'
            ELSE 'Unknown'
        END AS brand,

        REGEXP_MATCH(
            normalised_name,
            '([0-9]+(?:[.,][0-9]+)?)\s*(ml|kg|g|l)\y'
        ) AS pack_size_match

    FROM products

),

attributes AS (

    SELECT
        normalised_name,
        brand,

        pack_size_match[1] || pack_size_match[2]
            AS pack_size_raw,

        REPLACE(pack_size_match[1], ',', '.')::NUMERIC
            AS pack_size_value,

        pack_size_match[2]
            AS pack_size_unit,

        CASE
            WHEN pack_size_match[2] = 'l'
                THEN REPLACE(pack_size_match[1], ',', '.')::NUMERIC * 1000

            WHEN pack_size_match[2] = 'ml'
                THEN REPLACE(pack_size_match[1], ',', '.')::NUMERIC

            WHEN pack_size_match[2] = 'kg'
                THEN REPLACE(pack_size_match[1], ',', '.')::NUMERIC * 1000

            WHEN pack_size_match[2] = 'g'
                THEN REPLACE(pack_size_match[1], ',', '.')::NUMERIC

            ELSE NULL
        END AS pack_size_normalized_value,

        CASE
            WHEN pack_size_match[2] IN ('ml', 'l')
                THEN 'ml'

            WHEN pack_size_match[2] IN ('g', 'kg')
                THEN 'g'

            ELSE NULL
        END AS pack_size_normalized_unit

    FROM extracted

)

SELECT *
FROM attributes