from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime  import datetime
import requests
from bs4 import BeautifulSoup
import os 
import json
import time
import difflib
import re
from deepdiff import DeepDiff

app = Flask(__name__)

data = []
path = './downloads/'

def html_status(res):
    if res.status_code!=200:
        time.sleep(3)
        res = requests.get(url)
        print(res.status_code)
        print("website is down !")
        if res.status_code!=200:
            # create json that website is down  
            with open("website_down.json", 'w') as fp:
                webdown = {'url': url ,'status': 'website is down'}
                json.dump(webdown,fp, indent=2)

        return False
    else:
        print(res.status_code)
        print('website is working')
        return True

def fetch_html(url):
    res = requests.get(url)
    # check if url is json data 
    # if url.endswith('.json'):
    #     Jdata = res.json()
    #     urlAppend = {'URL': url}
    #     Jdata.insert(0, urlAppend)
    #     print(data)
    #     return Jdata
        
    html_status(res)

    if html_status(res) == False:
        print('still down')
    else:
        soup = BeautifulSoup(res.content, 'html.parser')
        for x in soup.recursiveChildGenerator():
            if x.name is None and not x.isspace():
                item = {
                    'tag': x.parent.name, 
                    'text': x.strip(),
                    'attrs': x.parent.attrs 
                }
                print("Crawling...")
                data.append(item)
            
        urlAppend = {'URL': url}
        data.insert(0, urlAppend)
    return data

# not complete
def check_if_file_exists(fileNmae):
    if os.path.exists(fileNmae):
        print("an older version of this files exists")

    else:
        print("This is the first time the file is being dowloaded")

def load_json(file):
    newFile = file + '.json'
    with open(newFile, 'r') as fp:
        return json.load(fp)


def write_html(path, fileName, data):  
    fullName = './' + path + '/' + fileName + '.json'
    with open(fullName, 'w') as fp:
        json.dump(data,fp, indent=2)


def comapre_files():
    with open('./downloads/20210215-193652.json') as json_file:
        file1 = json.load(json_file)

    with open('./downloads/20210301-011246.json') as json_file:
        file2 = json.load(json_file)

    ddiff = DeepDiff(file1, file2, ignore_order=True)

    differName = time.strftime("%Y%m%d-%H%M%S")

    with open("./difference/"+ differName+ ".json", 'w') as fp:
        result = json.dump(ddiff,fp, indent=2)

    return differName

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        file_content = request.form['content']
        file = time.strftime("%Y%m%d-%H%M%S")

        # ****************** write new filee ******************
        # write_html(path, file, fetch_html(file_content))
        
        filex = "./difference/" + comapre_files() 

        filediff = get_data_from_json(filex)

        return render_template('index.html', filediff=filediff)
    else:
        return render_template('index.html')


def get_data_from_json(file):
    json = load_json(file)
    newData = []
    for item in json['iterable_item_added']:
        data = json['iterable_item_added'].get(item)
        provider = data['attrs'].get('class')
        if isinstance(provider, list):
            for i in provider:
                if i == 'ontario-assessment-centre__title':
                    providerTitle = data['text']
                    print(providerTitle)
                    newData.append(providerTitle)
    print(newData)
    return newData

if __name__ == "__main__":
    app.run(debug=True)