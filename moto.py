# coding=utf-8
import os,json,urllib,time,datetime,math,re
import webapp2
from google.appengine.ext.webapp import template,blobstore_handlers,RequestHandler
from google.appengine.api import app_identity,mail,memcache
from google.appengine.ext import blobstore,ndb

try:
	# gae向けのrequests
	import requests
	import requests_toolbelt.adapters.appengine
	requests_toolbelt.adapters.appengine.monkeypatch()
except:
	pass


class base(ndb.Model):
	# default未使用低容量
	# 他から計算できる情報は保存しない。コメントマイリス数
	# 時刻
	bone=ndb.DateTimeProperty(auto_now_add=True)
	last=ndb.DateTimeProperty(auto_now=True)

	# 分類
	cate=ndb.StringProperty(default=u"what")

	# 関係検索用
	kusr=ndb.KeyProperty()  # 作者
	kint=ndb.KeyProperty()  # 米等の対象物
	kner=ndb.KeyProperty(repeated=True)
	kfar=ndb.KeyProperty(repeated=True)

	# 文章検索用
	name=ndb.StringProperty()
	text=ndb.TextProperty()
	mail=ndb.StringProperty()
	word=ndb.StringProperty()
	tags=ndb.StringProperty(repeated=True)

	# 整列用
	int0=ndb.IntegerProperty()
	int1=ndb.IntegerProperty()
	int2=ndb.IntegerProperty()
	intA=ndb.IntegerProperty()
	intB=ndb.IntegerProperty()
	intC=ndb.IntegerProperty()

	# ファイル
	blob=ndb.BlobKeyProperty(repeated=True)

	# JSON
	json=ndb.JsonProperty()

	@classmethod
	def getbyid(c,i,m=True):
		k=ndb.Key(c,int(i))
		if m: k=k.get()
		return k

	@classmethod
	def _pre_delete_hook(c,k):
		s=k.get()
		# delete blob
		blobstore.delete(s.blob)
		# delete kusr,kint
		ndb.delete_multi(base.query(ndb.OR(base.kusr==s.key,base.kint==s.key)).fetch(keys_only=True))


# https://cloud.google.com/appengine/docs/standard/python/blobstore/
class blobhandler(RequestHandler):
	def get(s,blob):
		s.response.headers.add_header('X-AppEngine-BlobKey',blob)
		if "Range" in s.request.headers:
			r=re.findall(r"\d+",s.request.headers['Range'])
			r0=int(r[0])
			r1=int(r[1]) if len(r)>=2 else r0+1048576
			s.response.headers.add_header('X-AppEngine-BlobRange',"bytes={0}-{1}".format(r0,r1))


class datainput:
	def __init__(s,handler):
		s.h=handler

	def __getattr__(s,k):
		r=vars(s)["h"].request
		if k=="hosturl":
			return r.host_url
		if k=="path":
			return r.path
		return r.get(k)

	def body(s):
		return s.h.request.body

	def json(s):
		return json.loads(s.h.request.body)

	def file(s):
		return [i.key() for i in s.h.get_uploads()]


class dataoutput():
	def __getattr__(s,k):
		pass

class workhandler(blobstore_handlers.BlobstoreUploadHandler,RequestHandler):
	@classmethod
	def getapp(cls):
		return webapp2.WSGIApplication([('/.*',cls)])

	def mset(s,v):
		memcache.set("memcache",v)

	def mget(s):
		return memcache.get("memcache")

	def cget(s,k):
		return s.request.cookies.get(k,'')

	def cset(s,k,v,d=100):
		s.response.headers.add_header('Set-Cookie','{0}={1}; path=/; max-age={2}'.format(k,v,86400*d if v else -100))

	def kget(s,m=True):
		try:
			x=ndb.Key(urlsafe=s.cget('urlsafe'))
			if m: x=x.get()
			return x
		except:
			return None

	def kset(s,k):
		s.cset('urlsafe',k.urlsafe() if k else '')

	def work(s,a,o):
		pass  # doing

	def post(s):
		s.get()

	def get(s):
		#　メモリリーク対策
		context=ndb.get_context()
		context.clear_cache()
		context.set_cache_policy(lambda key:False)
		context.set_memcache_policy(lambda key:False)
		# 入力
		s.i=datainput(s)
		if any(not i.size for i in s.get_uploads()):
			blobstore.delete(i.key() for i in s.get_uploads())
		# 処理
		s.work(s.i)

	def write_json(self,data):
		def jsondefault(o):
			if isinstance(o,ndb.Model):
				r=o.to_dict()
				r["key"]=o.key
				return r
			if isinstance(o,ndb.Key):
				return {"id":o.id(),"kind":o.kind(),"urlsafe":o.urlsafe()}
			if isinstance(o,blobstore.BlobKey):
				return str(o)
			return None

		self.response.out.write(json.dumps(data,default=jsondefault,indent=4))

	def write_temp(self,temp,data):
		tmp=os.path.join(os.path.dirname(__file__),temp)
		if os.path.exists(tmp):
			if hasattr(data,"__dict__"):
				data=vars(data)
			data["path"]=self.request.path
			data["hosturl"]=self.request.host_url
			self.response.out.write(template.render(tmp,data))

	def write(self,text):
		self.response.out.write(text)

	def sendmail(data):
		data["sender"]=u"anything@{0}.appspotmail.com".format(app_identity.get_application_id())
		mail.send_mail(sender=data["sender"],to=data["to"],subject=data["subject"],body=data["body"])

	def getuploadurl(next,maxbytes=None):
		return blobstore.create_upload_url(next,max_bytes_per_blob=maxbytes)

	def geturl(s,path):
		return "http://{0}{1}".format(app_identity.get_default_version_hostname(),path)
