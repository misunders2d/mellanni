import streamlit as st
from modules import formatting as ff
import textwrap
# from PIL import Image
# from PIL import ImageDraw
from modules import gcloud_modules as gc
from PIL import ImageFont
font = ImageFont.load_default()
from fpdf import FPDF
import pandas as pd
from io import BytesIO
import numpy as np
import os
from barcode import Code128, Code39
from barcode.writer import ImageWriter

width = 2.2
height = 0.4
options_fnsku = {'module_width':height, 'module_height':width+7, 'font_size':10, 'text_distance':4}
options_itf = {'module_width':height, 'module_height':width+7, 'font_size':12, 'text_distance':4, 'font':font}
itf_columns = ['SKU','Quantity','UPC','FNSKU']
template = pd.DataFrame(data = [['sample SKU','required quantity of labels','upc (NOT ITF)','FNSKU (barcode)']], columns = itf_columns)            

if not os.path.isdir('barcodes'):
    os.makedirs('barcodes')

def generate_pdf(fnskus, titles, qty):
    #PDF
    pdf_w = 8.5
    pdf_h = 11
    xmargin = 0.05
    ymargin = 0.5
    x_coords = [round(x,3) for x in np.arange(xmargin,pdf_w-xmargin,((pdf_w-xmargin)-xmargin)/3)+0.15]
    y_coords = [round(y,3) for y in np.arange(ymargin,pdf_h-ymargin,((pdf_h-ymargin)-ymargin)/10)+0.2]
    pdf = FPDF('P', 'in', 'Letter')
    pdf.add_page()
    # pdf.set_stretching(70.0)
    pdf.set_font('Arial', style ='', size = 8)
    
    #generate fnsku barcodes from the list
    ix = 0
    iy = 0
    for i, fnsku in enumerate(fnskus):
        with open(f'barcodes/{fnsku}.png', 'wb') as f:
            Code128(str(fnsku), writer = ImageWriter()).write(f, options = options_fnsku)
        title_str = textwrap.wrap(titles[i], width = 40)
        number_barcodes = qty[i]
        for n in range(number_barcodes):
            for p,s in enumerate(title_str):
                pdf.text(x_coords[ix]+.1+(p/3), y_coords[iy]+0.5+(p/10), s)
            pdf.text(x_coords[ix]+.1, y_coords[iy]+0.6, 'New')
            pdf.image(f'barcodes/{fnsku}.png', x = x_coords[ix], y = y_coords[iy], w = width, h = height, type = '', link = '')
            if ix <2:
                ix += 1
            else:
                ix = 0
                iy +=1
            if iy <10:
                pass
            else:
                iy = 0
                pdf.add_page()
    
    # pdf.output('barcodes.pdf', 'F')
    return pdf


def remove_images():
    #remove all created png's
    if os.path.isdir('barcodes'):
        files = os.listdir('barcodes')
        for file in files:
            os.remove(os.path.join('barcodes',file))
        os.removedirs('barcodes')
    return None

def pull_dictionary():
    client = gc.gcloud_connect()
    sql = '''SELECT sku,fnsku,upc,collection,sub_collection,size,color,short_title FROM `auxillary_development.dictionary`'''
    query_job = client.query(sql)  # Make an API request.
    dictionary = query_job.result().to_dataframe()
    client.close()
    dictionary = dictionary[~dictionary['fnsku'].isin(['bundle','none','FBM'])]
    dictionary['collection'] = dictionary['collection'].str.replace('1800','Iconic')
    dictionary['sub_collection'] = dictionary['sub_collection'].str.replace('1800','Iconic')
   return dictionary

col1, col2 = st.columns([10,3])

with col2:
    # @st.cache_data(show_spinner=False)
    def download_dictionary():
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
        dictionary = download_dictionary()
        st.download_button('Download dictionary',dictionary, file_name = 'Dictionary.xlsx')

with col1:
    skus = st.text_area('Input SKUs', height = 300, help = 'Input a list of SKUs you want to generate barcodes for').split('\n')
    sku_list = [x for x in skus if x != '']
    if st.button('Create barcodes') and len(sku_list) > 0:
        with st.spinner('Please wait'):
            dictionary = pull_dictionary()
            st.session_state.file = dictionary[dictionary['sku'].isin(sku_list)].reset_index()
            del st.session_state.file['index']
            fnskus = st.session_state.file['fnsku']
            titles = st.session_state.file['short_title']
            qty = [1]*len(sku_list)
            st.session_state.pdf = generate_pdf(fnskus, titles, qty)
    if 'pdf' in st.session_state:
        st.session_state.pdf.output('barcodes/barcodes.pdf', 'F')
        with open('barcodes/barcodes.pdf', "rb") as pdf_file:
            PDFbyte = pdf_file.read()
        remove_images()
        st.download_button(
            label = 'Download PDF',
            data=PDFbyte,
            file_name = 'barcodes.pdf')
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            st.session_state.file.to_excel(writer, sheet_name = 'SKUs', index = False)
            ff.format_header(st.session_state.file, writer, 'SKUs')
        st.download_button(
            label = 'Download SKU list',
            data = output.getvalue(),
            file_name = 'SKUs.xlsx')
