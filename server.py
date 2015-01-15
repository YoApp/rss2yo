from tornado import ioloop, web, escape, gen, httpclient #install
from MySQLdb import OperationalError
import torndb #install
import feedparser #install
import sys
import time
import datetime
import dateutil.parser as parser #install
import os


print "restarted"

def checkRSS(entry):
    # print 'checking'
    def parseRSS(resp):
        try:
            feed = feedparser.parse(resp.body)
            source = entry['url'].split('.')[1]

            
            if entry['datetime'] != '':
                entry_datetime = entry['datetime']
                entry_url = entry['lastid']
                published_time = feed['items'][0]['published']
                published_url = feed['items'][0]['link']
                if parser.parse(entry_datetime) < parser.parse(published_time) and published_url != entry_url:


                    client = httpclient.HTTPClient()
                    req = httpclient.HTTPRequest("http://newapi.justyo.co/yoall/", method='POST', body="api_token="+entry['apikey']+"&link="+feed['items'][0]['link'])
                    resp = client.fetch(req)

                    if 'link' in feed['items'][0]:
                        id = feed['items'][0]['link']
                    elif 'id' in feed['items'][0]:
                        id = feed['items'][0]['id']
                    elif 'title' in feed['items'][0]:
                        id = feed['items'][0]['title']

                    date = feed['items'][0]['published']
                    print 'mysql updated'
                    print entry['id']
                    print '{} sent {}'.format(source, feed['items'][0]['link'])
                    mysql.execute("UPDATE feeds SET datetime=%s, lastid=%s WHERE id=%s", date, published_url, entry['id'])
            else:
                print 'else'
                if 'link' in feed['items'][0]:
                    id = feed['items'][0]['link']
                elif 'id' in feed['items'][0]:
                    id = feed['items'][0]['id']
                elif 'title' in feed['items'][0]:
                    id = feed['items'][0]['title']

                entry_url = entry['lastid']
                link = feed['items'][0]['link']

                if entry['lastid'] != id and entry_url != link:
                    # print("new")
                    print '{} sent {}'.format(source, feed['items'][0]['link'])
                    #Send the Yo
                    client = httpclient.HTTPClient()
                    # print 'New feed item found for {}'.format(apikey)
                    date = feed['items'][0]['published']
                    req = httpclient.HTTPRequest("http://newapi.justyo.co/yoall/", method='POST', body="api_token="+entry['apikey']+"&link="+feed['items'][0]['link'])

                    mysql.execute("UPDATE feeds SET datetime=%s, lastid=%s WHERE id=%s", date, link, entry['id'])
        except Exception as e:
            print "Err1 {} {}".format(e, entry)
            pass


    try:
        client = httpclient.AsyncHTTPClient()
        client.fetch(entry['url'], parseRSS)
    except Exception as e:
        print 'Err2 {} {}'.format(e, entry)
        pass




@gen.engine
def crawlRSS():
    # print("here")
    mysql.reconnect()
    try:
        res = mysql.query("SELECT * FROM feeds")
    except OperationalError:
        mysql.reconnect()
        res = []
        print 'failed connection'
    finally:
        for entry in res:
            try:
                checkRSS(entry)
            except Exception as e:
                print(e)
                pass

        # print "waiting"
        yield gen.Task(ioloop.IOLoop.instance().add_timeout, time.time() + 30)
        print 'crawling'
        crawlRSS()



class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("pages/index.html")

    def post(self):
        self.add_header("Content-Type:", "application/json")

        url = self.get_argument("url", strip=True)
        apikey = self.get_argument("apikey", strip=True)

        q = mysql.query("SELECT * FROM feeds WHERE apikey=%s AND url=%s", apikey,url)


        if len(q) != 0:
            self.write('{"error":"Already exists"}')
            return

        query = mysql.query("SELECT * FROM feeds WHERE apikey=%s", apikey)
        if len(query) >= 10:
            self.write('{"error":"Too many broadcasts."}')
            print "TOO MANY BROADCASTS FOR {}".format(apikey)
            return

        #print(q)


        #print(url, apikey)

        if apikey == '' or url == '':
            self.write('{"error":"Pleae don\'t leave blank fields"}')
            return

        try:
            f =feedparser.parse(url)
        except Exception :
            self.write('{"error":"Could not connect to RSS Feed"}')
            return


        if 'bozo_exception' in f:
            self.write('{"error":"Error: Could not parse RSS Feed"}')
            return

        if len(f['items']) != 0:

            if 'published' in f['items'][0]:
                published = f['items'][0]['published']
            else:
                published = ''


            if 'link' in f['items'][0]:
                id = f['items'][0]['link']
            elif 'id' in f['items'][0]:
                id = f['items'][0]['id']
            elif 'title' in f['items'][0]:
                id = f['items'][0]['title']
            else:
                self.write('{"error":"Could not parse RSS Feed - Required title tag not found."}')
                return

            row = mysql.execute("INSERT INTO feeds VALUES (0, %s, %s, %s, %s)", url, apikey, published, f['items'][0]['link'])

            self.write('{"success":true}')





        else:
            self.write('{"error":"RSS Feed did not appear to have any items in it."}')
            return




class DeleteFeeds(web.RequestHandler):

    def post(self):
        print("DELETING")
        apikey = self.get_argument("apikey", None, True)
        if apikey == None or apikey == '':
            self.write('{"error":"API Key must not be blank"}')
            return

        row = mysql.execute("DELETE FROM feeds WHERE apikey=%s", apikey)
        #print(row)
        self.write('{}')

try:
    #Connect to SQL
    mysql = torndb.Connection("us-cdbr-iron-east-01.cleardb.net", "heroku_1b6ef821ac71ff5", user="bb1624dc5468e6", password="4293f1a6")
    print 'connected'
    q = open("feeds.sql").read()
    try:
        pass
        #mysql.execute(q)
    except Exception:
        print "table already exists"

except Exception as e:
    print(e)

app = web.Application([
     (r'/', IndexHandler),
    (r'', IndexHandler),
    (r'/delete', DeleteFeeds),
    (r'/delete/(.*)', DeleteFeeds),
    (r'/static/(.*)', web.StaticFileHandler, {'path': "static"}),
], debug=True)

if __name__ == '__main__':
    app.listen(int(os.environ.get('PORT', '5000')))
    crawlRSS()
    ioloop.IOLoop.instance().start()


