from tornado import httpclient
import feedparser

def parseRSS(resp):
	feed = feedparser.parse(resp.body)
	return feed
  #   published_url =
 	# print published_url


client = httpclient.AsyncHTTPClient()
client.fetch('http://www.marketwatch.com/news/rss/YONTK', parseRSS)
