# importing libraries
import fireworks.client
import base64
import json
import streamlit as st
import psycopg2
import string

from PIL import Image
from pdf2image import convert_from_path

# driver function
def dexter(file: str):
  """
  function: feeds a file to the LLM to classify the document into one of the
  given categories

  input: file

  output: category of document
  """
  file_name = file.split(".")[0]
  file_extension = file.split(".")[-1]

  # checking for file extension and processing accordingly
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

# image encoder
def encode_image(image_path):
  """
  function: encoding image in base64 format

  input: image path

  output: encoded image
  """
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# LLM model
def model(filename: str) -> str:
  """
  function: performs LLM inferencing on the given image

  input: file

  output: response generated by the LLM
  """
  docs = [
    "birth certificate",
    "driving license",
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

  api = st.secrets["keys"]
  fireworks.client.api_key = api["fireworks"] # need to hide this

  response = fireworks.client.ChatCompletion.create(
    model = "accounts/fireworks/models/firellava-13b",
    messages = [
      {
      "role": "system",
      "content": f"You are an AI Assistant expert in classifying documents into one of the following categories: {docs}"
      },
      {
      "role": "user",
      "content": [{
        "type": "text",
        "text":  f"""Analyze the image and classify it into one of the following categories: {docs}. Just print the classified category name.""",
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
  return output

# stream lit app title
st.title("Dexter: A Document Database")

def get_db_connection():
    """
    function: get database configuration info

    input: none

    output: database configuration
    """
    # Accessing secrets from .streamlit/secrets.toml
    db_config = st.secrets["database"]
    return psycopg2.connect(
        dbname=db_config["database"],
        user=db_config["username"],
        password=db_config["password"],
        host=db_config["host"],
        port=db_config["port"]
    )
# initiating connection
conn = get_db_connection()

# repetition check
def check_filename(filename):
   """
   function: checks if the file is already present in the database

   input: file

   output: true if file exists, false if it doesn't
   """
   with conn.cursor() as cur:
      query = """
      SELECT 1 FROM records WHERE filename = %s
      """
      cur.execute(query, (filename,))
      return cur.fetchone() is not None

# data insertion
def insert_data(data, file_name):
  """
  function: inserts a row in the database

  input: llm response, filename

  output: none, writes entry to the database
  """
  if check_filename(file_name):
     st.write(f"File {file_name} already exists in the database. Skipping insertion.")
  with conn.cursor() as cur:
      query = """
      INSERT INTO records (filename, category)
      VALUES (%s, %s)
      """
      cur.execute(query, (file_name, data.lower()))
      conn.commit()
      st.write("Successfully Written to Database")

# processing uploaded documents
def processDocuments(files):
  """
  function: processes uploaded documents and performs data insertion

  input: files

  output: none, writes data to the database
  """
  if files:
    for file in files:
      # storing file name
      file_name = file.name

      # storing the file in directory
      with open(f"uploads/{file_name}", "wb") as f:
        f.write(file.getbuffer())
      
      res = dexter(f"uploads/{file_name}")
      res = res.translate(str.maketrans('', '', string.punctuation))
      insert_data(res, file_name)
  else:
    st.write("No files uploaded. Please upload a file!")

# upload document section
st.title("Upload Document")

if 'files' not in st.session_state:
    st.session_state.files = 0

uploaded_files = st.file_uploader("Choose a file", accept_multiple_files = True)
if uploaded_files:
    st.session_state.files = uploaded_files

if st.button("Submit"):
   processDocuments(uploaded_files)

# query database section
st.title("Query Database")
docs = [
  "birth certificate",
  "driving license",
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
option = st.selectbox(
    "Select Document Type",
    docs)

# fetching data from database
def fetch_entries(category):
    """
    function: fetches data from database based on the category of document

    input: category

    output: prints documents corresponding to the category to the app
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = f"""
            SELECT *
            FROM records
            WHERE category = %s
            """
            cur.execute(query, (category,))
            return cur.fetchall()
    except:
       st.write(f"No file with category {category} in database.")
    finally:
        conn.close()

if st.button("Fetch"):
   query_results = fetch_entries(str(option))
   for res in query_results:
      st.write(f"Filename: {res[0]}, Category: {res[1]}")