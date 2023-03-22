import streamlit as st
import pandas as pd
import re
from io import BytesIO
from modules import formatting as ff
import login
from modules import gcloud_modules as gc
st.session_state['login'], st.session_state['name'] = login.login()
name_area = st.empty()
col1, col2 = st.columns([10,3])

if st.session_state['login']:
    name_area.write(f"Welcome {st.session_state['name']}")

    with col2:
        @st.cache_data(show_spinner=False)
        def pull_dictionary():
            client = gc.gcloud_connect()
            sql = '''SELECT * FROM `auxillary_development.dictionary`'''
            query_job = client.query(sql)  # Make an API request.
            dictionary = query_job.result().to_dataframe()
            client.close()
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                dictionary.to_excel(writer, sheet_name = 'Dictionary', index = False)
                ff.format_header(dictionary,writer,'Dictionary')
            return output.getvalue()
        
        if col2.checkbox('Dictionary'):
            dictionary = pull_dictionary()
            st.download_button('Download dictionary',dictionary, file_name = 'Dictionary.xlsx')


    with col1:
        with st.expander('Link generator for Seller Central'):
            result = []

            def review_links():
                for a in asin_list:
                    link = 'https://www.amazon.com/product-reviews/'+a+'/ref=cm_cr_arp_d_viewopt_fmt?sortBy=recent&pageNumber=1&formatType=current_format'
                    result.append(link)
                return result
                    
            def sc_links():
                for a in asin_list:
                    link = 'https://sellercentral.amazon.com/inventory/ref=xx_invmgr_dnav_xx?tbla_myitable=sort:%7B%22sortOrder%22%3A%22ASCENDING%22%2C%22sortedColumnId%22%3A%22skucondition%22%7D;search:'+a+';pagination:1;'
                    result.append(link)
                return result

            def pdp_links():
                for a in asin_list:
                    link = 'https://www.amazon.com/dp/'+a
                    result.append(link)
                return result

            def check_prices():
                client = gc.gcloud_connect()
                sql = '''SELECT asin, item_name, price FROM `auxillary_development.inventory_report`'''
                query_job = client.query(sql)  # Make an API request.
                inventory = query_job.result().to_dataframe()
                client.close()
                inventory_asin = inventory[inventory['asin'].isin(asin_list)]
                inventory_asin[inventory_asin.columns] = inventory_asin[inventory_asin.columns].astype('str')
                # result = (inventory_asin['asin']+' - '+ inventory_asin['price'] + ' - ' + inventory_asin['item_name']).tolist()
                return inventory_asin

            def edit_links():
                client = gc.gcloud_connect()
                sql = '''SELECT ASIN,SKU FROM `auxillary_development.dictionary`'''
                query_job = client.query(sql)  # Make an API request.
                dictionary = query_job.result().to_dataframe()
                client.close()
                for a in asin_list:
                    dict_asin = dictionary[dictionary['ASIN'] == a]
                    sku = dict_asin['SKU'].tolist()[0]
                    link = f'https://sellercentral.amazon.com/abis/listing/edit?marketplaceID=ATVPDKIKX0DER&ref=xx_myiedit_cont_myifba&sku={sku}&asin={a}&productType=HOME_BED_AND_BATH#product_details'
                    result.append(link)
                return result
                
            def fix_stranded_inventory():
                for a in asin_list:
                    # dict_asin = dictionary[dictionary['ASIN'] == a]
                    link = 'https://sellercentral.amazon.com/inventory?viewId=STRANDED&ref_=myi_ol_vl_fba&tbla_myitable=sort:%7B%22sortOrder%22%3A%22DESCENDING%22%2C%22sortedColumnId%22%3A%22date%22%7D;search:'+a+';pagination:1;'
                    result.append(link)
                return result
                    
            def order_links():
                for a in asin_list:
                    link = 'https://sellercentral.amazon.com/orders-v3/search?page=1&q='+a+'&qt=asin'
                    result.append(link)
                return result
            
            functions = {
                '1 - review links':review_links,
                '2 - Seller Central links':sc_links,
                '3 - Product Detail Page links':pdp_links,
                '4 - Check prices in Inventory file':check_prices,
                '5 - Seller Central Edit links':edit_links,
                '6 - Fix Stranded Inventory links':fix_stranded_inventory,
                '7 - Order links':order_links
                }

            asins = re.split(r'\n|,| ',st.text_area('Input ASINs'))
            options = [x for x in functions.keys()]
            option = st.selectbox('Select an option',options)
            if st.button('Run'):
                asin_list = [x for x in asins if x != ""]
                func = functions[option]
                result = func()
                if isinstance(result,pd.core.frame.DataFrame):
                    result = result.reset_index().drop('index', axis = 1)
                st.experimental_data_editor(result)

        with st.expander('Business report link generator'):
            from datetime import datetime, timedelta
            e_date = (datetime.now().date()-timedelta(days = 2))
            s_date = (e_date-timedelta(days = 10))
            start = st.date_input('Starting date', value = s_date)
            end = st.date_input('End date', value = e_date)
            numdays = (e_date - s_date).days + 1
            date_range = [e_date - timedelta(days = x) for x in range(numdays)]
            link_list = []
            for d in date_range:
                link = f"https://sellercentral.amazon.com/business-reports/ref=xx_sitemetric_dnav_xx#/report?id=102%3ADetailSalesTrafficBySKU&chartCols=&columns=0%2F1%2F2%2F3%2F4%2F5%2F6%2F7%2F8%2F9%2F10%2F11%2F12%2F13%2F14%2F15%2F16%2F17%2F18%2F19%2F20%2F21%2F22%2F23%2F24%2F25%2F26%2F27%2F28%2F29%2F30%2F31%2F32%2F33%2F34%2F35%2F36%2F37&fromDate={d.strftime('%Y-%m-%d')}&toDate={d.strftime('%Y-%m-%d')}"
                link_list.append(link)
                full_list = '  \n  \n'.join(link_list)
            if st.button('Generate'):
                st.text_area('Generated links',full_list)

        with st.expander('Pricelist checker'):
            import pandas as pd
            import numpy as np
            
            def linspace(df,steps):
                result = np.linspace(df['Standard Price'],df['MSRP'],steps)
                return result

            def add_steps(file_path, steps):
                file = pd.read_excel(file_path, usecols = ['Collection','SKU', 'ASIN', 'Size', 'Color', 'Standard Price', 'MSRP'])
                file['steps'] = file.apply(linspace, steps = steps+1, axis = 1)
                
                for i in range(0,steps+1):
                    file[f'step {i}'] = file['steps'].apply(lambda x: round(x[i],2))
                for i in range(0,steps):
                    file[f'% {i+1}'] = file[f'step {i+1}'] / file[f'step {i}'] - 1
                del file['steps']
                del file['step 0']
                return file

        with st.expander('Backend checker'):
            import json
            def process_backend(files):
                to_df = []
                for file in files:
                    file = file.getvalue()
                    result = json.loads(file.decode('utf-8'))
                
                    kw_fields = [x for x in result['detailPageListingResponse'].keys() if 'keyword' in x.lower()]
                    if not kw_fields:
                        break
                    asin = result['detailPageListingResponse']['asin']['value']
                    try:
                        brand = result['detailPageListingResponse']['brand#1.value']['value']
                    except:
                        try:
                            brand = result['detailPageListingResponse']['brand']['value']
                        except:
                            brand = 'Unknown'
                    platinum = [x for x in result['detailPageListingResponse'].keys() if 'platinum' in x.lower()]
                    pkw = []
                    for p in platinum:
                        pkw.append(result['detailPageListingResponse'][p]['value'])
                    pkw = ' '.join(pkw)
                    try:
                        size = result['detailPageListingResponse']['size#1.value']['value']
                    except:
                        size = result['detailPageListingResponse']['size_name']['value']
                    try:
                        color = result['detailPageListingResponse']['color#1.value']['value']
                    except:
                        color = result['detailPageListingResponse']['color_name']['value']
                    try:
                        kws = result['detailPageListingResponse']['generic_keyword#1.value']['value']#.split(' ')
                    except:
                        kws = result['detailPageListingResponse']['generic_keywords']['value']#.split(' ')
                    try:
                        title = result['detailPageListingResponse']['item_name#1.value']['value']
                    except:
                        title = result['detailPageListingResponse']['item_name']['value']
                    to_df.append([asin, brand, size, color, kws, pkw,title])
                df = pd.DataFrame(to_df,columns = ['asin','brand','size','color','kws','platinum kws','title'])
                return df

            market = st.radio('Select marketplace',['USA','CA'],horizontal = True)
            data_area = st.empty()
            button_area = st.empty()
            but1,but2,but3 = button_area.columns([1,1,1])
            if market == 'USA':
                link = 'https://sellercentral.amazon.com/abis/ajax/reconciledDetailsV2?asin='
            elif market == 'CA':
                link = 'https://sellercentral.amazon.ca/abis/ajax/reconciledDetailsV2?asin='
            asins = data_area.text_area('Input ASINs to parse').split('\n')
            if but1.button('Get links'):
                st.session_state['asins'] = True
                data_area.text_area('Links:','\n'.join(link+asin for asin in asins))
            if 'asins' in st.session_state:
                files = st.file_uploader('Upload files', type = '.json', accept_multiple_files= True)
                if files:
                    final = process_backend(files)
                    st.write(final)
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        final.to_excel(writer, sheet_name = 'KW', index = False)
                        ff.format_header(final, writer, 'KW')
                    st.download_button('Download results',output.getvalue(), file_name = 'backend.xlsx')
            if but3.button('Reset') and 'asins' in st.session_state:
                del st.session_state['asins']
