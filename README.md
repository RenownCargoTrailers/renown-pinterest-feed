# Renown Pinterest Feed

Daily (10:00 UTC) rebuild of the Pinterest product catalog from renowncargotrailers.com (read-only WooCommerce Store API).
Skips items with no price, no photo, or links that redirect.

Feed: https://renowncargotrailers.github.io/renown-pinterest-feed/renown_pinterest_feed.csv

## Meta (Facebook) Vehicles catalog feed
Feed: https://renowncargotrailers.github.io/renown-pinterest-feed/renown_meta_vehicle_feed.csv
Built daily by build_meta.py (Commerce Manager > Vehicles catalog > Data feed > Scheduled URL). Skips: docs/meta_skipped.json

## Microsoft Merchant Center (Bing Shopping) feed
Feed: https://renowncargotrailers.github.io/renown-pinterest-feed/renown_bing_feed.txt
Tab-delimited TXT, rebuilt daily by the same build.py workflow. Same in-stock inventory as the Pinterest feed, excluding items without a Microsoft-supported image (jpg/png/gif/bmp/tiff) or a price greater than 0. Uses google_product_category 4044 (Utility & Cargo Trailers) and identifier_exists=FALSE (trailers have no GTIN). Prices are the current website prices.
