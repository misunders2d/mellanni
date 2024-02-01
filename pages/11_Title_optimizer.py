from openai import OpenAI
import streamlit as st
import time, json

ASSISTANT_KEY = st.secrets['ASSISTANT_KEY']
assistant_id = 'asst_mvg3s2IB6NBVDUMVQAyhLAmb'
thread_id = 'thread_RBShV8Ay9B9n1nmJnAXdbBfy'

product_description_area = st.empty()
title_area1 = st.empty()
title_area2 = st.empty()
bullets_area = st.empty()
keywords_area = st.empty()
button_area = st.empty()
button_col1, button_col2 = button_area.columns([2,1])
log_area = st.empty()

if 'optimized_title' not in st.session_state:
    st.session_state.optimized_title = ('',True)
if 'optimized_bullets' not in st.session_state:
    st.session_state.optimized_bullets = ('',True)

product = product_description_area.text_area('Describe your product', placeholder='A bed sheet set made of microfiber with 1 flat sheet, 1 fitted sheet and 2 pillowcases')
title_current = title_area1.text_area('Current title', height = 2, max_chars=200, placeholder='input your current title here')
title_optimized = title_area2.text_area('Optimized title will be shown here', value = st.session_state.optimized_title[0], disabled = st.session_state.optimized_title[1])

bullets_real_col, bullets_opt_col = bullets_area.columns([1,1])
bullets_real = bullets_real_col.text_area('current bulletpoints', height = 300)
bullets_optimized = bullets_opt_col.text_area('Optimized bulletpoints', value = st.session_state.optimized_bullets[0], height = 300, disabled=st.session_state.optimized_bullets[1])

keywords = keywords_area.text_area('current keywords')

if 'assistant' not in st.session_state:
    client = client = OpenAI(api_key = ASSISTANT_KEY)
    st.session_state['client'] = client
    st.session_state['assistant'] = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.retrieve(thread_id = thread_id)

prompt = f'Product:\n{product}\n\nTitle:\n{title_current},\n\nBulletpoints:\n{bullets_real}\n\nKeywords:\n{keywords}'


if button_col1.button('Optimize') and 'result' not in st.session_state:
    client = st.session_state['client']
    message = client.beta.threads.messages.create(
        thread_id = thread_id,
        role = 'user',
        content = prompt)
    
    run = client.beta.threads.runs.create(
        thread_id = thread_id,
        assistant_id = assistant_id)
    
    status = ['queued']
    while status in ["queued", "in_progress"]:
        status = client.beta.threads.runs.retrieve(run_id = run.id, thread_id = thread_id).status
        log_area.write(status)
        time.sleep(1)
    if status not in ["queued", "in_progress"]:
        messages = client.beta.threads.messages.list(thread_id = thread_id)
        log_area.write('Done')
        st.session_state.result = json.loads(messages.data[0].content[0].text.value)
        st.session_state.optimized_title = (st.session_state.result.get('Title'),False)
        new_bullets = st.session_state.result.get('Bulletpoints')
        new_bullets = '\n\n'.join(new_bullets)
        st.session_state.optimized_bullets =  (new_bullets,False)
        st.rerun()
if button_col2.button('Clear'):
    if 'result' in st.session_state:
        del st.session_state.result