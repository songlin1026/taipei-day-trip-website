from flask import *

import json
import mysql.connector
import getpass

#mysql.connector
password=getpass.getpass(prompt='請輸入資料庫密碼: ', stream=None)
def DBconnect():
	connection=mysql.connector.connect(
		host="localhost",
		user="root",
		password= password,
		database='taipeitrip',
		charset='utf8',
		)
	return connection


app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

######
@app.route("/api/booking",methods=["GET","POST","DELETE"])
def bookingAPI():	
	try:
		if request.method=="POST":
			# 檢查是否登入
			if session.get("member")!="":
				attractionpostData=json.loads(request.data.decode('utf-8'))
				# 檢查訂購資料是否有誤
				if attractionpostData["attractionId"] =="" or attractionpostData["date"] ==""  :
					return {"error":True,"message":"訂購資料有缺誤"}
				elif attractionpostData["time"] =="" or attractionpostData["price"] =="" :
					return {"error":True,"message":"訂購資料有缺誤"}
				else:
					# 抓取景點資料
					attractionId=attractionpostData["attractionId"]
					connection=DBconnect()
					cursor=connection.cursor()
					cursor.execute("select * from taipeitrip.data where id=%s",[attractionId])
					bookingAtt=cursor.fetchone()
					attractionId=int(bookingAtt[0])
					attractionName=bookingAtt[1]
					attractionAddress=bookingAtt[4]
					attractionImage=eval(bookingAtt[9])[0]
					bookingDate=attractionpostData["date"]
					bookingTime=attractionpostData["time"]
					bookingPrice=int(attractionpostData["price"])
					# 設定session
					bookingdic={"attraction":{"id":attractionId,"name":attractionName,"address":attractionAddress,"image":attractionImage},"date":bookingDate,"time":bookingTime,"price":bookingPrice}
					session["booking"]=bookingdic
					return {"ok":True}
			else:
				return {"error":True,"message":"使用者未登入"}
		elif request.method=="GET":
			if session.get("member")=="":
				return {"error":True,"message":"使用者未登入"}
			else:
				if session.get("booking")=="":
					return {"data":None}
				else:
					data=session.get("booking")
					return {"data":data}
		elif request.method=="DELETE":
			session["booking"]=""
			return {"ok":True}
		else:
			return{"error":True}
	except:
		return {"error":True,"message":"伺服器有誤"}




@app.route("/api/user",methods=["GET","POST","PATCH","DELETE"])
def user():
	try:
		# 檢查是否登入
		if request.method=="GET":
			if session.get("member")!="":
				memberName=session.get("member")
				# 連接mysql
				connection=DBconnect()
				cursor=connection.cursor()
				cursor.execute("select * from taipeitrip.member where name=%s",[memberName])
				memberData=cursor.fetchone()
				if memberData!=None:
					return {"data":{"id":memberData[0],"name":memberData[1],"email":memberData[2]}}
				else:
					session["member"]=""
					return{"data":None}					
			else:
				session["member"]=""
				return{"data":None}	
		# 登入
		elif request.method=="PATCH":
			signin_Data=json.loads(request.data.decode('utf-8'))
			signinEmail=signin_Data["email"]
			# 連接mysql
			connection=DBconnect()
			cursor=connection.cursor()
			cursor.execute("select * from taipeitrip.member where email=%s",[signinEmail])
			signinData=cursor.fetchone()
			# 判斷是否有使用者資料
			if signinData!=None:
				# 檢查密碼是否與帳號相符
				if signinData[3]==signin_Data["password"]:
					session["member"]=signinData[1]
					return {"ok":True}
				else:
					return {"error":True,"message":"信箱或密碼錯誤"}
			else:
				return {"error":True,"message":"信箱或密碼錯誤"}	
		# 登出
		elif request.method=="DELETE":
			session["member"]=""
			session["booking"]=""
			return {"ok":True}
		# 註冊
		elif request.method=="POST":
			signupData=json.loads(request.data.decode('utf-8'))
			signupEmail=signupData["email"]
			signupName=signupData["name"]
			signupPassword=signupData["password"]
			if signupEmail!=None or signupName!=None or signupPassword!=None:
				connection=DBconnect()
				cursor=connection.cursor()
				cursor.execute("select * from taipeitrip.member where email=%s",[signupEmail])
				signup_member=cursor.fetchone()
				if signup_member==None:
					connection=DBconnect()
					cursor=connection.cursor()
					cursor.execute("insert into taipeitrip.member (name,email,password) values (%s,%s,%s) ",[signupName,signupEmail,signupPassword])
					connection.commit()
					return {"ok":True}
				else:
					return{"error":True,"message":"重複的email"}
			else:
				return{"error":True,"message":"資料有缺無法註冊"}
		else:
			return{"error":True,"message":"伺服器發生錯誤"}
	except:	
		return {"error": True,"message": "伺服器發生錯誤"}

	


