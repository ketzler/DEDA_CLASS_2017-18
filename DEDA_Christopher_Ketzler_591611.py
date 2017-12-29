
# coding: utf-8

# In[1]:


import requests
import datetime
from progressbar import ProgressBar
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from stop_words import get_stop_words
import feedparser 

# represents an article with its important metadata
class Article:
    author = ""
    date = ""
    title = ""
    text = ""
    link = ""
    
    # constructor for the class Article
    def __init__(self,aut, dat, titl, txt, lin):
        self.author = aut
        self.date = dat
        self.title = titl
        self.text = txt
        self.link = lin
    
    # removing german stop words  
    def remove_stop_words(self, lang):
        stopWords = set(stopwords.words(lang))
        words = word_tokenize(self.text)
        wordsFiltered = []
        for w in words:
            if w not in stopWords:
                wordsFiltered.append(w)
        return(wordsFiltered)

# webscraping object for sueddeutsche.de 
class Sueddeutsche:
    
    # loading the search
    def load_search(self,searchterm):
        searchString = "http://www.sueddeutsche.de/news?search="+searchterm+        "&sort=date&dep%5B%5D=politik&dep%5B%5D=wirtschaft&dep%5B%5D=geld&typ%5B%5D=article&all%5B%5D=sys&all%5B%5D=time"
        page = requests.get(searchString)
        soup = BeautifulSoup(page.content, 'html.parser')
        searchLinks = soup.find_all('a', class_="entrylist__link")
        result= []
        for row in searchLinks:
            result.append(row["href"])
        return result

    # loading of the articles 
    def get_articles(self,links):
        result = []
        print("SZ-Bar")
        bar  = ProgressBar()
        for row in bar(links):
            page = requests.get(row)
            soup = BeautifulSoup(page.content, 'html.parser')
            body_part = soup.find(class_="body")
            header_part = soup.find(class_="header")
            text =""
            texts = body_part.find_all("p")
            for row in texts:
                text += row.get_text()
            article = Article(aut = body_part.find("span"), dat = header_part.find("time")["datetime"],                               titl = header_part.find("h2").get_text(), txt = text,                              lin = row)
            result.append(article)
        return result
    
# webscraping object for faz.net
#http://www.faz.net/suche/?offset=&cid=&index=&query=VW&offset=&allboosted=&boostedresultsize=%24boostedresultsize&from=TT.MM.JJJJ&to=09.12.2017&chkBox_2=on&chkBox_3=on&chkBox_4=on&BTyp=redaktionelleInhalte&chkBoxType_2=on&author=&username=&sort=date&resultsPerPage=20
class FAZ:
     
    # loading the search
    def load_search(self,searchword):
        now = datetime.datetime.now()
        datestring = now.strftime("%d-%m-%y")
        counter = 1
        result=[]
        while counter < 20:
            if counter == 1:
                searchString = "http://www.faz.net/suche/?offset=&cid=&index=&query="+searchword+"&offset=&allboosted=&boostedresultsize=%24boostedresultsize&from=TT.MM.JJJJ&to="+                datestring+"&chkBox_2=on&chkBox_3=on&chkBox_4=on&BTyp=redaktionelleInhalte&chkBoxType_2=on&author=&username=&sort=date&resultsPerPage=20"
            else:
                searchString = "http://www.faz.net/suche/s"+str(counter)+".html?cid=&index=&query="+searchword+                "&allboosted=&boostedresultsize=%24boostedresultsize&from=TT.MM.JJJJ&to=10-12-17&chkBox_2=on&chkBox_3=on&chkBox_4=on&BTyp=redaktionelleInhalte&chkBoxType_2=on&author=Vorname+Nachname&username=Benutzername&sort=date&resultsPerPage=20"
            page = requests.get(searchString)
            soup = BeautifulSoup(page.content, 'html.parser')
            searchLinks = soup.find_all('a', class_="TeaserHeadLink")
            for row in searchLinks:
                result.append(row["href"])
            counter += 1
        return result

    # loading of the articles
    def get_articles(self,links):
        result = []
        print("FAZ-Bar")
        print(len(links))
        bar  = ProgressBar()
        for row in bar(links):
            try:
                page = requests.get(row)
            except:
                newRow = "http://www.faz.net"+row
                page = requests.get(newRow)
            try:
                soup = BeautifulSoup(page.content, 'html.parser')
                article_part= soup.find(class_ =" atc-Text")
                text =""
                texts = article_part.find_all("p")
                for row in texts:
                    text += row.get_text()
                article = Article(aut = soup.find(class_ = "quelle"), dat = soup.find(class_ = "atc-MetaTime")["datetime"],                               titl = soup.find(class_ = "atc-HeadlineText").get_text(), txt = text,                              lin = row)
                result.append(article)
            except:
                pass
        print(len(result))
        return result


# In[2]:


# Which company do we want to search?
searchterm = "Siemens"
# webscrapping sueddeutsche.de
sued = Sueddeutsche()
links = sued.load_search(searchterm)
articleList = sued.get_articles(links)
# webscrapping faz.net
faz = FAZ()
links2 = faz.load_search(searchterm)
articleList += faz.get_articles(links2)
# removing stop words
bar  = ProgressBar()
for row in bar(articleList):
    row.text = row.remove_stop_words("german")
    print(row.text)


# In[10]:


import csv
import requests
from progressbar import ProgressBar
import fix_yahoo_finance as yf

# possible sample of searchterms for yahoo finance
Siemens = "SIE.DE"
KS = "SDF.DE"
Merck = "MRK.DE"
HeidelCem = "HEI.DE"
Henkel = "HEN3.DE"
Thyssen = "TKA.DE"
Allianz = "ALV.DE"
BMW = "BMW.DE"
Beiersdorf = "BEI.DE"
DtBank = "DBK.DE"
Lanxess = "LXS.DE"
Coba = "CBK.DE"
Conti = "CON.DE"
Basf = "BAS.DE"
Daimler = "DAI.DE"
Fresenius = "FRE.DE"
FreseniusM = "FME.DE"
Linde = "LIN.DE"
DeutBoer = "DB1.DE"
Bayer = "BAYN.DE"
VW = "VOW.DE"
Adidas = "ADS.DE"
DtPost = "DPW.DE"
SAP = "SAP.DE"
Lufth = "LHE.DE"
MRueck = "MUV2.DE"
Infineon = "IFX.DE"
Telekom = "DTE.DE"
RWE = "RWE.DE"
Eon = "EOAN.DE"
# loading the stock prices for a company
data = yf.download("SIE.DE", start="2010-01-01", end="2017-12-09")
print("\n")
print(data)

