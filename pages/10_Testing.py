import streamlit as st
import numpy as np
import pandas as pd
import time
import re
from io import BytesIO
from modules import formatting as ff

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import nltk
# if nltk.download('all') == False:
#     nltk.download('all')
try:
    from nltk.corpus import stopwords
except:
    nltk.download('all')
finally:
    from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

st.set_page_config(page_title = 'M Tools App', page_icon = 'media/logo.ico',layout="wide",initial_sidebar_state='collapsed')

import login
st.session_state['login'], st.session_state['name'] = login.login()

def text_processing(file):
    cluster_col = 'cluster'
    corpus_col = 'clean kw'
    kw_col = [x for x in ['Search Query', 'Keyword Phrase'] if x in file.columns][0]
    def lemmatize(file, column):
        kw = file[column].values.tolist()
        lemmatizer = WordNetLemmatizer()
        corpus = []
        for i in range(len(kw)):
            r = re.sub('[^a-zA-Z]', ' ', kw[i]).lower().split()
            r = [word for word in r if word not in stopwords.words(['english','spanish'])]
            r = [lemmatizer.lemmatize(word) for word in r]
            r = ' '.join(r)
            corpus.append(r)
        file[corpus_col] = corpus
        return file
    
    def measure_clusters(vectors,bins):
        sims = {'cosine':cosine_similarity(vectors), 'nocosine':vectors.toarray()}
        optimal = 1000000000
        for key,sim in sims.items():
            wcss = []
            for i in bins:
                model = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
                model.fit(sim)
                wcss.append(model.inertia_)
            minimal = min([abs(wcss[i+1]-wcss[i]) for i in range(len(wcss)-1)])
            if minimal < optimal:
                optimal = minimal
                optimal_clusters = [abs(wcss[i+1]-wcss[i]) for i in range(len(wcss)-1)].index(minimal)
                result = [key, optimal_clusters, minimal]
        st.success(f'Found {result[1]} keyword groups')
        return sims[result[0]],result[1], result[0]
    
    def clusterize_keywords(file):
        corpus = file[corpus_col].values.tolist()
        cv = TfidfVectorizer(stop_words=['english','spanish'],ngram_range=(1,3))
        vectors = cv.fit_transform(corpus)
        if len(corpus)<10:
            bins = 3
        elif len(corpus)<=50:
            bins = range(1,4)
        elif len(corpus) > 50:
            bins = range(2,30)
        sim, n_clusters, method = measure_clusters(vectors,bins)
        model = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=300, n_init=10, random_state=0)
        clusters = model.fit_predict(sim)
        return clusters
    def name_groups(file):
        clusters = file[cluster_col].unique().tolist()
        # names = {}
        # for c in clusters:
        #     kws = file[file[cluster_col] == c][kw_col].values.tolist()
        #     kw_list = [w for line in [x.split() for x in kws] for w in line]
        #     counts = pd.DataFrame(kw_list).value_counts()
        #     limit = counts.describe(percentiles = [0.5,0.9])['90%']
        #     counts = counts[counts>=limit].index.tolist()
        #     if len(counts) > 5:
        #         names[c] = ' '.join([x[0] for x in counts[:5]]) + ' +'
        #     else:
        #         names[c] = ' '.join([x[0] for x in counts])
        #     file[cluster_col] = file[cluster_col].replace(names)
        #     file[cluster_col] = file[cluster_col].replace('','other')

        names = {}
        for c in clusters:
            group = file.loc[file[cluster_col] == c][corpus_col]
            vectorizer = TfidfVectorizer()
            X = vectorizer.fit_transform(group)
            names[c] = ' '.join(pd.DataFrame(
                X.toarray(), columns=vectorizer.get_feature_names_out()
                ).sum().sort_values(ascending = False)[:3].index.tolist())
            file[cluster_col] = file[cluster_col].replace(names)
            file[cluster_col] = file[cluster_col].replace('','other')


        return file
    file = lemmatize(file, kw_col)
    clusters = clusterize_keywords(file)
    file[cluster_col] = clusters
    file = name_groups(file)
    del file['clean kw']
    return file

