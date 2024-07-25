# Dexter ![project-stage-badge: Development](https://img.shields.io/badge/Project%20Stage-Development-yellowgreen.svg)

Dexter is a document database. Given a document, Dexter will automatically classify it into one of the given categories and store it in the database. You can upload multiple files at once and click "Submit", and Dexter will do the rest.

# Workflow
<p align = "center"><img src = "https://github.com/user-attachments/assets/6bece8d4-64a9-42fe-a3ac-c209e5c0608e"></p>

1. Document Upload: The user uploads single or multiple documents on the Streamlit app
2. Document Processing: Depending on the number of documents uploaded and the kind of documents uploaded (.pdf, .jpg, .png, .tif), Dexter processes the documents
3. LLM: Dexter employs the LLaVa 13B vision language model to classify the documents uploaded into one of the categories pre-defined in Dexter. The LLM inference is conducted using <a href = "https://fireworks.ai/">Fireworks-AI</a>
4. PostgreSQL: Once the category of a document is defined, the document is added to the database using SQL. The documents can be retrieved as well.

## Demo
<p align = "center"><a href = "https://www.youtube.com/watch?v=ngD0vXelB-w"><img src = "https://img.youtube.com/vi/ngD0vXelB-w/0.jpg"></a></p>


## Setup

NOTE: Since this app is still not deployed yet, it requires the user to setup a PostgreSQL database on their local machine before running the demo. You can follow this <a href = "https://www.youtube.com/watch?v=qw--VYLpxG4&t=2539s">tutorial</a> to setup PostgreSQL. Once the setup is completed, create a database with name "dexterdb" and add a table named "records" with "filename" and "category" as columns.

1. On your local machine, open the terminal and create a virtual environment
```python
python3 -m venv dexter
```

2. Activate the virtual environment
```python
source dexter/bin/activate
```

3. Install dependencies
```python
pip3 install -r requirements.txt
```

4. Dexter uses a library named ```pdf2image```. This library has some dependencies whose installation varies according to the OS you are using. You can follow the steps given <a href = "https://github.com/Belval/pdf2image">here</a>

5. Once all the dependencies are installed, in the main project directory, add the following folder:
```python
.streamlit/
```
This folder will store your database configuration information and your fireworks-ai api key.

6. Add a file ```secrets.toml``` file in the ```.streamlit/``` folder. Inside ```secrets.toml``` file, add the following information:
```python
[database]
dialect = "postgresql"
host = "localhost"
port = "5432"
database = "dexterdb"
username = "<username>"
password = "<password>"

[keys]
fireworks = "<api_key>"
```

7. Finally, from the terminal, run:
```python
streamlit run app.py
```

