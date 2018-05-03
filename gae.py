import moto,random,time

class work(moto.workhandler):
	def work(s,i):
		data={}
		if i.path=="/":
			data["univ"]=moto.base.query(moto.base.cate=="univ").order(+moto.base.int0).fetch()
			data["vote"]=s.cget("vote")
			s.write_temp("home.html",data)
		if i.path=="/rank":
			data["univ"]=moto.base.query(moto.base.cate=="univ").order(+moto.base.int0).fetch()
			if s.cget("vote"):
				data["main"]=moto.base.getbyid(s.cget("vote"))
			random.shuffle(data["univ"])
			s.write_temp("rank.html",data)
		if i.path=="/admn":
			if s.i.iden:
				data["main"]=moto.base.getbyid(s.i.iden)
			data["univ"]=moto.base.query(moto.base.cate=="univ").fetch()
			s.write_temp("admn.html",data)
		if i.path=="/set":
			if s.i.iden:
				main=moto.base.getbyid(s.i.iden)
			else:
				main=moto.base()
			main.populate(cate="univ",name=i.name,int0=int(i.int0),json={"embed":i.embed,"univ":i.univ})
			if i.order=="del":
				main.key.delete()
			if i.order=="set":
				main.put()
			time.sleep(1)
			s.redirect("/admn")
		if i.path=="/vote":
			main=moto.base.getbyid(s.i.iden)
			main.int0+=1
			main.put()
			s.cset("vote",main.key.id())
			time.sleep(1)
			s.redirect("/rank")
		if i.path=="/reset":
			s.cset("vote",None)
			time.sleep(1)
			s.redirect("/rank")


app=work.getapp()
