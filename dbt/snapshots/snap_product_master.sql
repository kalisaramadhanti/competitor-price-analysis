{% snapshot snap_product_master %}

{{
    config(
        target_schema='snapshots',
        unique_key='product_id',
        strategy='check',
        check_cols=[
            'canonical_product_name',
            'brand',
            'category',
            'pack_size_raw'
        ],
        invalidate_hard_deletes=True
    )
}}

SELECT
    product_id,
    product_matching_key,
    canonical_product_name,
    brand,
    category,
    pack_size_raw
FROM {{ ref('dim_product_master') }}

{% endsnapshot %}