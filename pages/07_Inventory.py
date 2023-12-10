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

top_area = st.empty()
bottom_area = st.empty()
col1, col2, col3 = top_area.columns([3,2,1])


if not os.path.isdir('barcodes'):
    os.makedirs('barcodes')

def check_skus(sku_list,dictionary):
    wrong_skus = []
    for i, sku in enumerate(sku_list):
        file_sku = dictionary[dictionary['sku'] == sku]
        if len(file_sku) == 0:
            wrong_skus.append(sku)
    if len(wrong_skus) > 0:
        skus_out = '\n'.join(wrong_skus)
        st.text(f'The following SKUs were not found:\n{skus_out}')
        return False
    else:
        return True
    
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
        with open(f'barcodes\{fnsku}.png', 'wb') as f:
            Code128(str(fnsku), writer = ImageWriter()).write(f, options = options_fnsku)
        title_str = textwrap.wrap(titles[i], width = 40)
        number_barcodes = qty[i]
        for n in range(number_barcodes):
            for p,s in enumerate(title_str):
                pdf.text(x_coords[ix]+.1+(p/3), y_coords[iy]+0.5+(p/10), s)
            pdf.text(x_coords[ix]+.1, y_coords[iy]+0.6, 'New')
            pdf.image(f'barcodes\{fnsku}.png', x = x_coords[ix], y = y_coords[iy], w = width, h = height, type = '', link = '')
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

def generate_itf(sku_list,dictionary, layout, qty,leading = '00'):
    if check_skus(sku_list,dictionary):
        pass
    else:
        return None
    if layout == 'Letter':
        pdf_w = 8.5
        pdf_h = 11
        xmargin = 0.05
        ymargin = 0.5
        x_coords = [round(x,3) for x in np.arange(xmargin,pdf_w-xmargin,((pdf_w-xmargin)-xmargin)/3)+0.15]
        y_coords = [round(y,3) for y in np.arange(ymargin,pdf_h-ymargin,((pdf_h-ymargin)-ymargin)/10)+0.2]
        pdf = FPDF('P', 'in', 'Letter')
        #add a title page
        pdf.add_page()
        pdf.set_font('Arial', style ='', size = 42)
        pdf.text(2,pdf_h/2,'ITF14 CODE LIST')
        
    elif layout == 'Zebra':
        pdf_w = 4
        pdf_h = 1.25
        xmargin = 0.05
        ymargin = 0.2
        # x_coords = [round(x,3) for x in np.arange(xmargin,pdf_w-xmargin,((pdf_w-xmargin)-xmargin)/3)+0.15]
        # y_coords = [round(y,3) for y in np.arange(ymargin,pdf_h-ymargin,((pdf_h-ymargin)-ymargin)/10)+0.2]
        pdf = FPDF('L', 'in', (1.25,4))
    
    #start barcode pages
    pdf.add_page()
    pdf.set_font('Arial', style ='', size = 11)
    # skus = dictionary['sku']#.unique()
    # upcs = dictionary['upc']#.dropna().unique()
    # if len(upcs) == 0:
    #     del file['UPC']
    #     d = pd.read_excel('Dictionary.xlsx', usecols = ['FNSKU','UPC'])
    #     d = d.drop_duplicates('FNSKU', keep = 'last')
    #     file = pd.merge(file, d, how = 'left', on = 'FNSKU')
    #generate itf barcodes from the list
    ix = 0
    iy = 0
    for i, sku in enumerate(sku_list):
        # print(f'Printing {sku}')
        file_sku = dictionary[dictionary['sku'] == sku]
        sku_str = textwrap.wrap(sku, width = 25)
        upc = f"{leading}{file_sku['upc'].values[0]}"
        # quantity = file_sku['Quantity'].values[0]
        with open(f'barcodes\{sku.replace("-","_")}.png', 'wb') as f:
            Code39(str(upc), writer = ImageWriter(),add_checksum = False).write(f, options = options_itf)
        # time.sleep(0.5)
        # for q in qty:
        if layout == 'Letter':
            for p,s in enumerate(sku_str):
                pdf.text(x_coords[ix]+.1, y_coords[iy]+(p/7), s)
            pdf.image(f'barcodes\{sku.replace("-","_")}.png', x = x_coords[ix], y = y_coords[iy]+0.2, w = width, h = height, type = '', link = '')
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
        # pdf.add_page()
                ix = 0
                iy = 0
        elif layout == 'Zebra':
            for p,s in enumerate(sku_str):
                pdf.text(xmargin+0.5, ymargin+(p/7), s)
            pdf.image(f'barcodes\{sku.replace("-","_")}.png', x = xmargin+0.3, y = ymargin+0.2, w = width, h = height, type = '', link = '')
            # ymargin += 0.2
            pdf.add_page()
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

# col1, col2, = st.columns([10,3])

with col3:
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
    
    if col3.checkbox('Dictionary'):
        dictionary = download_dictionary()
        col3.download_button('Download dictionary',dictionary, file_name = 'Dictionary.xlsx')
    if col3.button('Clear'):
        remove_images()
with col2:
    barcode_type = col2.radio('Select barcode type:',['FNSKU','ITF14'])
    
    if barcode_type == 'ITF14':
        layout = col2.radio('Layout type',['Letter','Zebra'])
        qty_type = 1
        leading = col2.text_input('Leading digits', '00',max_chars=2, placeholder='00')
    elif barcode_type == 'FNSKU':
        layout = 'Letter'
        qty_type = col2.radio('Labels per sheet',[1,30])

with col1:
    skus = st.text_area('Input SKUs', height = 300, help = 'Input a list of SKUs you want to generate barcodes for').split('\n')
    sku_list = [x for x in skus if x != '']
    if col1.button('Create barcodes') and len(sku_list) > 0:
        with st.spinner('Please wait'):
            dictionary = pull_dictionary()
            check_skus(sku_list,dictionary)
            st.session_state.file = dictionary[dictionary['sku'].isin(sku_list)].reset_index()
            del st.session_state.file['index']
            fnskus = st.session_state.file['fnsku']
            titles = st.session_state.file['short_title']
            upcs = st.session_state.file['upc']
            skus = st.session_state.file['sku']
            qty = [qty_type]*len(sku_list)
            if barcode_type == 'FNSKU':
                st.session_state.pdf = generate_pdf(fnskus, titles, qty)
                st.session_state.file_name = 'Amazon barcodes.pdf'
            elif barcode_type == 'ITF14':
                st.session_state.pdf = generate_itf(sku_list,dictionary, layout, qty, leading = leading)
                st.session_state.file_name = 'ITF14 barcodes.pdf'
    if 'pdf' in st.session_state and st.session_state['pdf'] is not None:
        st.session_state.pdf.output('barcodes/barcodes.pdf', 'F')
        with open('barcodes/barcodes.pdf', "rb") as pdf_file:
            PDFbyte = pdf_file.read()
        remove_images()
        col2.download_button(
            label = 'Download PDF',
            data=PDFbyte,
            file_name = st.session_state.file_name)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            st.session_state.file.to_excel(writer, sheet_name = 'SKUs', index = False)
            ff.format_header(st.session_state.file, writer, 'SKUs')
        col2.download_button(
            label = 'Download SKU list',
            data = output.getvalue(),
            file_name = 'SKUs.xlsx')


bottom_area.markdown('\nAdditional tool to optimize package dimensions\n\nhttps://package-optimizer.streamlit.app/')