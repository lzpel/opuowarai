import webapp2

import moto
from google.appengine.ext import ndb
from datetime import datetime,timedelta
from logging import info


class word(ndb.Model):
	text=ndb.StringProperty()
	kind=ndb.StringProperty()


class tweet(ndb.Model):
	text=ndb.StringProperty()
	words=ndb.LocalStructuredProperty(word,repeated=True)


class base(moto.base):
	tweets=ndb.LocalStructuredProperty(tweet,repeated=True)


class work(moto.workhandler):
	def work(s,i,o):
		if i.path=="/":
			s.o.template="home.html"
			# 出力
			s.o.univ=base.query(base.anal=="univ").fetch()
		if i.path=="/admn":
			s.o.template="admn.html"
			# 出力
			s.o.main=base.query(base.anal=="admn").get()
			s.o.univ=base.query(base.anal=="univ").fetch()
			if not s.o.main:
				s.o.main=base(anal="admn")
				s.o.main.put()
		if i.path=="/cnf":
			t=base.query(base.anal=="admn").get()
			if not t:
				t=base(anal="admn")
			t.populate(text=i.text,mail=i.mail,word=i.word,icon=i.icon,head=i.head,size=int(i.size))
			t.put()
			s.o.redirect="/admn"
		if i.path=="/set":
			t=base.getbyid(s.i.iden)
			if t:
				if i.delete:
					t.key.delete()
				else:
					t.populate(mail=i.mail,word=i.word,name=i.name,text=i.text)
					t.put()
			s.o.redirect="/admn"
		if i.path=="/clr":
			univ=base.query(base.anal=="univ").fetch()
			for i in univ:
				i.tweets=[]
			ndb.put_multi(univ)
		if i.path=="/add":
			if i.name:
				base(anal="univ",name=i.name,mail=i.mail,word=i.word).put()
				s.o.redirect="/admn"
		if i.path=="/recv":
			s.o.template="json"
			# order(+時刻)が古い順
			univ=base.query(base.anal=="univ").order(+base.last).get()
			main=base.query(base.anal=="admn").get()
			o.google_key=main.text
			o.twitter_key=main.mail
			o.twitter_sec=main.word
			o.ready=univ and univ.last<datetime.now()-timedelta(minutes=main.size)
			if o.ready:
				univ.put()
			if univ:  # デバッグの為
				o.id=univ.key.id()
				o.account_key=univ.mail
				o.account_sec=univ.word
				o.keywords=(univ.text or "").split()
				o.words=[]
				for tmp in univ.tweets:
					o.words.append(("",""))
					for j in tmp.words:
						o.words.append((j.kind,j.text))
				o.words.append(("",""))
		if i.path=="/send":
			j=i.json()
			univ=base.getbyid(j["id"])
			for i in j["tweets"]:
				univ.tweets.append(tweet(text=i["text"],words=[word(text=w[1],kind=w[0]) for w in i["words"]]))
			univ.tweets=univ.tweets[-100:]
			univ.put()


app=webapp2.WSGIApplication([('/.*',work)])