def sqp_analyze(file):
    # bins = [0.4, 0.7]
    # bin_labels = [str(int(x*100))+'%' for x in bins]
    file['Max position for glance views'] = file['Impressions: Total Count'] / file['Search Query Volume']
    file['Max position for glance views'] = file['Max position for glance views'].astype(int)
    file[f'{st.session_state.entity} products per search'] = file[f'Impressions: {st.session_state.entity} Count'] / file['Search Query Volume']
    file[f'{st.session_state.entity} KW triggers'] = 'OK'
    file.loc[file[f'{st.session_state.entity} products per search']<1,[f'{st.session_state.entity} KW triggers']] = 'Lost search'
    file[f'{st.session_state.entity} CTR'] = file[f'Clicks: {st.session_state.entity} Count'] / file[f'Impressions: {st.session_state.entity} Count']
    file['Niche ATC Conversion'] = file['Cart Adds: Total Count'] / file['Clicks: Total Count']
    file[f'{st.session_state.entity} ATC Conversion'] = file[f'Cart Adds: {st.session_state.entity} Count'] / file[f'Clicks: {st.session_state.entity} Count']
    file['KW Conversion'] = file['Purchases: Total Count'] / file['Clicks: Total Count']
    file[f'{st.session_state.entity} Conversion'] = 0
    file.loc[file[f'Purchases: {st.session_state.entity} Count']>0,f'{st.session_state.entity} Conversion'] = file[f'Purchases: {st.session_state.entity} Count'] / file[f'Clicks: {st.session_state.entity} Count'].fillna(0)
    file['Conversion status'] = 'Above average'
    file.loc[file[f'{st.session_state.entity} Conversion']<=file['KW Conversion'],'Conversion status'] = 'Below average'
    file['Sales increase potential'] = 0
    file.loc[file[f'{st.session_state.entity} products per search']<1,'Sales increase potential'] = file[f'Purchases: {st.session_state.entity} Count']/file[f'{st.session_state.entity} products per search']-file[f'Purchases: {st.session_state.entity} Count']
    file.loc[file[f'Purchases: {st.session_state.entity} Count']==0,'Sales increase potential'] = file['Purchases: Total Count']/file['Max position for glance views']
    file['Sales increase potential'] = file['Sales increase potential'].astype(int)
    normalize_cols = ['Search Query Volume','Purchases: Total Count']
    normalized_cols = ['_norm_'+x for x in normalize_cols]
    file[normalized_cols] = MinMaxScaler().fit_transform(file[normalize_cols])
    categorical_cols = ['Search','Sales','Conversion']
    try:
        bins = [0.4, 0.7]
        bin_labels = [str(int(x*100))+'%' for x in bins]
        
        for cat_col, norm_col in list(zip(categorical_cols,normalized_cols+['KW Conversion'])):
            file[cat_col] = pd.cut(
                file[norm_col],
                bins = [-1,
                        file[norm_col].describe(percentiles = bins).loc[bin_labels[0]],
                        file[norm_col].describe(percentiles = bins).loc[bin_labels[1]],
                        1],
                labels = ['low','med','high'],
                duplicates = 'drop'
                )
    except:
        bins = [0.5]
        bin_labels = [str(int(x*100))+'%' for x in bins]
        
        for cat_col, norm_col in list(zip(categorical_cols,normalized_cols+['KW Conversion'])):
            file[cat_col] = pd.cut(
                file[norm_col],
                bins = [-1,
                        file[norm_col].describe(percentiles = bins).loc[bin_labels[0]],
                        1],
                labels = ['low','high'],
                duplicates = 'drop'
                )
    file['KW Conversion'] = round(file['KW Conversion']*100,1)
    return file

def read_file(file_path):
    pd_action = pd.read_csv if '.csv' in file_path.name[-4:] else pd.read_excel
    f = pd_action(file_path, nrows = 20)
    file_path.seek(0)
    if any(['Search Query' in  f.values,'Search Query' in  f.index]):
        skip = 1
    else:
        skip = 0
    st.session_state.info = ', '.join(f.columns.tolist()).replace('[','').replace(']','')
    file = pd_action(file_path, skiprows = skip)
    if any(['ASIN' in x for x in f.columns.tolist()]):
        st.session_state.entity = 'ASIN'
    elif any(['Brand' in x for x in f.columns.tolist()]):
        st.session_state.entity = 'Brand'
    return file

