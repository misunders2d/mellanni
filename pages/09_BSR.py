import streamlit as st
import pandas as pd
import altair as alt
from matplotlib import pyplot as plt

st.set_page_config(page_title = 'M Tools App', page_icon = 'media/logo.ico',layout="wide")

col1, col2, col3, col4, col5 = st.empty(),st.empty(),st.empty(),st.empty(),st.empty()
column_area = [col1, col2, col3, col4, col5]

file_path = st.file_uploader('Upload a BSR file')
if file_path:
    st.session_state.file = pd.read_excel(file_path)
    st.session_state.start = pd.to_datetime(st.session_state.file['Date'].values[0]).date()
    st.session_state.end = pd.to_datetime(st.session_state.file['Date'].values[-1]).date()

if 'file' in st.session_state:
    min_value, max_value = st.session_state.start, st.session_state.end
    start, end = st.slider(
        'Select dates',
        min_value = min_value, max_value = max_value,
        value = (min_value+pd.Timedelta(days = 30),max_value)
        )
    full_file = st.session_state.file
    # bsr_columns = [x for x in full_file.columns if 'BSR' in x]
    # full_file[bsr_columns] = full_file[bsr_columns].applymap(lambda x: None if x >100 else x)
    file = full_file[(full_file['Date']>=pd.to_datetime(start))&(full_file['Date']<=pd.to_datetime(end))]
    brands = [x.split(' ')[0] for x in file.columns]
    brands.remove('Date')
    brands = list(set(brands))
    for brand,col in list(zip(brands, column_area)):
        cols = [x for x in file.columns if brand in x]
        f = file[['Date']+cols]

        fig, ax = plt.subplots(figsize = (12,6))
        ax.plot(f['Date'],f[cols[0]], color = 'red')
        ax.set_ylabel('Price', color = 'red')
        ax1 = ax.twinx()
        ax1.set_ylim(50)
        ax1.plot(f['Date'],f[cols[1]],linestyle = '--', color = 'green',)
        ax1.set_ylabel('BSR', color = 'green')
        plt.suptitle(brand)
        fig.tight_layout()
        col.pyplot(fig)


        # base = alt.Chart(f).encode(alt.X('Date'))
        # price = base.mark_line(color = 'red').encode(alt.Y(cols[0]))
        # bsr = base.mark_line(color = 'green', clip = True).encode(alt.Y(cols[1]))#.alt.scale(domain = (1,100)))

        # col.altair_chart((price+bsr).resolve_scale(y = 'independent'), use_container_width=True)
