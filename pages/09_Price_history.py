import streamlit as st
import pandas as pd

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading
from queue import Queue
from google.cloud import bigquery #pip install google-cloud-bigquery
from google.oauth2 import service_account
from modules import gcloud_modules as gc
from modules import formatting as ff
from io import BytesIO


import altair as alt
# from matplotlib import pyplot as plt

st.set_page_config(page_title = 'Price tracker', page_icon = 'media/logo.ico',layout="wide",initial_sidebar_state='collapsed')

chart_area = st.container()

def get_asins(queue,mode = 'mapping'):
    # authorize Google Sheets credentials
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    # creds_file = 'competitor_pricing.json'
    # if not os.path.isfile('competitor_pricing.json'):
    #     creds_file = input('Input path to creds file')#G:\Shared drives\70 Data & Technology\70.03 Scripts\mellanni_2\google-cloud\competitor_pricing.json
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets['gsheets-access'], scope)
    # creds = service_account.Credentials.from_service_account_info(st.secrets['gsheets-access'])
    client = gspread.authorize(creds)
    
    #open Google Sheets sheet
    book = client.open_by_url('https://docs.google.com/spreadsheets/d/12AD3N0eUWXt2YjY64OEJpj8IWRRxZA_Qq5TSZJ0gINQ')
    sheet = book.get_worksheet_by_id(28000141)
    data = pd.DataFrame(sheet.get_all_records(head = 2))
    data['ASIN'] = data['Link'].str.extract('([A-Z0-9]{10})')
    asin_cols = [x for x in data.columns if 'ASIN' in x]
    if mode == 'asins':
        asins = data[asin_cols].values.tolist()
        asins = list(set([asin for asin_list in asins for asin in asin_list]))
        # if '' in asins:
        #     asins.remove('')
        asins = [x.strip() for x in asins if re.search('([A-Z0-9]{10})',x)]
        queue.put(asins)
        return None
    elif mode == 'mapping':
        products = data['Product'].unique().tolist()
        mapping = {}
        for product in products:
            product_asins = data[data['Product'] == product][['ASIN']+asin_cols].values[0].tolist()
            product_asins = [x.strip() for x in product_asins if x != '']
            mapping[product] = product_asins
        queue.put(mapping)
        return None

def get_prices(queue):
        query = 'SELECT datetime, asin, brand, final_price FROM `auxillary_development.price_comparison`'
        client = gc.gcloud_connect()
        query_job = client.query(query)  # Make an API request.
        data = query_job.result().to_dataframe()
        client.close()
        queue.put(data)
        return None

if 'data' not in st.session_state:
# if st.button('Pull data'):

    q1, q2 = Queue(), Queue()
    p1 = threading.Thread(target = get_asins,args = (q1,))
    p2 = threading.Thread(target = get_prices,args = (q2,))
    processes = [p1,p2]
    for process in processes:
        process.start()
    st.session_state.mapping = q1.get()
    st.session_state.prices = q2.get()
    for process in processes:
        process.join()


    # st.session_state.mapping = get_asins()
    # st.session_state.prices = get_prices()
    st.session_state.prices['datetime'] = pd.to_datetime(st.session_state.prices['datetime'])

    st.session_state.df = pd.DataFrame()
    for product,asins in st.session_state.mapping.items():
        temp_file = st.session_state.prices[st.session_state.prices['asin'].isin(asins)]
        temp_file['product'] = product
        st.session_state.df = pd.concat([st.session_state.df,temp_file])
        st.session_state.data = True

if 'data' in st.session_state:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.df.to_excel(writer, sheet_name = 'Prices', index = False)
        ff.format_header(st.session_state.df, writer, 'Prices')
    st.download_button('Export full data',output.getvalue(), file_name = 'Price history.xlsx')

    products = st.session_state.df['product'].unique().tolist()
    product = st.selectbox('Select a product',products)
    f = st.session_state.df[st.session_state.df['product'] == product]
    f['brandasin'] = f['brand'] + ' : ' + f['asin']
    plot_file = f[['datetime','brandasin','final_price']]

    c = alt.Chart(plot_file, title = product).mark_line().encode(
        x = alt.X('datetime:T'),
        y = alt.Y('final_price:Q'), color = alt.Color('brandasin')
        )

    chart_area.altair_chart(c.interactive(),use_container_width=True)#