def get_stats(file):
    kw_conversion = round(float(file['Purchases: Total Count'].sum() / file['Clicks: Total Count'].sum())*100,1)#
    brand_conversion = round(float(file[f'Purchases: {st.session_state.entity} Count'].sum() / file[f'Clicks: {st.session_state.entity} Count'].sum())*100,1)#
    niche_ctr = round(float(file['Clicks: Total Count'].sum() / file['Impressions: Total Count'].sum())*100,1)#
    brand_ctr_share = round(float(file[f'Clicks: {st.session_state.entity} Count'].sum() / file[f'Impressions: {st.session_state.entity} Count'].sum())*100,1)#
    total_purchases = int(file['Purchases: Total Count'].sum())#
    brand_purchases = int(file[f'Purchases: {st.session_state.entity} Count'].sum())#
    brand_market_share = round(float(brand_purchases / total_purchases)*100,1)#
    keywords_above_niche = len(file[file['Conversion status']=='Above average'])
    keywords_below_niche = len(file[file['Conversion status']=='Below average'])
    keywords_above_niche_sales = f"{int(file[file['Conversion status']=='Above average']['Purchases: Total Count'].sum()):,}"#
    keywords_below_niche_sales = f"{int(file[file['Conversion status']=='Below average']['Purchases: Total Count'].sum()):,}"#
    sales_increase_potential = f"{int(file['Sales increase potential'].sum()):,}"


    # label1.write('Purchases')
    stat1.metric(
        f'{st.session_state.entity} purchases',
        f'{brand_purchases:,}',
        help = f'Total and {st.session_state.entity}-specific purchases generated by the keyword pool'
        )
    stat6.metric(
        'Total purchases',
        f'{total_purchases:,}'
        )

    # label2.write('CTR')
    stat2.metric(
        f'{st.session_state.entity} CTR',
        str(brand_ctr_share)+'%',
        help = 'Total CTR for the keyword pool and % of clicks the f{st.session_state.entity} got'
        )
    stat7.metric(
        'Total CTR',
        str(niche_ctr)+'%'
        )

    # label3.write('Brand market share')
    stat3.metric(
        f'{st.session_state.entity} market share',
        str(brand_market_share)+'%',
        help = f'{st.session_state.entity} sales compared to all sales for this keyword set'        
        )
    stat8.metric('Sales increase potential',sales_increase_potential)

    # label4.write('Conversion')
    stat4.metric(
        f'{st.session_state.entity} conversion',
        str(brand_conversion)+'%',
        help = '% of purchases made compared to number of clicks'
        )
    stat9.metric(
        'Total conversion',
        str(kw_conversion)+'%'
        )


    # label5.write('Sales and KWs ABOVE and BELOW average')
    stat5.metric(
        'Sales and KWs ABOVE average',
        keywords_above_niche_sales,
        keywords_above_niche,
        delta_color='off',
        help = 'How many sales are we more/less eligible to participate in'
        )
    stat10.metric(
        'Sales and KWs BELOW average',
        keywords_below_niche_sales,
        keywords_below_niche,
        delta_color='off'
        )

    return None

def combine_files(multifile_path):
    pattern = '(?<=\")(.*?)(?=\")'

    column_list = ['Search Query', 'Search Query Score', 'Search Query Volume',
        'Impressions: Total Count', 'Impressions: ASIN Count',
        'Impressions: ASIN Share %', 'Clicks: Total Count',
        'Clicks: Click Rate %', 'Clicks: ASIN Count', 'Clicks: ASIN Share %',
        'Clicks: Price (Median)', 'Clicks: ASIN Price (Median)',
        'Clicks: Same Day Shipping Speed', 'Clicks: 1D Shipping Speed',
        'Clicks: 2D Shipping Speed', 'Cart Adds: Total Count',
        'Cart Adds: Cart Add Rate %', 'Cart Adds: ASIN Count',
        'Cart Adds: ASIN Share %', 'Cart Adds: Price (Median)',
        'Cart Adds: ASIN Price (Median)', 'Cart Adds: Same Day Shipping Speed',
        'Cart Adds: 1D Shipping Speed', 'Cart Adds: 2D Shipping Speed',
        'Purchases: Total Count', 'Purchases: Purchase Rate %',
        'Purchases: ASIN Count', 'Purchases: ASIN Share %',
        'Purchases: Price (Median)', 'Purchases: ASIN Price (Median)',
        'Purchases: Same Day Shipping Speed', 'Purchases: 1D Shipping Speed',
        'Purchases: 2D Shipping Speed', 'Reporting Date']

    combined = pd.DataFrame()
    for f in multifile_path:
        file = pd.read_csv(f, skiprows = 1)
        combined = pd.concat([combined, file])

    stat_cols = [
        'Impressions: ASIN Count','Clicks: ASIN Count','Cart Adds: ASIN Count',
        'Purchases: ASIN Count'
        ]

    pivot = combined.pivot_table(
        values = stat_cols,
        index = 'Search Query',
        aggfunc = 'sum'
        ).reset_index()

    for stat_col in stat_cols:
        del combined[stat_col]

    full = pd.merge(combined, pivot, how = 'left', on = 'Search Query')
    full = full[column_list]
    full = full.drop_duplicates('Search Query')
    full['Impressions: ASIN Share %'] = full['Impressions: ASIN Count'] / full['Impressions: Total Count']
    full['Clicks: ASIN Share %'] = full['Clicks: ASIN Count'] / full['Clicks: Total Count']
    full['Cart Adds: ASIN Share %'] = full['Cart Adds: ASIN Count'] / full['Cart Adds: Total Count']
    full['Purchases: ASIN Share %'] = full['Purchases: ASIN Count'] / full['Purchases: Total Count']    
    return full, combined


