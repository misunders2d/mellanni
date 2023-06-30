# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 12:46:22 2022

@author: Sergey
"""

import os
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account


def gcloud_connect():
    key_path = service_account.Credentials.from_service_account_info(st.secrets['gcp_service_account'])
    client = bigquery.Client(credentials = key_path)
    return client

def list_projects():
    client = gcloud_connect()
    projects = [x.project_id for x in client.list_projects()]
    sections = [x.dataset_id for x in client.list_datasets()]
    table_list = {section:[x.table_id for x in client.list_tables(section)] for section in sections}
    client.close()
    return table_list

def push_dictionary():
    import pandas as pd
    dict_path = mm.get_db_path('US')[1]
    d = pd.read_excel(dict_path)
    new_cols = [x.replace(' ','_').replace('-','_').replace('?','') for x in d.columns]
    d.columns = new_cols
    d['Launch_date'] = d['Launch_date'].astype('str')
    client = gcloud_connect('US')
    d.to_gbq('auxillary_development.dictionary', if_exists = 'replace')
    client.close()
    return None
    
def gcloud_daterange(client,
                     report = 'auxillary_development',
                     table = 'business_report',
                     start = None,
                     end = None,
                     columns = '*'):
    if isinstance(columns, list):
        cols = '`'+'`,`'.join(columns)+'`'
    else:
        cols = columns
    if any([start is None, end is None]):
        query = f'''
        SELECT {cols}
        FROM `{report}.{table}`'''
    else:
        query = f'''
        SELECT {cols}
        FROM `{report}.{table}`
        WHERE date >= "{start}"
        AND date <= "{end}"'''
    query_job = client.query(query)  # Make an API request.
    data = query_job.result().to_dataframe()
    client.close()
    return data

def get_last_date(client,report = 'reports',table = 'business_report'):
    date_cols = {
        'all_listing_report': 'date',
        'all_orders': 'purchase_date',
        'fba_inventory': 'date',
        'fba_returns': 'return_date',
        'fee_preview': 'date',
        'inventory': 'Date',
        'promotions': 'shipment_date',
        'storage_fee': 'date',
        'business_report': 'date'
        }
    column = date_cols[table]
    query = f"""
        SELECT {column}
        FROM `{report}.{table}`
        ORDER BY `{column}` DESC
        LIMIT 1
    """
    query_job = client.query(query)  # Make an API request.
    date = query_job.result().to_dataframe().values[0][0] #get results from query
    try:
        date = date.strftime('%Y-%m-%d')
    except:
        pass
    return date