@app.route("/api/attractions")
def attractions():
	try:
		page=request.args.get("page",0)
		keyword=request.args.get("keyword",None)
		result=[]
		firstdata=0+(12*int(page))
		# finaldata=12+(12*int(page))
		finaldata=12
		# 是否有關鍵字
		if keyword==None:
			# 根據緯度排序後抓取資料
			connection=DBconnect()
			cursor=connection.cursor()
			if firstdata==0:
				cursor.execute("select * from taipeitrip.data ORDER BY `latitude` limit  %s ",[finaldata])
			else:
				cursor.execute("select * from taipeitrip.data order by `latitude` limit %s , %s ",[firstdata,finaldata])  #執行SQL
			database=cursor.fetchall()
			dataDict={}
			data=[]
			n=0
			# 判斷資料是否有12筆資料 (是否為page最後一頁)
			if len(database)<12 :
				while n<len(database):
					dataDict={
						"id":int(database[n][0]),
						"name":database[n][1],
						"category":database[n][2],
						"description":database[n][3],
						"address":database[n][4],
						"transport":database[n][5],
						"mrt":database[n][6],
						"latitude":float(database[n][7]),
						"longitude":float(database[n][8]),
						"images":eval(database[n][9])
					} 
					data.append(dataDict)
					n+=1
				nextpage=None
				return {"nextPage":nextpage,"data":data}
			else:
				while n<12:
					dataDict={
						"id":int(database[n][0]),
						"name":database[n][1],
						"category":database[n][2],
						"description":database[n][3],
						"address":database[n][4],
						"transport":database[n][5],
						"mrt":database[n][6],
						"latitude":float(database[n][7]),
						"longitude":float(database[n][8]),
						"images":eval(database[n][9])
					} 
					data.append(dataDict)
					n+=1
				nextpage=int(page)+1
				return {"nextPage":nextpage,"data":data}
		else:
			# 抓取關鍵字資料
			keyword="%"+keyword+"%"
			connection=DBconnect()
			cursor=connection.cursor()
			cursor.execute("select * from taipeitrip.data  where name like %s order by latitude",[keyword])
			database=cursor.fetchall()
			databaseNumber=len(database)
			dataDict={}
			data=[]
			n=0
			# 資料數是否大於12筆
			if databaseNumber>12:
				start=0+(12*int(page)-1)
				final=11+12*int(page)
				lastpageData=databaseNumber % 12
				totalpage=databaseNumber // 12
				# 判斷是否在資料最後一頁
				if int(page)==totalpage:
					n=start
					while n<=(start+lastpageData):
						dataDict={
							"id":int(database[n][0]),
							"name":database[n][1],
							"category":database[n][2],
							"description":database[n][3],
							"address":database[n][4],
							"transport":database[n][5],
							"mrt":database[n][6],
							"latitude":float(database[n][7]),
							"longitude":float(database[n][8]),
							"images":eval(database[n][9])
						} 
						data.append(dataDict)
						n+=1
					nextpage=None
					return {"nextPage":nextpage,"data":data}
				else:
					# 抓取12筆資料
					while start<final:
							dataDict={
									"id":int(database[start][0]),
									"name":database[start][1],
									"category":database[start][2],
									"description":database[start][3],
									"address":database[start][4],
									"transport":database[start][5],
									"mrt":database[start][6],
									"latitude":float(database[start][7]),
									"longitude":float(database[start][8]),
									"images":eval(database[start][9])
								} 
							data.append(dataDict)
							start+=1
					nextpage=int(page)+1
					return {"nextPage":nextpage,"data":data}
			else:
				# 抓取未滿或剛好12筆的資料
				while n<databaseNumber:
					dataDict={
							"id":int(database[n][0]),
							"name":database[n][1],
							"category":database[n][2],
							"description":database[n][3],
							"address":database[n][4],
							"transport":database[n][5],
							"mrt":database[n][6],
							"latitude":float(database[n][7]),
							"longitude":float(database[n][8]),
							"images":eval(database[n][9])
						} 
					data.append(dataDict)
					n+=1
				nextpage=None
				return {"nextPage":nextpage,"data":data}
	except:
		return{"error": True,"message": "連線失敗"}



@app.route("/api/attraction/<attractionId>")
def attractionId(attractionId):
	try:
		# 抓取id資料
		connection=DBconnect()
		cursor=connection.cursor()
		cursor.execute("select * from taipeitrip.data where id=%s",[attractionId])
		database=cursor.fetchall()
		databaseNumber=len(database)
		dataDict={}
		# 編號id是否存在
		if database!=None:
			dataDict={
					"id":int(database[0][0]),
					"name":database[0][1],
					"category":database[0][2],
					"description":database[0][3],
					"address":database[0][4],
					"transport":database[0][5],
					"mrt":database[0][6],
					"latitude":float(database[0][7]),
					"longitude":float(database[0][8]),
					"images":eval(database[0][9])
				} 
			return {"data":dataDict}	
		else:
			return{"error": True,"message": "景點編號不正確"}
	except:
		return {"error": True,"message": "伺服器發生錯誤"}


# app.run(port=3000)
app.run(host="0.0.0.0",port=3000)