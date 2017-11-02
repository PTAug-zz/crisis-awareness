
# coding: utf-8

# In[ ]:

import requests
from bs4 import BeautifulSoup
import time
import pymongo
from pymongo import MongoClient
import datetime
import pandas as pd
import nltk
from nltk.corpus import stopwords
import pymysql
from math import ceil
import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')

def get_words(url):
    words = requests.get(url).content.decode('latin-1')
    word_list = words.split('\n')
    index = 0
    while index < len(word_list):
        word = word_list[index]
        if ';' in word or not word:
            word_list.pop(index)
        else:
            index+=1
    return word_list



class sentiment_analysis():
    api_key ="02165ff998334d15b1664ecf365f2733" # http://developer.nytimes.com/article_search_v2.json#/Console/GET/articlesearch.json
    apiUrl='https://api.nytimes.com/svc/search/v2/articlesearch.json?'
    client=MongoClient()
    db = client.final_project # create db - final_project
    collection = db.articles # create collection articles
    fl='web_url,pub_date'
    p_url = 'http://ptrckprry.com/course/ssd/data/positive-words.txt'
    n_url = 'http://ptrckprry.com/course/ssd/data/negative-words.txt'
    positive_words = get_words(p_url)
    negative_words = get_words(n_url)
    invert = ["no", "never", "not"]
    StopWords = stopwords.words("english")

    def pages(self,beginDate,endDate,query):
        page = "0"
        url_built = sentiment_analysis.apiUrl + "begin_date=" + beginDate + "&end_date=" + endDate + "&api-key=" + sentiment_analysis.api_key + "&q=" + query + "&fl=" + sentiment_analysis.fl + "&page=" + page
        response = requests.get(url_built)
        json_resp = response.json()
        number_articles = json_resp['response']['meta']['hits']
        pages = int(number_articles/10)
        return pages

    def fetch_articles(self,beginDate,endDate,query):
        page = "0"
        url_built = sentiment_analysis.apiUrl + "begin_date=" + beginDate + "&end_date=" + endDate + "&api-key=" + sentiment_analysis.api_key + "&q=" + query + "&fl=" + sentiment_analysis.fl + "&page=" + page
        response = requests.get(url_built)
        json_resp = response.json()
        number_articles = json_resp['response']['meta']['hits']
        pages = int(number_articles/10)
        for page_number in range(pages+1):
            time.sleep(0.5)
            url_built = sentiment_analysis.apiUrl + "begin_date=" + beginDate + "&end_date=" + endDate + "&api-key=" + sentiment_analysis.api_key + "&q=" + query + "&fl=" + sentiment_analysis.fl + "&page=" + str(page_number)
            response = requests.get(url_built)
            if(response.status_code!=200):
                    print(response.content)
            try:
                json_resp = response.json()
            except:
                pass
            docs = json_resp['response']['docs']
            for i in docs:
                print(i)
                web_link = i['web_url']
                pub_date = int(i['pub_date'][:10].replace("-",""))
                temp_dict = {}
                try:
                    response = requests.get(web_link)
                    if(response.status_code==401):
                        print(response.content)
                    article = ''
                    page_soup = BeautifulSoup(response.content,'lxml')
                    for para in page_soup.find_all('p',{'class':'story-body-text story-content'}):
                        article = ' '.join([article, para.get_text().replace('\n','')])
                    temp_dict.update({"article":article.lower()})
                    temp_dict.update({"url":web_link})
                    temp_dict.update({"date":pub_date})
                    temp_dict.update({"country":query})
                    if(article!=''):
                        sentiment_analysis.collection.update(temp_dict, temp_dict, upsert=True)
                except:
                    pass
        print("done")


    def value_of(self,sentiment):
        if sentiment == 'pos':
            return 1
        elif sentiment == 'neg':
            return -1
        else: return 0


    def sentence_score(self,sentence_tokens, previous_token, pos_score, neg_score):
        if not sentence_tokens:
            return pos_score, neg_score
        else:
            current_token = sentence_tokens[0]
            token_score = self.value_of(current_token[1])
            if previous_token is not None:
                if previous_token[0] in sentiment_analysis.invert:
                    token_score *= -1
            if (token_score==1):
                return self.sentence_score(sentence_tokens[1:], current_token, pos_score + token_score, neg_score)
            else:
                return self.sentence_score(sentence_tokens[1:], current_token, pos_score, neg_score + token_score)



    def tag_words(self,sent_tok):
        tagged_list=[]
        for word in sent_tok:
            if word in positive_words:
                tagged_word =(word, "pos")
            elif word in negative_words:
                tagged_word =(word, "neg")
            else:
                tagged_word =(word, "")
            tagged_list.append(tagged_word)
        return tagged_list

    def takespread(sequence, num):
        length = float(len(sequence))
        for i in range(num):
            yield sequence[int(ceil(i * length / num))]

    def create_sql(self):
        db = pymysql.connect("localhost","root","password","final_project")
        cursor = db.cursor()
        cursor.execute("create table afghanistan (date int, mentions int, positivity float, negativity float)")
        db.commit()

    def analyse_Articles(self,beginDate,endDate,query):

        db = pymysql.connect("localhost","root","password","final_project")
        cursor = db.cursor()
        d1 = datetime.datetime.strptime(beginDate, '%Y%m%d').date()
        d2 = datetime.datetime.strptime(endDate, '%Y%m%d').date()
        dd = [int((d1 + datetime.timedelta(days=x)).strftime("%Y%m%d")) for x in range((d2-d1).days + 1)]

        df = pd.DataFrame(0,index=dd,
                  columns=["Country","Mentions","Positivity","Negativity","Year"])
        dtype={'Country':'object', 'Mentions':'int64','Positivity':'float64', 'Negativity':'float64','Year':'int64'}
        for k, v in dtype.items():
            df[k] = df[k].astype(v)

        for i in dd:
            print(i)
            mentions=0
            pos=0
            neg=0
            tot_wordcount = 0
            articles = sentiment_analysis.collection.find({"date":i, "country": query})
            for doc in articles:
                mentions = doc["article"].count(query) + mentions
                sentences = nltk.sent_tokenize(doc["article"])
                tot_wordcount = len(doc["article"]) + tot_wordcount
                tokenized_doc = [[word for word in nltk.word_tokenize(sentence) if word not in sentiment_analysis.StopWords] for sentence in sentences]
                tagged_doc = [self.tag_words(sent_tok) for sent_tok in tokenized_doc]
                positivity = 0
                negativity = 0
                for sent_tok in tagged_doc:
                    positivity, negativity = self.sentence_score(sent_tok,None,0,0)
                    pos = positivity + pos
                    neg = negativity + neg
            df.set_value(i, "Country", query)
            df.set_value(i, 'Mentions', mentions)
            df.set_value(i, 'Positivity', pos)
            df.set_value(i, 'Negativity', neg)
            df.set_value(i, 'Year', int(str(i)[0:6]))

        df = df[df.Mentions !=0].reset_index(drop=True)

        df = df.groupby(['Year']).agg({'Mentions': ['sum'], 'Positivity': ['mean'],'Negativity': ['mean']})
        df.columns = df.columns.droplevel(1)
        df = df.reset_index(level=['Year'])

        df["Positivity"]=df["Positivity"]/df["Positivity"].max()
        df["Negativity"]=df["Negativity"]/df["Negativity"].min()


        for index, row in df.iterrows():
            cursor.execute("""INSERT INTO afghanistan VALUES (%s,%s,%s,%s)""",(int(row["Year"]),int(row["Mentions"]),float(row["Positivity"]),float(row["Negativity"])))
        db.commit()

    def takespread(self, sequence, num):
        length = float(len(sequence))
        for i in range(num):
            yield sequence[int(ceil(i * length / num))]

    def plotter(self, country):
        db = pymysql.connect("localhost","root","password","final_project")
        cursor = db.cursor()
        cursor.execute("select * from %s", country)
        a = cursor.fetchall()
        df = pd.DataFrame(list(a[i] for i in range(len(a))), columns=['Date', 'Mentions', 'Negativity','Positivity'])
        ticks = takespread(list(df["Date"]),10)
        plt.xticks(range(len(df["Positivity"])),ticks,rotation=45)
        plt.plot(df['Negativity'],color="red")
        plt.plot(df['Positivity'],color="green")
        plt.locator_params(nbins=10)
        plt.show()

