import streamlit as st
import pandas as pd
import re
from google.cloud import bigquery #pip install google-cloud-bigquery
from google.oauth2 import service_account
from modules import gcloud_modules as gc

bad_chars = [
    '%off any%',
    '%off for non-prime customers%',
    'AB DEX Incentives%',
    'ABMarketing:%',
    'ABMktg%',
    'Acquisition Promotion for Prime Day',
    'ADEX%',
    'AFD Base Promo%',
    'Discover PAGE%',
    'EFF Promotion%',
    'Exports Free Shipping',
    'FAP offer%',
    'First App purchase%',
    'Free Delivery On First Order%',
    'Free Same Day%',
    'Free Sub SameDay%',
    'PAGE-Venmo%',
    'PD21 BXGY',
    'PROD_%',
    'Project Diamond%',
    '%AB Incentives%',
    'SameDay US%',
    'Promo Propensity%',
    '%VPC-%',
    'TDU Promotion%',
    'US Core Free Shipping%',
    'USAA PAGE%',
    'User Activation Promotion%',
    'Venmo-Maple%'
    ]

ld_promos = [
    'DCMS%', 'Mellanni%'
    ]

negative_filter = bad_chars+ld_promos

@st.cache_data
def read_db_cloud(
    report = 'auxillary_development',
    table = 'Promotions',
    column = 'description',
    code_list = None,
    start = None, end = None,
    negative = True
    ):
    prefix_sql = f'SELECT shipment_date, description, amazon_order_id FROM `{report}.{table}`'
    negative_str = f'WHERE {column} NOT LIKE "'+ f'" AND {column} NOT LIKE "'.join(negative_filter)+'"'

    query = f'{prefix_sql} {negative_str}'
    if code_list:
        if len(code_list) == 1:
            code_str = f' AND {column} LIKE "%{code_list[0]}%"'
        else:
            code_str = f' AND ({column} LIKE "%'+f'%" OR {column} LIKE "%'.join(code_list)+'%")'
        query += code_str
    if all([start is not None, end is not None]):
        start, end = pd.to_datetime(start).date(), pd.to_datetime(end).date()
        date_str = f' AND (shipment_date >= "{start}" AND shipment_date <= "{end}")'
        query += date_str

    client = gc.gcloud_connect()
    query_job = client.query(query)  # Make an API request.
    data = query_job.result().to_dataframe()
    client.close()
    return data

@st.cache_data
def process_data(data):
    return processed_data


end = pd.to_datetime('today')
start = end - pd.to_timedelta(180, 'days')

col1, col2, col3 = st.columns([4,2,1])

d_from = col3.date_input('Starting date', key = 'db_datefrom',value = start )
d_to = col3.date_input('End date', key = 'db_dateto', value = end)


codes = re.split(' |,|\n',col2.text_area('Input codes to search'))
if col2.button('Run'):
    codes = [x for x in codes if x != '']
    with st.spinner('Please wait, pulling information...'):
        if codes == []:
            st.session_state.processed_data = read_db_cloud(code_list = None,start = d_from, end = d_to)
        else:
            st.session_state.data = read_db_cloud(code_list = codes,start = d_from, end = d_to)
            code_pattern = '\(([A-Za-z0-9\s]{8,13})\-{0,1}\d{0,1}\)'
            st.session_state.data['Promo-code'] = st.session_state.data['description'].str.extract(code_pattern).fillna(' ')
            promocodes = st.session_state.data['Promo-code'].unique().tolist()
            st.session_state.processed_data = st.session_state.data[st.session_state.data['Promo-code'].isin(codes)]
        st.write(len(st.session_state.processed_data),st.session_state.processed_data)

