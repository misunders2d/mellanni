from openai import OpenAI
import streamlit as st
import time

st.set_page_config(page_title = 'Mellanni Tools App', page_icon = 'media/logo.ico',layout="wide")

ASSISTANT_KEY = st.secrets['ASSISTANT_KEY']
assistant_id = 'asst_mvg3s2IB6NBVDUMVQAyhLAmb'
# thread_id = 'thread_RBShV8Ay9B9n1nmJnAXdbBfy'

st.title('AI powered Title and Bulletpoints optimizer')
st.subheader('Input short product description, current title and bulletpoints along with the most important keywords.')

product_description_area = st.empty()
title_area1 = st.empty()
title_area2 = st.empty()
bullets_area = st.empty()
keywords_area = st.empty()
button_area = st.empty()
button_col1, button_col2, button_col3 = button_area.columns([3,1,1])
log_area = st.empty()

if 'optimized_title' not in st.session_state:
    st.session_state.optimized_title = ('',True)
if 'optimized_bullets' not in st.session_state:
    st.session_state.optimized_bullets = ('',True)

product = product_description_area.text_area('Describe your product',placeholder='Example: A bed sheet set made of microfiber with 1 flat sheet, 1 fitted sheet and 2 pillowcases')
title_current = title_area1.text_area('Current title', height = 2, max_chars=200, placeholder='Input your current title here')
title_optimized = title_area2.text_area('Optimized title will be shown here', value = st.session_state.optimized_title[0], disabled = st.session_state.optimized_title[1], max_chars=200)

bullets_real_col, bullets_opt_col = bullets_area.columns([1,1])
bullets_real = bullets_real_col.text_area('Current bulletpoints', height = 300, placeholder='Input your current bulletpoints')
bullets_optimized = bullets_opt_col.text_area('Optimized bulletpoints', value = st.session_state.optimized_bullets[0], height = 300, disabled=st.session_state.optimized_bullets[1])

keywords = keywords_area.text_area('Current keywords', placeholder='Input your most important keywords - AI will try to use them in the new title')

if 'assistant' not in st.session_state:
    client = client = OpenAI(api_key = ASSISTANT_KEY)
    st.session_state['client'] = client
    st.session_state['assistant'] = client.beta.assistants.retrieve(assistant_id)
    # thread = client.beta.threads.retrieve(thread_id = thread_id)

prompt = f'Product:\n{product}\n\nTitle:\n{title_current},\n\nBulletpoints:\n{bullets_real}\n\nKeywords:\n{keywords}'

def process():
    client = st.session_state['client']
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id = thread.id,
        role = 'user',
        content = prompt)
    
    run = client.beta.threads.runs.create(
        thread_id = thread.id,
        assistant_id = assistant_id)
    time.sleep(0.5)
    if 'status' not in st.session_state:
        st.session_state.status = ['queued']
    while True:
        st.session_state.status = client.beta.threads.runs.retrieve(run_id = run.id, thread_id = thread.id).status
        log_area.write('Please wait')
        time.sleep(0.5)
        log_area.write(st.session_state.status)
        time.sleep(0.5)
        if st.session_state.status =='completed':
            break
    messages = client.beta.threads.messages.list(thread_id = thread.id)
    log_area.write('Done')
    st.session_state.result = messages.data[0].content[0].text.value
    st.session_state.optimized_title = (st.session_state.result.split('|')[0].strip(),False)
    new_bullets = st.session_state.result.split('|')[1:]
    new_bullets = [x.strip() for x in new_bullets]
    new_bullets = '\n\n'.join(new_bullets)
    st.session_state.optimized_bullets =  (new_bullets,False)
    client.beta.threads.delete(thread_id = thread.id)
    st.rerun()

if button_col1.button('Optimize') and 'result' not in st.session_state:
    process()
if button_col2.button('Try again'):
    if 'result' in st.session_state:
        del st.session_state.result
    process()
# if button_col3.button('Reset'):
#     for item in st.session_state:
#         del item
#     st.rerun()
