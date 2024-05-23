import sys
sys.path.append('./modules')
import gcloud_modules as gc
from typing import Dict
import threading
import pandas as pd
import time

START_DATE = "2023-05-15"
END_DATE = "2024-05-22"
CURRENCY = "USD"
SALES_CHANNEL = "Amazon.com"
RESULTS: Dict[str,pd.DataFrame] = {}
FALSE_PROMOS: list = [
    'off any','off for non-prime customers','AB DEX Incentives',
    'ABMarketing:','ABMktg','Acquisition Promotion for Prime Day',
    'ADEX','AFD Base Promo','Discover PAGE','EFF Promotion',
    'Exports Free Shipping','FAP offer','First App purchase',
    'Free Delivery On First Order','Free Same Day','Free Sub SameDay',
    'PAGE-Venmo','PD21 BXGY','PROD_','Project Diamond','AB Incentives',
    'SameDay US','Promo Propensity','TDU Promotion',
    'US Core Free Shipping','USAA PAGE','User Activation Promotion',
    'Venmo-Maple','UNK']

def pull_bigquery(query: str, name: str) -> None:
    start = time.perf_counter()
    print(f'Reading {name}')
    with gc.gcloud_connect() as client:
        result = client.query(query).result().to_dataframe()
    RESULTS[name] = result
    print(f'Succesfully pulled {name} in {time.perf_counter() - start:.2f} seconds')
    return None

def apply_false_promos(series: pd.Series, FALSE_PROMOS: list):
    return any(part in series for part in FALSE_PROMOS)


def gather_data() -> None:
    promo_query = f'''SELECT DATE(shipment_date, "America/Los_Angeles") as date,
                    item_promotion_discount, item_promotion_id, description, amazon_order_id, shipment_item_id
                    FROM `auxillary_development.promotions`
                    WHERE DATE(shipment_date, "America/Los_Angeles") BETWEEN DATE("{START_DATE}") AND DATE("{END_DATE}")
                    AND
                    currency = "{CURRENCY}"'''
    afo_query = f'''SELECT amazon_order_id,shipment_item_id, DATE(TIMESTAMP(purchase_date),"America/Los_Angeles") as purchase_date,
                    merchant_sku as sku, shipped_quantity,item_price,item_promo_discount
                    FROM `auxillary_development.amazon_fulfilled_orders`
                    WHERE currency = "{CURRENCY}" and sales_channel = "{SALES_CHANNEL}"
                    AND
                    DATE(TIMESTAMP(purchase_date),"America/Los_Angeles") BETWEEN DATE("{START_DATE}") AND DATE("{END_DATE}")
                    '''
    dict_query  = f'''SELECT *
                    FROM `auxillary_development.dictionary`'''
    threads = []
    for data in [(promo_query,'promos'), (afo_query,'afo'), (dict_query,'dictionary')]:
        threads.append(threading.Thread(target=pull_bigquery, args = data))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return None

def process_data():
    gather_data()
    promos: pd.DataFrame = RESULTS['promos']
    afo: pd.DataFrame = RESULTS['afo']
    dictionary: pd.DataFrame = RESULTS['dictionary']

    promos['promocode'] = promos['description'].str.extract(r'(\b[A-Z0-9-]{8,12}\b)')
    promos['false_promo'] = promos['description'].apply(lambda x: apply_false_promos(x,FALSE_PROMOS))
    shipment_id_mapping = afo[['shipment_item_id','sku','shipped_quantity','item_price','item_promo_discount']].copy()

    promo_mapping = pd.Series(promos['description'].values, index = promos['item_promotion_id']).to_dict()
    false_promos = pd.Series(promos['false_promo'].values, index = promos['item_promotion_id']).to_dict()
    false_promo_cols = [key for key, value in false_promos.items() if value]
    true_promo_cols = [key for key, value in false_promos.items() if not value]


    promos_pivot = promos.pivot(index = ['shipment_item_id','amazon_order_id'], columns = 'item_promotion_id', values = 'item_promotion_discount').reset_index()
    promos_pivot['real_promos_discount'] = promos_pivot[true_promo_cols].sum(axis = 1)
    promos_pivot['fake_promos_discount'] = promos_pivot[false_promo_cols].sum(axis = 1)

    promos_pivot = promos_pivot[['shipment_item_id','amazon_order_id','real_promos_discount','fake_promos_discount'] + true_promo_cols + false_promo_cols]

    promos_pivot = promos_pivot.rename(columns = promo_mapping)

    promos_total = pd.merge(shipment_id_mapping, promos_pivot, how = 'right', on = 'shipment_item_id')
    promos_total = promos_total.dropna(subset = 'sku')

    with pd.ExcelWriter(r'c:\temp\pics\test.xlsx', engine='xlsxwriter') as writer:
        print('Exporting promos total')
        promos_total.to_excel(writer, sheet_name='promos', index=False)
        print('Exporting afo')
        # afo.to_excel(writer, sheet_name='afo', index=False)
        print('dictionary')
        dictionary.to_excel(writer, sheet_name='dictionary', index=False)
        print('Exporting promos')
        promos.to_excel(writer, sheet_name = 'promos_raw', index = False)

# pull_bigquery(test_query,'test')
# test = RESULTS['test']
# print(test.duplicated().sum())
process_data()