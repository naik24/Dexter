import fireworks.client
import base64
import json
from PIL import Image
from pdf2image import convert_from_path

def dexter(file: str):
  file_name = file.split(".")[0]
  file_extension = file.split(".")[-1]

  if file_extension == 'jpg' or file_extension == 'jpeg' or file_extension == 'png':
    result = model(file)
  elif file_extension == 'tif':
    tif_file = Image.open(file)
    tif_file.save(f"{file_name}.jpeg")
    result = model(f"{file_name}.jpeg")
  elif file_extension == 'pdf':
    images = convert_from_path(file)
    first_page = images[0].convert('RGB')
    first_page.save(f"{file_name}.jpeg")
    result = model(f"{file_name}.jpeg")
  else:
    print("Please upload a valid file")
    return

  return result

# Helper function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def model(filename: str) -> str:
  docs = [
    "birth certificate",
    "driving licence",
    "passport",
    "resume",
    "report",
    "memo",
    "death certificate",
    "letter",
    "statement",
    "contract",
    "adhaar card",
    "social security number"
  ]
  file_extension = filename.split(".")[-1]
  image_base64 = encode_image(filename)

  fireworks.client.api_key = "hTmLdao0XGOLNQvqvOmDVPUgrd6LJb8hy6DBAJlbtoOT16wr" # need to hide this

  response = fireworks.client.ChatCompletion.create(
    model = "accounts/fireworks/models/firellava-13b",
    messages = [
      {
      "role": "system",
      "content": f"You are an AI Assistant expert in classifying documents into one of the following categories: {docs}. Also, print the organization to whom the document belongs."
      },
      {
      "role": "user",
      "content": [{
        "type": "text",
        "text":  f"""Analyze the image and classify it into one of the following categories: {docs}. Just print the category and organization to whom the document belongs. Print the output strictly in JSON format.""",
        },
        {
        "type": "image_url",
        "image_url": {
          "url": f"data:image/{file_extension};base64,{image_base64}"
          },
        },],
      }],
  )
  output = response.choices[0].message.content

  # converting output to json
  #
  output = json.loads(output)
  return output

import streamlit as st

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    st.write(bytes_data)