##############################################################################################################
#markup area
if 'entity' not in st.session_state:
    st.session_state.entity = ''
info_area = st.empty()
if 'info' not in st.session_state:
    st.session_state.info = ''
stat_area1 = st.empty()
stat_area2 = st.empty()
stat1,stat2,stat3,stat4,stat5 = stat_area1.columns([1,1,1,1,1])
stat6,stat7,stat8,stat9,stat10 = stat_area2.columns([1,1,1,1,1])

filter_area = st.empty()
filters1,filters2,filters3 = filter_area.columns([1,1,2])

df_area = st.empty()

if st.session_state['login']:

    if 'file' not in st.session_state:
        # with st.form('Search Query Performance analysis', clear_on_submit=True):
        file_path = st.file_uploader('Upload SQP file')
        if file_path:
            with st.spinner('Reading file'):
                time.sleep(0.5)
                file = read_file(file_path)
            with st.spinner('Crunching numbers'):
                time.sleep(0.5)
                file = sqp_analyze(file)
            with st.spinner('Grouping keywords, will take a few seconds...'):
                file = text_processing(file)
            st.session_state['file'] = file
            st.session_state['clusters_all'] = st.session_state['file']['cluster'].tolist()
            # submitted = st.form_submit_button("Let's see what you got",use_container_width=True)
        if st.checkbox('Multiple files to combine'):
            multifile_path = st.file_uploader('Upload multiple files to combine',accept_multiple_files=True)
            if multifile_path != []:
                full, combined = combine_files(multifile_path)
                combined_result = ff.prepare_for_export([full, combined],['Full','Combined'])
                st.download_button('Download combined file',combined_result,file_name = 'Combined ASINS.xlsx')
#################################################################################################################
#working area
    display_cols = [
        'Search Query','Search Query Volume',f'Impressions: {st.session_state.entity} Share %','Purchases: Total Count',f'Purchases: {st.session_state.entity} Count','Max position for glance views',
        'Sales increase potential','KW Conversion',f'{st.session_state.entity} Conversion','Conversion status'
    ]
    if 'file' in st.session_state:
        info_area.subheader(st.session_state.info)
        display_file = st.session_state['file'].copy() #copy the full dataframe to be sliced during filtering
        sales = filters1.multiselect('Sales',['high','med','low'],['high','med','low'])
        conversion = filters1.multiselect('Conversion',['high','med','low'], ['high','med','low'])
        niche_compare = filters2.multiselect('Brand vs Niche',['Above average','Below average'],['Above average','Below average'])
        kw_search = re.split(' ',filters2.text_input('Seach keywords containing',''))
        kw_container = filters3.container()
        all_keywords = filters3.checkbox('Select all', value = True)
        processed_groups = st.session_state['file']['cluster'].unique().tolist()
        processed_groups = sorted(processed_groups)
        if all_keywords:
            kw_groups = kw_container.multiselect('Select Keyword groups',processed_groups,processed_groups)
        else:
            kw_groups = kw_container.multiselect('Select Keyword groups',processed_groups)

        try:
            display_file = display_file[
                (display_file['Sales'].isin(sales))&
                (display_file['Conversion'].isin(conversion))&
                (display_file['cluster'].isin(kw_groups))&
                (display_file['Conversion status'].isin(niche_compare))
            ]
            display_file = display_file[display_file['Search Query'].str.contains('|'.join(kw_search),case = False)]
            # if len(kw_search)!= '':
            #     display_file = display_file[display_file['Search Query'].str.split(' ').apply(set(kw_search).issubset)]

            df_area.write(display_file[display_cols])
            get_stats(display_file)
        except:
            df_area.write('No matches found')

        result = ff.prepare_for_export([st.session_state['file']],['Search Query Performance'])
        st.download_button('Download full analysis',result,file_name = 'Keyword analysis.xlsx')
            

    

