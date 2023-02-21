import streamlit as st
import re
import login
st.session_state['login'] = login.login()

if st.session_state['login']:
    st.write("logged in")
    d_from = st.date_input('Starting date', key = 'db_datefrom')
    d_to = st.date_input('End date', key = 'db_dateto')
    if st.button('Read db'):
        client = gcloud_connect()
        # reports = [x.dataset_id for x in client.list_datasets()]
        data = read_db_cloud(start = d_from, end = d_to)
        client.close()
        st.write(data)



    with st.expander('Link generator for SC'):
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
                link = 'https:www.amazon.com/dp/'+a
                result.append(link)
            return result

        def check_prices():
            client = gcloud_connect()
            sql = '''SELECT asin, price FROM `auxillary_development.inventory_report`'''
            query_job = client.query(sql)  # Make an API request.
            inventory = query_job.result().to_dataframe()
            client.close()
            inventory_asin = inventory[inventory['asin'].isin(asin_list)]
            inventory_asin[inventory_asin.columns] = inventory_asin[inventory_asin.columns].astype('str')
            result = (inventory_asin['asin']+' - '+ inventory_asin['price']).tolist()
            return result

        def edit_links():
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
            st.write('  \n'.join(result))

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