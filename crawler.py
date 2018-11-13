from urllib.request import urlopen
from bs4 import BeautifulSoup
from newspaper import Article
import json
import nltk
import sys,re
nltk.download('punkt')

class Crawler:
    def __init__(self,url):
        self.url = url
        self.is_downloaded=False
        self.content = ""
        # stucture 
        self.gatheredData = {
        "website_link": self.url,
        "links":[],
        "content":"",
        "content_html":"",
        "content_keywords":"",
        "summary":"",
        "meta_title":"", 
        "meta_desc":"",
        "meta_keywords":"",
        "top_image":""
        }
        self.initCrawl()

    def initCrawl(self):
        self.is_downloaded=self.initDownloadContent()
        if(self.is_downloaded):
            self.parseMetaData()
        else:
            raise ValueError('Seems Something Wrong with URL')     
        
    def initDownloadContent(self):
        try:
            html = urlopen(self.url)
            self.content = html
            return True
        except:
            return False

    def parseMetaData(self):
        soup = BeautifulSoup(self.content, 'lxml')        
       
        #read title tag
        title = soup.title  
        self.gatheredData["meta_title"] = title.getText() or ""
       
        #read href links and texts
        for singleText in soup.find_all('a'):
            self.gatheredData["links"].append({
            "link_text":BeautifulSoup(str(singleText), "lxml").get_text(),
            "link_href":singleText.get('href'),
            "link_alt":singleText.get('alt')
            })

        #read meta desc and keyword
        for meta in soup.findAll("meta"):
            metaname = meta.get('name', '').lower()
            metaprop = meta.get('property', '').lower()
            if 'description' == metaname or metaprop.find("description")>0:
                self.gatheredData["meta_desc"] = meta['content'].strip()
            if 'keywords' == metaname or metaprop.find("keywords")>0:
                self.gatheredData["meta_keywords"] = meta['content'].strip()
        #read the content 
        self.parseContent()
        
    def parseContent(self):
        article = Article(self.url)
        article.download()
        article.parse()
        article.nlp() 
        self.gatheredData["summary"] = article.summary
        self.gatheredData["content"] = article.text
        self.gatheredData["content_html"] = article.article_html
        self.gatheredData["top_image"] = article.top_image
    
    def getJSON(self):
        if(self.is_downloaded):
            return json.dumps(self.gatheredData,indent=4, sort_keys=True)
        else:
            return json.dumps({"error":"URL  InValid / Download Error"})

# Validated URL
def validateURL(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None  

# SampleCode Objects
if(len(sys.argv) == 2):
    url= sys.argv[1]
    if(url): 
        if(validateURL(url)):   
            newSite = Crawler(url)
            data = newSite.getJSON()
            print(data)
        else:
           print("URL Invalid")
    else:
           print("URL Parameter missing!")


