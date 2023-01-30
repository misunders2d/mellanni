# -*- coding: utf-8 -*-
"""
Created on Fri May  6 15:15:51 2022

@author: djoha
"""
import streamlit as st
import os
import pandas as pd
from io import BytesIO
from PIL import Image
from modules import formatting as ff


def process_file(xray, reviews):
    price_col = [x for x in xray.columns.tolist() if 'price' in x.lower()][0]
    fee_col = [x for x in xray.columns.tolist() if 'fees' in x.lower()][0]
    if isinstance(reviews,pd.core.frame.DataFrame) == False:# or reviews == None:
        columns_to_drop = [
            'Product Details','Revenue','Active Sellers #','Images',
            'Review velocity','Buy Box','Category','Size Tier','Fulfillment',
            'Dimensions','Weight','Creation Date'
           ]
        recolumns = [
            'ASIN','Review Count','',' ','  ','   ','Sales','Total Sales',
            'Brand',price_col,'BSR',fee_col,'Ratings'
            ]

        xray['Sales'] = xray['Sales'].replace('n/a',0)
        xray['Sales'] = xray['Sales'].astype(str)
        xray['Sales'] = xray['Sales'].str.replace('\xa0','')
        xray['Sales'] = xray['Sales'].str.replace(',','').astype(float)
        xray['Total Sales'] = xray['Sales'].copy()
        xray[['',' ','  ','   ']] = ''
        xray = xray[recolumns]

        for c in columns_to_drop:
            try:
                del xray[c]
            except:
                pass
        return xray
    else:
        total_reviews = sum(reviews['Review Count'])
        reviews = reviews[reviews['ASIN'] != 'Unattributed'].reset_index()
        reviews.sort_values('Review Count', ascending = False)
        variations = reviews['Description'].str.split('\|', expand = True).fillna('no name')
        columns = [variations[i].str.split(':',expand = True).fillna('no name')[0][0].strip() for i in variations.columns]
        col_names = ['column1','column2','column3','column4']
        for i,j in enumerate(col_names):
            try:
                globals()[j] = columns[i]
            except:
                globals()[j] = f'Default col{i+1}'
        columns = [column1,column2,column3,column4]

        for i,j in enumerate(col_names):
            try:
                reviews[globals()[j]] = variations[i].str.split(':',expand = True)[1].str.strip()
            except:
                try:
                    reviews[globals()[j]] = variations[i].str.split(':',expand = True)[0].str.strip()
                except:
                    reviews[globals()[j]] = ''
        columns.sort(reverse = True)
        reviews = reviews.sort_values('Review Count', ascending = False)
        asin = reviews['ASIN'].values[0]
            
        xray['Sales'] = xray['Sales'].replace('n/a',0)
        xray['Sales'] = xray['Sales'].astype(str)
        xray['Sales'] = xray['Sales'].str.replace('\xa0','')
        xray['Sales'] = xray['Sales'].str.replace(',','').astype(float)
        sales = max(xray['Sales'])
        reviews['Sales'] = round(reviews['Review Count'] / total_reviews * sales,0)
        reviews['Total Sales'] = sales
        reviews = reviews[['ASIN','Review Count', column1,column2,column3,column4,'Sales', 'Total Sales']]
        reviews = reviews.sort_values('Sales', ascending=False)
        columns_to_drop = [
            'Product Details','Sales','Revenue','Active Sellers #','Images',
            'Review velocity','Buy Box','Category','Size Tier','Fulfillment',
            'Dimensions','Weight','Creation Date','Review Count'
            ]
        for c in columns_to_drop:
            del xray[c]
        reviews = pd.merge(reviews, xray, how = 'outer', on = 'ASIN').fillna(0)
        try:
            reviews['Avg. Price'] = round(sum(reviews[price_col]*reviews['Sales'])/sum(reviews['Sales']),2)
        except:
            reviews['Avg. Price'] = 'undefined'

        return reviews

def read_files(xray_file, reviews_file = None):
    check, reviews = False, None
    xray = pd.read_csv(xray_file).fillna(0)
    if all(['Product Details' in xray.columns,'ASIN' in xray.columns,'Brand' in xray.columns]):
        check = True
        brand = xray['Brand'].values[0]
        st.session_state.brand_area.text_area('Brand in file:',brand)
    else:
        return xray, reviews, check
    if reviews_file != None:
        reviews = pd.read_csv(reviews_file).fillna(0)
        if all(['Review Count' in reviews.columns,'Review Share' in reviews.columns]):
            check = True
    return xray, reviews, check

def get_asins(links):
    import re
    asins = []
    for l in links:
        asin = re.search('([A-Z0-9]{10})',l).group()
        if asin not in asins:
            asins.append(asin)
    return asins

def main_estimator():
    # st.header("This tool is designed to assess variation sales based on H10's Xray and review downloads")
    col1, col2 = st.columns(2)
    st.session_state.brand_area = col1.empty()
    col2_area = col2.empty()
    links_area = col2_area.text_area('Input links with ASINs to extract ASINs only')
    links = links_area.split('\n')
    if col2.button('Extract ASINs') and len(links) > 0:
        asins = get_asins(links)
        col2_area.text_area('Extracted ASINs:','\n'.join(asins))

    with st.expander('First, upload necessary files'):
        if st.checkbox('Show example'):
            st.image('media/xray_guide.png')
        xray_file = st.file_uploader('Xray file from H10 (mandatory)', type = '.csv')
        if st.checkbox('Add review file'):
            if st.checkbox('Show example', key = 'review_example'):
                st.image('media/review_guide.png')            
            reviews_file = st.file_uploader('Review file from H10 (optional)', type = '.csv')
        else:
            reviews_file = None

    if st.button('Process file(s)'):
        xray, reviews, check = read_files(xray_file, reviews_file)
        if check:
            final = process_file(xray,reviews)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                final.to_excel(writer, sheet_name = 'Sales', index = False)
                ff.format_header(final, writer, 'Sales')
            st.download_button('Download results',output.getvalue(), file_name = 'variation_sales.xlsx')
        else:
            st.warning('Wrong files selected')

    with st.expander('If needed, upload the completed research for further analysis (feature coming)'):
        research_file = st.file_uploader('Cleaned and refined research file')
        pass

    return None



if __name__ == '__main__':
    main_estimator()