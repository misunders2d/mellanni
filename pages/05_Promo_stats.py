import sys
sys.path.append('./modules')
import gcloud_modules as gc
import pandas as pd

CUTOFF = "2024-05-10"

def pull_bigquery(query: str) -> pd.DataFrame:
    with gc.gcloud_connect() as client:
        result = client.query(query).result().to_dataframe()
    return result

promo_query = f'''SELECT DATE(shipment_date, "America/Los_Angeles") as date,
                  item_promotion_discount, description, amazon_order_id, shipment_item_id
                  FROM `reports.promotions`
                  WHERE DATE(shipment_date, "America/Los_Angeles") >= DATE("{CUTOFF}")
                  AND
                  currency = "USD"
                  LIMIT 10'''
test_query = f'''SELECT *
                 FROM `auxillary_development.amazon_fulfilled_orders`
                 LIMIT 10'''
test = pull_bigquery(test_query)
print(test)
