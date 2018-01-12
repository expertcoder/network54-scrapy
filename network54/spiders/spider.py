# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
import string
from network54.items import ThreadItem, PostItem
from bs4 import BeautifulSoup, Comment, NavigableString
import json

def clean_text(text):
	if text is None:
		return ""
	text = text.strip().replace("\r", "").replace("\n", "").replace("\xa0", " ")
	text = " ".join(text.split())
	return text

def innerHTML(element):
    return element.decode_contents(formatter="html")

class SpiderSpider(scrapy.Spider):
	name = 'spider'
	allowed_domains = ['network54.com']
	start_urls = ['http://www.network54.com/Forum/TODO_MY_FORUM_ID']

	def parse(self, response):
		r =  scrapy.Request("http://www.network54.com/Forum/TODO_MY_FORUM_ID", callback=self.parse_page)
		r.meta['page'] = 1
		yield r
		for link in LinkExtractor(
				allow=('/Forum/TODO_MY_FORUM_ID/page-\d+$', ),
				allow_domains=self.allowed_domains).extract_links(response):
			r = scrapy.Request(link.url, callback=self.parse_page)
			page = int(link.url.replace("http://www.network54.com/Forum/TODO_MY_FORUM_ID/page-", ""))
			r.meta['page'] = page
			yield r
 	
	def parse_page(self, response):
		#http://www.network54.com/Forum/TODO_MY_FORUM_ID/thread/1499865412/last-1499893238/What+size+can+you+get+up+to+with+the+Flesh+Tunnels
		page = response.meta['page']
		for link in LinkExtractor(
				allow=('/Forum/TODO_MY_FORUM_ID/thread/\d+/last-.*$', ),
				allow_domains=self.allowed_domains).extract_links(response):
			item = ThreadItem()
			item['url'] = link.url
			item['title'] = link.text
			item['page'] = page
			r = scrapy.Request(link.url, callback=self.parse_thread)
			r.meta['item'] = item
			yield r
		for link in LinkExtractor(
				allow=('/Forum/TODO_MY_FORUM_ID/page-\d+$', ),
				allow_domains=self.allowed_domains).extract_links(response):
			r = scrapy.Request(link.url, callback=self.parse_page)
			page = int(link.url.replace("http://www.network54.com/Forum/TODO_MY_FORUM_ID/page-", ""))
			r.meta['page'] = page
			yield r

	def parse_thread(self, response):
		titem = response.meta['item']
		html = response.text
		soup = BeautifulSoup(html, 'lxml')
		[s.extract() for s in soup('script')]
		[s.extract() for s in soup('.signature')]
		for element in soup(text=lambda text: isinstance(text, Comment)):
			element.extract()

		for element in soup.select('.signature'):
			element.extract()
		titem['posts'] = []
		for l in soup.select('a'):
			if l.text == 'Next >':
				item = ThreadItem()
				item['url'] = l['href']
				item['title'] = titem['url']
				r = scrapy.Request(l['href'], callback=self.parse_thread)
				r.meta['item'] = item
				yield r

		posts = soup.select('center > table > tr > td[colspan=2] > table > tr > td > table > tr')
		for p in posts:
			if len(p.select('font[size=4] > h1')) > 0:
				post = PostItem()
				post['title'] = clean_text(p.select('h1')[0].text)
				post['date'] = clean_text(p.select('td > font[size=2]')[0].contents[0])
				if len(p.select('td[align=right] > font[size=1]')) > 0:
					hit = p.select('td[align=right] > font[size=1]')[0]
					name = ''.join(child for child in hit.children if isinstance(child, NavigableString) and not isinstance(child, Comment))
					post['screen_name'] =  clean_text(name)
					post['screen_name'] = post['screen_name'][:-1]
				if len(p.select('a.profile')) > 0:
					post['user_name'] = p.select('a.profile')[0].text
				post['top'] = True
				post['contents'] = innerHTML(p.select('.intelliTxt')[0])
				titem['posts'].append(post)
			elif len(p.select('font[size=2] > h1')) > 0:
				post = PostItem()
				post['title'] = clean_text(p.select('h1')[0].text)
				post['date'] = clean_text(p.select('td[align=right] > font[size=1]')[0].text)
				if len(p.select('td > font[size=2] > b')) > 0:
					post['screen_name'] = clean_text(p.select('td > font[size=2] > b')[0].text)
				if len(p.select('a.profile')) > 0:
					post['user_name'] = p.select('a.profile')[0].text
				post['contents'] = innerHTML(p.select('.intelliTxt')[0])
				titem['posts'].append(post)
				post['top'] = False
		yield titem




