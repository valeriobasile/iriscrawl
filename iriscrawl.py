#!/usr/bin/env python

import yaml
import requests
from bs4 import BeautifulSoup
import tempfile
import pandas as pd
import numpy as np
import re

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
list_url = config['url']+"/browse"

args = {
    'type':'author',
    'authority':config['userid'],
    'sort_by':2,
    'order':config['order'],
    'rpp':100,
    'etal':0,
    'submit_browse':'Update'
}

response = requests.get(list_url, args)
soup = BeautifulSoup(response.text, 'html.parser')
item_ids = [item['value'] for item in soup.find_all(attrs={"name": "item_id"})]

export_url = config['url']+"/references"
args = {
    'format': 'excel',
    'item_id': item_ids
}

headers = {"Accept-Language": "en-US,en"}
response = requests.get(export_url, args, headers=headers)

with open('fields.txt') as f:
    fields = [line.strip() for line in f]

with tempfile.NamedTemporaryFile() as temp:
    temp.write(response.content)
    
    df = pd.read_excel(temp.name, dtype=object)

df = df.replace(np.nan, '', regex=True)
df.columns = fields

with open('template.txt') as f:
    template = f.read()

for index, entry in df.iterrows():
    entry_clean = {k: v.strip().replace('\n', ' ') for k, v in dict(entry).items()}
    full_entry = template.format(**entry_clean)
    full_entry_clean = re.sub(r'\n *', '\n', full_entry)
    full_entry_clean = re.sub(r' *\n', '\n', full_entry_clean)
    full_entry_clean = re.sub(r'\n+', '\n', full_entry_clean)
    print (full_entry_clean)

