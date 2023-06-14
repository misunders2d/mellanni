import streamlit as st
import pandas as pd
import re
from io import BytesIO
from modules import formatting as ff
import login
from modules import gcloud_modules as gc
import openai
import time
key = st.secrets['AI_KEY']
openai.api_key = key


st.set_page_config(page_title = 'Mellanni Tools', page_icon = 'media/logo.ico',layout="wide",initial_sidebar_state='collapsed')
st.session_state['login'], st.session_state['name'] = login.login()
name_area = st.empty()
col1, col2 = st.columns([10,3])

if st.session_state['login']:
    name_area.write(f"Welcome {st.session_state['name']}")

    with col2:
        # @st.cache_data(show_spinner=False)
        def pull_dictionary():
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
            dictionary = pull_dictionary()
            st.download_button('Download dictionary',dictionary, file_name = 'Dictionary.xlsx')


    with col1:
        with st.expander('Link generator for Seller Central'):
            result = []

            def review_links():
                for a in asin_list:
                    link = 'https://www.amazon.com/product-reviews/'+a+'/ref=cm_cr_arp_d_viewopt_fmt?sortBy=recent&pageNumber=1&formatType=current_format'
                    result.append(link)
                return result
                    
            def sc_links():
                for a in asin_list:
                    link = 'https://sellercentral.amazon.com/inventory/ref=xx_invmgr_dnav_xx?tbla_myitable=sort:%7B%22sortOrder%22%3A%22ASCENDING%22%2C%22sortedColumnId%22%3A%22skucondition%22%7D;search:'+a+';pagination:1;'
                    result.append(link)
                return result

            def pdp_links():
                for a in asin_list:
                    link = 'https://www.amazon.com/dp/'+a
                    result.append(link)
                return result

            def check_prices():
                client = gc.gcloud_connect()
                sql = '''SELECT asin, item_name, price FROM `auxillary_development.inventory_report`'''
                query_job = client.query(sql)  # Make an API request.
                inventory = query_job.result().to_dataframe()
                client.close()
                inventory_asin = inventory[inventory['asin'].isin(asin_list)]
                inventory_asin[inventory_asin.columns] = inventory_asin[inventory_asin.columns].astype('str')
                # result = (inventory_asin['asin']+' - '+ inventory_asin['price'] + ' - ' + inventory_asin['item_name']).tolist()
                return inventory_asin

            def edit_links():
                client = gc.gcloud_connect()
                sql = '''SELECT ASIN,SKU FROM `auxillary_development.dictionary`'''
                query_job = client.query(sql)  # Make an API request.
                dictionary = query_job.result().to_dataframe()
                client.close()
                for a in asin_list:
                    dict_asin = dictionary[dictionary['ASIN'] == a]
                    sku = dict_asin['SKU'].tolist()#[0]
                    for s in sku:
                        link = f'https://sellercentral.amazon.com/abis/listing/edit?marketplaceID=ATVPDKIKX0DER&ref=xx_myiedit_cont_myifba&sku={s}&asin={a}&productType=HOME_BED_AND_BATH#product_details'
                        result.append(link)
                return result
                
            def fix_stranded_inventory():
                for a in asin_list:
                    # dict_asin = dictionary[dictionary['ASIN'] == a]
                    link = 'https://sellercentral.amazon.com/inventory?viewId=STRANDED&ref_=myi_ol_vl_fba&tbla_myitable=sort:%7B%22sortOrder%22%3A%22DESCENDING%22%2C%22sortedColumnId%22%3A%22date%22%7D;search:'+a+';pagination:1;'
                    result.append(link)
                return result
                    
            def order_links():
                for a in asin_list:
                    link = 'https://sellercentral.amazon.com/orders-v3/search?page=1&q='+a+'&qt=asin'
                    result.append(link)
                return result
            
            functions = {
                '1 - review links':review_links,
                '2 - Seller Central links':sc_links,
                '3 - Product Detail Page links':pdp_links,
                '4 - Check prices in Inventory file':check_prices,
                '5 - Seller Central Edit links':edit_links,
                '6 - Fix Stranded Inventory links':fix_stranded_inventory,
                '7 - Order links':order_links
                }

            asins = re.split(r'\n|,| ',st.text_area('Input ASINs'))
            options = [x for x in functions.keys()]
            option = st.selectbox('Select an option',options)
            if st.button('Run'):
                asin_list = [x for x in asins if x != ""]
                func = functions[option]
                result = func()
                if isinstance(result,pd.core.frame.DataFrame):
                    result = result.reset_index().drop('index', axis = 1)
                st.experimental_data_editor(result)

        with st.expander('Business report link generator'):
            from datetime import datetime, timedelta
            e_date = (datetime.now().date()-timedelta(days = 2))
            s_date = (e_date-timedelta(days = 10))
            start = st.date_input('Starting date', value = s_date)
            end = st.date_input('End date', value = e_date)
            numdays = (e_date - s_date).days + 1
            date_range = [e_date - timedelta(days = x) for x in range(numdays)]
            link_list = []
            for d in date_range:
                link = f"https://sellercentral.amazon.com/business-reports/ref=xx_sitemetric_dnav_xx#/report?id=102%3ADetailSalesTrafficBySKU&chartCols=&columns=0%2F1%2F2%2F3%2F4%2F5%2F6%2F7%2F8%2F9%2F10%2F11%2F12%2F13%2F14%2F15%2F16%2F17%2F18%2F19%2F20%2F21%2F22%2F23%2F24%2F25%2F26%2F27%2F28%2F29%2F30%2F31%2F32%2F33%2F34%2F35%2F36%2F37&fromDate={d.strftime('%Y-%m-%d')}&toDate={d.strftime('%Y-%m-%d')}"
                link_list.append(link)
                full_list = '  \n  \n'.join(link_list)
            if st.button('Generate'):
                st.text_area('Generated links',full_list)

        with st.expander('Pricelist checker'):
            import pandas as pd
            import numpy as np
            
            def linspace(df,steps):
                result = np.linspace(df['Standard Price'],df['MSRP'],steps)
                return result

            def add_steps(file_path, steps):
                file = pd.read_excel(file_path, usecols = ['Collection','SKU', 'ASIN', 'Size', 'Color', 'Standard Price', 'MSRP'])
                file['steps'] = file.apply(linspace, steps = steps+1, axis = 1)
                
                for i in range(0,steps+1):
                    file[f'step {i}'] = file['steps'].apply(lambda x: round(x[i],2))
                for i in range(0,steps):
                    file[f'% {i+1}'] = file[f'step {i+1}'] / file[f'step {i}'] - 1
                del file['steps']
                del file['step 0']
                return file

        with st.expander('Backend checker'):
            import json
            def process_backend(files):
                to_df = []
                for file in files:
                    file = file.getvalue()
                    result = json.loads(file.decode('utf-8'))
                
                    kw_fields = [x for x in result['detailPageListingResponse'].keys() if 'keyword' in x.lower()]
                    if not kw_fields:
                        break
                    asin = result['detailPageListingResponse']['asin']['value']
                    try:
                        brand = result['detailPageListingResponse']['brand#1.value']['value']
                    except:
                        try:
                            brand = result['detailPageListingResponse']['brand']['value']
                        except:
                            brand = 'Unknown'
                    platinum = [x for x in result['detailPageListingResponse'].keys() if 'platinum' in x.lower()]
                    pkw = []
                    for p in platinum:
                        pkw.append(result['detailPageListingResponse'][p]['value'])
                    pkw = ' '.join(pkw)
                    try:
                        size = result['detailPageListingResponse']['size#1.value']['value']
                    except:
                        size = result['detailPageListingResponse']['size_name']['value']
                    try:
                        color = result['detailPageListingResponse']['color#1.value']['value']
                    except:
                        color = result['detailPageListingResponse']['color_name']['value']
                    try:
                        kws = result['detailPageListingResponse']['generic_keyword#1.value']['value']#.split(' ')
                    except:
                        kws = result['detailPageListingResponse']['generic_keywords']['value']#.split(' ')
                    try:
                        title = result['detailPageListingResponse']['item_name#1.value']['value']
                    except:
                        title = result['detailPageListingResponse']['item_name']['value']
                    to_df.append([asin, brand, size, color, kws, pkw,title])
                df = pd.DataFrame(to_df,columns = ['asin','brand','size','color','kws','platinum kws','title'])
                return df

            markets = ['USA','CA','UK','DE','FR','IT','SP']
            market = st.radio('Select marketplace',markets,horizontal = True)
            extensions = ['com','ca','co.uk','de','fr','it','sp']
            choice = dict(zip(markets,extensions))
            data_area = st.empty()
            asin_col,links_col = data_area.columns([1,3])
            button_area = st.empty()
            but1,but2,but3 = button_area.columns([1,1,1])
            link = f'https://sellercentral.amazon.{choice[market]}/abis/ajax/reconciledDetailsV2?asin='
            asins = asin_col.text_area('Input ASINs to parse').split('\n')
            if but1.button('Get links'):
                st.session_state['asins'] = True
                links_col.text_area('Links:','\n'.join(link+asin for asin in asins))
            if 'asins' in st.session_state:
                files = st.file_uploader('Upload files', type = '.json', accept_multiple_files= True)
                if files:
                    final = process_backend(files)
                    st.write(final)
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        final.to_excel(writer, sheet_name = 'KW', index = False)
                        ff.format_header(final, writer, 'KW')
                    st.download_button('Download results',output.getvalue(), file_name = 'backend.xlsx')
            if but3.button('Reset') and 'asins' in st.session_state:
                del st.session_state['asins']

        with st.expander('Convert GDrive links to direct links'):
            import re
            links_area = st.empty()
            def clean_links(links):
                clean = []
                for i in links:
                    c = i.replace('https://drive.google.com/file/d/','').replace('/view?usp=sharing','')
                    c = c.replace('https://drive.google.com/open?id=','').split('&authuser=')[0]
                    c = 'https://drive.google.com/uc?export=view&id='+c
                    clean.append(c)
                return clean
            links = re.split(',|\n',links_area.text_area('Input links to convert'))
            links = [x for x in links if x != '']
            if st.button('Convert'):
                new_links = clean_links(links)
                links_area.text_area('Clean links','\n\n'.join(new_links))
        try:
            with st.expander('Upload images to web and get direct links'):
                from imagekitio import ImageKit
                from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
                from imagekitio.models.CreateFolderRequestOptions import CreateFolderRequestOptions
                import base64

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
                folder = st.text_input('Input folder name, if necessary').replace('.','_').replace(' ','_')
                options = UploadFileRequestOptions(
                    use_unique_file_name=False,
                    folder=f'/{folder}/')


                files = st.file_uploader('Upload images',accept_multiple_files= True)

                #read file into base_64
                if files and st.button('Upload'):
                    skus = [x for x in skus if x != '']
                    urls = []
                    for f in files:
                        image_file = f.read()
                        img = base64.b64encode(image_file)
                        
                        result = imagekit.upload_file(file = img, file_name = f.name, options = options)
                        url = url_endpoint+result.file_path
                        urls.append(url)
                    urls = sorted(urls, reverse = False)

                    df = pd.DataFrame(skus,columns = ['SKU'])
                    if len(skus) > 1 and skus != "":
                        urls = [urls for _ in range(len(skus))]
                        df['SKU'] = skus
                    url_df = pd.DataFrame(urls)
                    df = pd.concat([df, url_df], axis = 1)

                    st.write(df)
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, sheet_name = 'image_links', index = False)
                    st.download_button('Download results',output.getvalue(), file_name = 'image_links.xlsx')
        except Exception as e:
            st.write(f'Sorry, this block is currently unavailable:\n{e}')

        with st.expander('Text rewriter'):
            text_file_obj = st.file_uploader('Upload the excel file with text to work on')
            if text_file_obj:
                text_file_sheets = pd.ExcelFile(text_file_obj).sheet_names
                if text_file_sheets:
                    sheet = st.selectbox('Select the sheet with data', text_file_sheets)
                    if sheet:
                        text_file = pd.read_excel(text_file_obj, sheet_name = sheet)
                        columns = text_file.columns
                        col = st.selectbox('Select a column with text to process', columns)
                        text = text_file[col].values.tolist()
                        st.write(f'There are {len(text)} blocks to work on')
            style = st.radio('Select the rewrite power:', ['hard','medium','slight'],horizontal=True, index = 1)
            if style == 'hard':
                preprompt = '''Please rewrite the following text, keeping the main idea but using different words and changing the order of sentences, if applicable. Also, please alter the style of the original text'''
            elif style == 'medium':
                preprompt = '''Please rewrite the following text, keeping the main idea but using different words and changing the order of sentences, if applicable. Also, please keep the style of the original text'''
            elif style == 'slight':
                preprompt = '''Please rewrite the following text just slightly, without greatly altering the style or the order of sentences'''

            prompt = st.text_area('If needs be, please modify the prompt for the bot:',preprompt)

            if st.button('Rewrite'):
                progress_bar = st.progress(len(text)/100,f'Please wait, working on {len(text)} blocks')
                final_rewrites = pd.DataFrame(columns = ['Original text','Rewritten text'])
                for i,t in enumerate(text):
                    messages = [
                        {'role':'user', 'content':f"{prompt}:\n{t}"}]
                    try:
                        response = openai.ChatCompletion.create(
                        model = 'gpt-3.5-turbo',
                        messages =  messages,
                        temperature=0.9,
                        max_tokens=1000
                        )
                        # Get the generated text and append it to the chat history
                        rewritten = response['choices'][0]['message']['content'].strip()
                        temp = pd.DataFrame([[t,rewritten]], columns = ['Original text','Rewritten text'])
                        final_rewrites = pd.concat([final_rewrites, temp])
                    except Exception as e:
                        st.write(f'Sorry, something went wrong for the following reason\n{e}')
                    time.sleep(0.5)
                    progress_bar.progress((i+1)/len(text),f'Rewriting block {i+1} of {len(text)}')
                st.session_state.output = BytesIO()
                with pd.ExcelWriter(st.session_state.output, engine='xlsxwriter') as writer:
                    final_rewrites.to_excel(writer, sheet_name = 'Rewriting', index = False)
                    ff.format_header(final_rewrites, writer, 'Rewriting')
                st.download_button('Download results',st.session_state.output.getvalue(), file_name = 'rewrite.xlsx')


        with st.expander('Meeting summarizer'):
            def get_meeting_summary(prompt,text, temp):
                blocks = re.split('\n| \.',text)
                word_limit = 1950               
                chunks = []
                limit = 0
                chunk = []
                for block in blocks:
                    limit += len(block.split(' '))
                    if limit < word_limit:
                        chunk += [block]
                    else:
                        limit = 0
                        chunks.append(chunk)
                        chunk = []
                chunks.append(chunk)

                if len(chunks) == 1:
                    summaries = chunks[0]
                else:
                    summaries = []
                    progress_bar = st.progress(len(chunks)/100,'Please wait...')

                    for i,c in enumerate(chunks):
                        messages = [
                            {'role':'user', 'content':f'''I am sending you the meeting summary that consists of {len(chunks)} parts. Below is part {i+1}.
                            Please compress it, removing all inconsequential details, but keep key talking points and action items, if any.
                            Please stay within 1800 words limit:\n{c}'''}]
                        response = openai.ChatCompletion.create(
                        # model="text-davinci-003",
                        model = 'gpt-3.5-turbo',
                        messages =  messages,
                        temperature=temp,
                        max_tokens=1000
                        )
                        # Get the generated text and append it to the chat history
                        message = response['choices'][0]['message']['content'].strip()
                        summaries.append(message)
                        time.sleep(5)
                    progress_bar.progress((i+1)/len(chunks),'Please wait...')
                
                #summarize
                messages = [
                    {'role':'user', 'content':f'''{prompt}\n'''+'\n\n'.join(summaries)}]
                response = openai.ChatCompletion.create(
                # model="text-davinci-003",
                model = 'gpt-3.5-turbo',
                messages =  messages,
                temperature=temp,
                max_tokens=1000
                )
                # Get the generated text and append it to the chat history
                final = response['choices'][0]['message']['content'].strip()
                messages.append({'role':'assistant','content':final})
                return final, messages
            prompt_area = st.empty()
            text_area = st.empty()
            clarify_area = st.empty()
            prompt_text = '''
Please summarize the following meeting minutes, stay detailed, but concise. Make sure to explicitly and separately list key talking points and action items, if any,  in the following format:

Summary

Key talking points:
- key talking point 1
- key talking point 2
- etc

Action items:
- action item 1
- action item 2
- etc
            '''
            prompt_query = prompt_area.text_area('Prompt',prompt_text,help = 'Modify the query if you are not getting the results you need', height = 150)
            input_text = text_area.text_area('Input meeting transcription',height = 500)
            if st.button('Summarize'):
                st.session_state.summarized = True
                try:
                    st.session_state.result, st.session_state.messages = get_meeting_summary(prompt_query,input_text, temp = 0.2)
                except Exception as e:
                    st.session_state.result = f'Sorry, an error occurred, please contact the administrator\n\n{e}'
                text_area.text_area('Summary:',st.session_state.result, height = 500)
                # if st.session_state.summarized:
                #     if st.button('Regenerate'):
                #         st.session_state.result, st.session_state.messages = get_meeting_summary(prompt_query,input_text, temp = 0.5)

                # if st.checkbox('Adjust') or st.session_state.summarized:
                #     clarification = clarify_area.text_area("Fine-tune the bot's response",'')
                #     if st.button('Adjust'):
                #         st.session_state.messages.append({'role':'user','content':clarification})
                #         response = openai.ChatCompletion.create(
                #             # model="text-davinci-003",
                #             model = 'gpt-3.5-turbo',
                #             messages =  st.session_state.messages,
                #             temperature=temp,
                #             max_tokens=1000
                #             )
                #         st.session_state.clarified = response['choices'][0]['message']['content'].strip()
                #         clarify_area.text_area('Adjusted:',st.session_state.clarified, height = 500)
                        
