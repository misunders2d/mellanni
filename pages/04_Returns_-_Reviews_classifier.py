import streamlit as st
from io import BytesIO
import pandas as pd
from modules import formatting as ff

st.title('Page under maintenance')
# st.title('Text classifier')
# choice = st.radio('Switch between Returns comments and Negative Reviews classifier',['Returns','Reviews'], horizontal = True)

# @st.cache
# def restore_from_file():
#     import pickle
#     try:
#         with open('ml_models/return_comments_classification.pkl','rb') as f:
#             lr, cv = pickle.load(f)
#         st.write('Model successfully restored')
#     except:
#         lr, cv = None, None
#     return lr, cv

# with st.expander('Input data'):
#     comments_file = st.file_uploader('Upload file with customer comments', type = ['.csv','.xlsx'],)
#     if file_p and '.xlsx' in file_p.name:
#         sheets = pd.ExcelFile(file_p).sheet_names
#         st.session_state.sheet = st.selectbox('Select a sheet with data', sheets)
#         if st.session_state.sheet:
#             st.session_state.file = pd.read_excel(sheets, sheet_name=st.session_state.sheet[0]  )
#     # elif file_p and '.csv' in file_p.name:
#     #     file = pd.read_csv(file_p, encoding = 'cp1251')
#     # if training == True:
#     #     file = file.dropna()
#     # columns = file.columns.tolist()
#     # text_column = sg.Window('Select the text column',
#     #     layout = [
#     #         [sg.DropDown(columns, default_value = columns[0], change_submits = True)]
#     #     ],size = (300,50)).read(close = True)[1][0]
#     # file = file.rename(columns = {text_column:'original_text'})
#     # if training == False:
#     #     return file#, text_column
#     # label_column = sg.Window('Select the labels column',
#     #     layout = [
#     #         [sg.DropDown(columns, default_value = columns[0], change_submits = True)]
#     #     ],size = (300,50)).read(close = True)[1][0]    

# def predicting(lr, cv, source = 'file', text = None):
#     # use a trained model to predict a new file
#     if not lr:
#         lr, cv = restore_from_file()
#     if source == 'file':
#         p_file = read_file(training = False)
#         p_file = clean_text(p_file, 'original_text')
#         new_voc = cv.transform(p_file['clean_column'])
#         predictions = lr.predict(new_voc)
#         p_file['predictions'] = predictions
        
#         output = BytesIO()

#         with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#             p_file.to_excel(writer, sheet_name = 'predict', index = False)
#             ff.format_header(p_file, writer, 'predict')
#         print(f'File saved to {save_path}')
#         os.startfile(save_path)
#         return None
#     elif source == 'other':
#         new_voc = cv.transform(text)
#         predictions = lr.predict(new_voc)
#         return predictions[0]

# # file_p = st.file_uploader('Upload file with customer comments', type = ['.csv','.xlsx'],)
# # if file_p and '.xlsx' in file_p.name:
# #     sheets = pd.ExcelFile(file_p).sheet_names
# #     sheet = st.selectbox('Select a sheet with data',sheets)
# #     file = pd.read_excel(file_p, sheet_name=sheet)
# # elif file_p and '.csv' in file_p.name:
# #     file = pd.read_csv(file_p, encoding = 'cp1251')

# # if 'file' in st.session_state:
# #     columns = file.columns.tolist()
# #     text_column = sg.Window('Select the text column',
# #         layout = [
# #             [sg.DropDown(columns, default_value = columns[0], change_submits = True)]
# #         ],size = (300,50)).read(close = True)[1][0]
# #     file = file.rename(columns = {text_column:'original_text'})

# st.write(st.session_state)
