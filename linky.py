from apscheduler.schedulers.background import BackgroundScheduler
from pytrends.request import TrendReq
from  googlesearch import search
import re
from GoogleNews import GoogleNews
import nltk
from nltk.chunk import conlltags2tree, tree2conlltags
import urllib.request
from urllib.parse import urlparse
import heapq
import bs4 as bs
from collections import Counter
from datetime import datetime

class Linky():
	def __init__(self):
		self.trends = "trends"
		self.links = "links"
		self.images = "images"
		self.headlines = "headlines"
		self.timings = "timings"
		self.scheduler = BackgroundScheduler(daemon=True)
		self.setup()
		
		
	def setup(self):
		self.scheduler.add_job(self.update_trends)
		self.scheduler.start()
		
	def update_trends(self):
		while True:
			self.find_trends()

	def find_trends(self):
		trends = {}
		links = {}
		headlines = {}
		images = {}
		timings = {}

		pytrends = TrendReq(hl='en-UK', tz=360)
		
		searches = pytrends.trending_searches(pn='united_kingdom')
		#pytrends returns a Dataframe.
		headlines_ = []

		for trend in searches.iterrows():
			payload = str(trend[1][0])
			print(payload)
			urls = []
			for url in search(payload, start=1, stop=5, tld='com',tbs='qdr:d', tpe='nws', safe=True):
				urls.append(url)

			image_link = self.get_image_link(payload)
			data, urls_  = self.summarise(urls)
			headline = ""
			if data != False:
				trends[payload] = data
				links[payload] = urls_
				headlines[payload] = headline
				images[payload] = image_link
				timings[payload] = datetime.now()
		self.trends = trends
		self.links = links
		self.headlines = headlines
		self.images = images
		self.timings = timings

	def news(self, payload):
		google_news = GoogleNews(lang='en', start=self.now, end=self.now)
		google_news.search(payload)
		urls = google_news.result()
		return urls

	def get_image_link(self, payload):
		url =  ""
		for result in search(str(payload), start=1, stop=1, tld='com',tbs='qdr:d', tpe='isch', safe=True):
			url = result
		#scraped_data = urllib.request.urlopen(url)
		#article = scraped_data.read()
		
		#parsed_article = bs.BeautifulSoup(article, 'lxml')
		#img = parsed_article.find('img')
		#img_url = img['src']
		img_url =""
		return {'img_url':img_url, 'article_url':url}

	def headline_chunk(self, headline):
		#f = conlltags2tree()
		headline_tagged = tree2conlltags(headline)
		nltk.ne_chunk()

	def noun_phrase_chunking(self, phrase):
		pattern = 'NP: {<DT>?<JJ>*<NN>}'
		parser = nltk.RegexpParser(pattern)
		cs = parser.parse(phrase)
		return cs

	def preprocess_headlines(self, head):
		head_ = nltk.word_tokenize(head)
		head_  = nltk.pos_tag(head_)
		return head_

	def preprocess_paragraph(self, article_text):
		#remove references
		article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
		# removes square brackets and replaced with single spaces.
		article_text = re.sub(r'\s+', ' ', article_text)
		return article_text

	def summarise(self,urls):
		article_text = ""
		urls_ = []
		headlines_ = []
		for url in urls:
			try:
				scraped_data = urllib.request.urlopen(url)
				article = scraped_data.read()

				parsed_article = bs.BeautifulSoup(article, 'lxml')

				paragraphs = parsed_article.find_all('p')
				headlines = parsed_article.find_all('h1')
				for headline in headlines:
					headlines_ .append(headline)

				if paragraphs:
					base_url = urlparse(url)
					base_url = '{uri.scheme}://{uri.netloc}'.format(uri=base_url)
					urls_.append({'base': base_url,'full':url})
				for p in paragraphs:
					article_text += p.text
			except:
				pass

		article_text = self.preprocess_paragraph(article_text)

		#the following are used to create wegihted frequency histograms.
		formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text)
		formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)

		# tokensization into sentences.

		sentence_list = nltk.sent_tokenize(article_text)

		#find weighted frequency of occurence.
		stop_words = nltk.corpus.stopwords.words('english')

		word_frequencies = {}

		for word in nltk.word_tokenize(formatted_article_text):
			if word not in stop_words:
				if word not in word_frequencies.keys():
					word_frequencies[word] = 1
				else:
					word_frequencies[word] += 1
		if len(word_frequencies) > 0:
			max_frequency = max(word_frequencies.values())

			for word in word_frequencies.keys():
				word_frequencies[word] = (word_frequencies[word]/max_frequency)

			sentence_scores = {}
			for sent in sentence_list:
				for word in nltk.word_tokenize(sent.lower()):
					if word in word_frequencies.keys():
						if len(sent.split(' ')) < 30:
							if sent not in sentence_scores.keys():
								sentence_scores[sent] = word_frequencies[word]
							else:
								sentence_scores[sent] += word_frequencies[word]
			try:	
				summary_sentences = heapq.nlargest(5, sentence_scores, key=sentence_scores.get)
				return summary_sentences, urls_
			except:
				return False, False
		
	#named entityRecognition
	#sentiment analysis
	#text summarization
	#aspect mining
	#topic modeling

#extractive

#abstractive