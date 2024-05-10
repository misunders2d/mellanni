


def read_sql(query):
    with gc.gcloud_connect() as client:
        data = client.query(query).result().to_dataframe()
    return data




promo_query = f'''SELECT DATE(shipment_date, "America/Los_Angeles") AS shipment_date,
            item_promotion_discount, description, shipment_item_id, amazon_order_id
            FROM `reports.promotions`
            WHERE DATE(shipment_date, "America/Los_Angeles") >= "2024-01-01"
            '''
            
afo_query = f'''SELECT amazon_order_id, shipment_item_id, merchant_sku, shipped_quantity,
                item_price, item_promo_discount
                FROM `auxillary_development.amazon_fulfilled_orders`
                WHERE DATE(PARSE_TIMESTAMP("%Y-%m-%dT%H:%M:%S%Ez", shipment_date),"America/Los_Angeles") >= "2024-01-01"
                '''




data1 = read_sql(promo_query)
afo = read_sql(afo_query)

sku_stats = afo.groupby('merchant_sku')[['shipped_quantity', 'item_price', 'item_promo_discount']].agg('sum').reset_index()

sku_mapping = afo[['shipment_item_id', 'merchant_sku']]
data1 = pd.merge(data1, sku_mapping, how = 'left', on = 'shipment_item_id')

sku_data = data1.groupby(
    ['merchant_sku','description'])[
      ['item_promotion_discount']
      ].agg({'item_promotion_discount':'sum'}).reset_index().sort_values('merchant_sku')


fbm_promos = data1[~data1['shipment_item_id'].isin(afo['shipment_item_id'].unique().tolist())]['shipment_item_id'].unique().tolist() 