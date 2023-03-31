import streamlit as st
import pandas as pd
from io import BytesIO


st.write('Testing')

from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from imagekitio.models.CreateFolderRequestOptions import CreateFolderRequestOptions
import base64
from deta import Deta
db_token = st.secrets['DB_USERS']
deta = Deta(db_token)

# imagekitio credentials
ik_credentials = (st.secrets['IK_PRIVATE_KEY'],st.secrets['IK_PUBLIC_KEY'])
private_key=ik_credentials[0]
public_key=ik_credentials[1]
url_endpoint='https://ik.imagekit.io/jgp5dmcfb'


imagekit = ImageKit(
    private_key=private_key,
    public_key=public_key,
    url_endpoint=url_endpoint
    )

skus = st.text_area('Input SKUs').split('\n')
folder = st.text_input('Input folder name, if necessary')
options = UploadFileRequestOptions(
    use_unique_file_name=False,
    folder=f'/{folder}/')


files = st.file_uploader('Upload images',accept_multiple_files= True)

#read file into base_64
if files:
    urls = []
    for f in files:
        image_file = f.read()
        img = base64.b64encode(image_file)
        
        result = imagekit.upload_file(file = img, file_name = f.name, options = options)
        url = url_endpoint+result.file_path
        urls.append(url)
    df = pd.DataFrame(columns = ['SKU']+[f'Image_{x}' for x in range(9)])
    if len(skus) > 1 and skus != "":
        urls = [urls for _ in range(len(skus))]
        df['SKU'] = skus
    url_df = pd.DataFrame([urls], columns = [f'Image_{x}' for x in range(len(urls))])
    df = pd.concat([df, url_df])
    st.write(df)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name = 'image_links', index = False)
    st.download_button('Download results',output.getvalue(), file_name = 'image_links.xlsx')

