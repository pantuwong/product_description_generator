import pandas as pd
import re
from pythainlp.util import isthaichar


df = pd.read_excel('description_en_dataset.xlsx')

# description should not be too short (less than or equal 5)
# description should not be similar to product name
# product name should be only English
# description should be only English
# description should not be numeric follow by unit (short string <= 7)
# remove [....]
# start with net weight

df_out = pd.DataFrame(columns = ['product_title', 'product_description'])
for i,r in df.iterrows():
    product_title = str(r['product_title_en'])
    product_description = str(r['description_en'])

    if len(product_description) <= 5:
        continue

    if product_title.lower() == product_description.lower():
        continue

    if product_description[0].isdigit() and len(product_description[1:]) <= 7:
        continue

    if product_description.lower().startswith('net weight'):
        continue

    if product_description[0] == '[':
        continue

    found_thai = False
    for c in product_title:
        if isthaichar(c):
            found_thai = True
            break
    for c in product_description:
        if isthaichar(c):
            found_thai = True
            break
    if found_thai:
        continue

    re_words = re.compile(u"[\u4e00-\u9fa5]+")
    res = re.findall(re_words, product_title)
    if res:
        continue
    res = re.findall(re_words, product_description)
    if res:
        continue

    re_words = re.compile(u"[\uac00-\ud7ff]+") 
    res = re.findall(re_words, product_title)
    if res:
        continue
    res = re.findall(re_words, product_description)
    if res:
        continue

    re_words=re.compile(u"[\u30a0-\u30ff]+") 
    res = re.findall(re_words, product_title)
    if res:
        continue
    res = re.findall(re_words, product_description)
    if res:
        continue

    re_words=re.compile(u"[\u3040-\u309f]+")
    res = re.findall(re_words, product_title)
    if res:
        continue
    res = re.findall(re_words, product_description)
    if res:
        continue

    df_out.loc[len(df_out)] = [product_title, product_description]

df_out.to_excel('description_en_dataset_clean.xlsx', index = False)