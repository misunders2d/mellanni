import streamlit as st
from io import BytesIO
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
import re
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression


from modules import formatting as ff

# st.title('Page under maintenance')
st.subheader('Text classifier')

import login
st.session_state['login'], st.session_state['name'] = login.login()

if st.session_state['login']:

    choice = st.radio('Switch between Returns comments and Negative Reviews classifier',['Returns','Reviews'], horizontal = True)


    def read_file(file_obj, type = 'xlsx',sheet = None):
        if type == 'xlsx':
            return pd.read_excel(file_obj, sheet_name=sheet)
        elif type == 'csv':
            return pd.read_csv(file_obj, encoding = 'cp1251')

    def clean_text(file, column):
        text = file[column].tolist()
        lemmatizer = WordNetLemmatizer()
        corpus = []
        for i in range(len(text)):
            r = re.sub('[^a-zA-Z]', ' ', text[i]).lower().split()
            r = [word for word in r if word not in stopwords.words('english')]
            r = [lemmatizer.lemmatize(word) for word in r]
            r = ' '.join(r)
            corpus.append(r)
        file['clean_column'] = corpus
        return file

    def vectorize_text(train, test):
        cv = CountVectorizer()
        X_train_cv = cv.fit_transform(train)
        X_test_cv = cv.transform(test)
        return X_train_cv, X_test_cv, cv

    @st.cache_data
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
            p_file = st.session_state['file'].copy()
            p_file = p_file.dropna(subset = 'original_text')
            p_file = clean_text(p_file, 'original_text')
            new_voc = cv.transform(p_file['clean_column'])
            predictions = lr.predict(new_voc)
            p_file['predictions'] = predictions
            
            output = BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                p_file.to_excel(writer, sheet_name = 'predict', index = False)
                ff.format_header(p_file, writer, 'predict')
            st.download_button('Download results',output.getvalue(), file_name = 'Classifier.xlsx')
        elif source == 'other':
            new_voc = cv.transform(text)
            predictions = lr.predict(new_voc)
            return predictions[0]
            
                
            return None
        
        elif source == 'other':
            new_voc = cv.transform(text)
            predictions = lr.predict(new_voc)
            return predictions[0]

    file = None
    col1, col2 = st.columns(2)
    block1, block2 = col1.container(),col2.container()
    file_obj = block1.file_uploader('Upload the returns file', type = ['.csv','.xlsx'])
    phrase = block2.text_area('Input the comment to classify')
    if block2.button('Check') and phrase != '':
        lr, cv = restore_from_file()
        answer = predicting(lr, cv, source = 'other', text = [phrase])
        block2.write(f'Possible category:  \n\n{answer}')

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
        columns = (st.session_state['file']).columns.tolist()
        text_column = block1.selectbox('Select a column with comments', columns)
        st.dataframe((st.session_state['file']).head())
        if st.button('Run classifier'):
            st.session_state['file'] = st.session_state['file'].rename(columns = {text_column:'original_text'})
            lr,cv = restore_from_file()
            predicting(lr,cv,source = 'file')
