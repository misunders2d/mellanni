from openai import OpenAI
import base64, time
import streamlit as st
from PIL import Image, ImageOps
from io import BytesIO
from random import randint

import os, re

st.set_page_config(page_title = 'Competitor analysis', page_icon = 'media/logo.ico',layout="wide",initial_sidebar_state = 'collapsed')


API_KEY = os.getenv('GPT_VISION_KEY')
KEEPA_KEY = os.getenv('KEEPA_KEY')
HEIGHT = 250

input_tokens = 0
output_tokens = 0
PROMPT = """You are supplied with an image of a bedroom.
As a bedding designer and expert please suggest the best color option for this specific bedroom - the bed will typically consist of a set of pillowcases, flat sheet, fitted sheet,
bedskirt (if applicable) and a coverlet (if applicable). Please choose one best option and describe it in detail as if you were generating a prompt for an image-genearting model.
Please notify me if the image is not the one of a bedroom."""

def resize_image(image_obj):
    full_image = Image.open(image_obj)
    cropped_image = ImageOps.contain(full_image, (512,512))
    return cropped_image

def convert_image_to_bytes(image_obj):
    img_byte_arr = BytesIO()
    image_obj.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def encode_image(image_path):
    if isinstance(image_path, str):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    elif isinstance(image_path, bytes):
        return base64.b64encode(image_path).decode('utf-8')

def describe_image(image_bytes):
    global input_tokens, output_tokens
    time.sleep(randint(30,70)/10)

    message: list = [
        {"role": "user","content":
          [{"type": "text","text": PROMPT},
          {"type": "image_url",
           "image_url":{
               "url": f"data:image/jpeg;base64,{image_bytes}",
               "detail":"high"}
               }]
          }]
    
    client = OpenAI(api_key = API_KEY)

    response = client.chat.completions.create(
      model="gpt-4-vision-preview",
      messages = message,
      max_tokens=600,
      temperature = 0.0,
      n = 1,
      stream=False
    )
    
    stop = response.choices[0].finish_reason
    if stop == 'stop':
        description = response.choices[0].message.content
    else:
        st.write(stop)
        description = 'There was an error, please try again.'
    input_tokens += response.usage.prompt_tokens
    output_tokens += response.usage.completion_tokens
    
    return description

image_input= st.file_uploader('Upload your image')
if image_input:
    resized_image = resize_image(image_input)
    byte_image = convert_image_to_bytes(resized_image)
    st.session_state.encoded_image = encode_image(byte_image)
    st.image(resized_image)
if 'encoded_image' in st.session_state:
    if st.button('Refine'):
        st.session_state.result = describe_image(st.session_state.encoded_image)

if 'result' in st.session_state:
    st.write(st.session_state.result)
    st.write(f'Total tokens used: {input_tokens + output_tokens}. Estimated cost: ${(input_tokens * 10 / 1000000) + (output_tokens * 30 / 1000000):.3f}')
