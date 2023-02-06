import streamlit as st
from io import BytesIO
import pandas as pd
from modules import formatting as ff

# st.title('Page under maintenance')
st.subheader('Text classifier')
choice = st.radio('Switch between Returns comments and Negative Reviews classifier',['Returns','Reviews'], horizontal = True)

def main_returns(choice):
    file = None
    col1, col2 = st.columns(2)
    block1, block2 = col1.container(),col2.container()
    file_obj = block1.file_uploader('Upload the returns file', type = ['.csv','.xlsx'])
    phrase = block2.text_area('Input the comment to classify')
    if file_obj and '.xlsx' in file_obj.name:
        sheets = pd.ExcelFile(file_obj).sheet_names
        sheet = block1.selectbox('Select a sheet with data', sheets)
        if block1.button('Read file'):
            file = read_file(file_obj, type = 'xlsx', sheet = sheet)
    elif file_obj and '.csv' in file_obj.name:
        if block1.button('Read file'):
            file = read_file(file_obj, type = 'csv')
    if file_obj and isinstance(file, pd.core.frame.DataFrame):
        st.session_state['file'] = file
    if 'file' in st.session_state:
        columns = file.columns.tolist()
        text_column = block1.selectbox('Select a column with comments', columns)
        st.dataframe(file.head())
        if text_column:
            file = file.rename(columns = {text_column:'original_text'})
    # if choice == 'Returns':
    # elif choice == 'Reviews':
    #     block2.write('reviews')
    return None

def read_file(file_obj, type = 'xlsx',sheet = None):
    if type == 'xlsx':
        return pd.read_excel(file_obj, sheet_name=sheet)
    elif type == 'csv':
        return pd.read_csv(file_obj, encoding = 'cp1251')


@st.cache
def restore_from_file():
    import pickle
    try:
        with open('ml_models/return_comments_classification.pkl','rb') as f:
            lr, cv = pickle.load(f)
    except:
        lr, cv = None, None
    return lr, cv


def predicting(lr, cv, source = 'file', text = None):
    # use a trained model to predict a new file
    if not lr:
        lr, cv = restore_from_file()
    if source == 'file':
        p_file = read_file(training = False)
        p_file = clean_text(p_file, 'original_text')
        new_voc = cv.transform(p_file['clean_column'])
        predictions = lr.predict(new_voc)
        p_file['predictions'] = predictions
        
        output = BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            p_file.to_excel(writer, sheet_name = 'predict', index = False)
            ff.format_header(p_file, writer, 'predict')
        print(f'File saved to {save_path}')
        os.startfile(save_path)
        return None
    elif source == 'other':
        new_voc = cv.transform(text)
        predictions = lr.predict(new_voc)
        return predictions[0]

# file_p = st.file_uploader('Upload file with customer comments', type = ['.csv','.xlsx'],)
# if file_p and '.xlsx' in file_p.name:
#     sheets = pd.ExcelFile(file_p).sheet_names
#     sheet = st.selectbox('Select a sheet with data',sheets)
#     file = pd.read_excel(file_p, sheet_name=sheet)
# elif file_p and '.csv' in file_p.name:
#     file = pd.read_csv(file_p, encoding = 'cp1251')

# if 'file' in st.session_state:
#     columns = file.columns.tolist()
#     text_column = sg.Window('Select the text column',
#         layout = [
#             [sg.DropDown(columns, default_value = columns[0], change_submits = True)]
#         ],size = (300,50)).read(close = True)[1][0]
#     file = file.rename(columns = {text_column:'original_text'})

# st.write(st.session_state)
if __name__ == '__main__':
    main_returns(choice)