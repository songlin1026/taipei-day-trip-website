from flask import *
from dotenv import load_dotenv, find_dotenv
import os
import urllib.request 
import urllib.parse
import json
import mysql.connector
# from flask_mysqlpool import MySQLPool
from mysql.connector import pooling


#mysql.connector
#load .env
load_dotenv(find_dotenv())
def DBconnect():
	connection=pooling.MySQLConnectionPool(
		pool_name="taipeitrip_pool",
		pool_size=5,
		pool_reset_session=True,
		host=os.getenv('MYSQL_DB_HOST'),
		database=os.getenv('MYSQL_DB_NAME'),
		user=os.getenv('MYSQL_USER'),
		password=os.getenv('MYSQL_PASSWORD')
		)
	return connection




app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.secret_key = os.getenv('Session_secret_key')

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
@app.route("/api/order/<orderNumber>",methods=["GET"])
def orderapi(orderNumber):
	if session.get("member")!="":
		ordergetData=session.get("order")
		# 串接TapPay api
		orderGet={"partner_key":os.getenv('TapPay_partner_key'),"records_per_page":1,"filters":{"rec_trade_id":orderNumber}}
		url="https://sandbox.tappaysdk.com/tpc/transaction/query"
		headers={"content-type": "application/json","x-api-key":os.getenv('TapPay_partner_key')}
		orderGet=json.dumps(orderGet).encode('utf-8')
		tappaygetResponse=urllib.request.Request(url,orderGet,headers)
		# 解碼TapPay Data
		tappaygetData=urllib.request.urlopen(tappaygetResponse).read().decode('utf-8')
		tappaygetData=json.loads(tappaygetData)

		# 查無交易紀錄
		if tappaygetData["status"]!=2:
			return {"error":True,"message":"查無交易紀錄"}
		# 授權交易未請款
		elif tappaygetData["trade_records"][0]["record_status"]==0:
			return ordergetData
		# 交易完成
		elif tappaygetData["trade_records"][0]["record_status"]==1:
			return ordergetData
		# 待付款
		elif tappaygetData["trade_records"][0]["record_status"]==4:
			return ordergetData
		else:
			return {"error":True,"message":"查無交易紀錄"}
	else:
		return{"error":True,"message":"使用者未登入"}





@app.route("/api/orders",methods=["POST"])
def ordersapi():
		if session.get("member")!="":
			# 串接TapPay api
			orderData=json.loads(request.data.decode('utf-8'))
			url="https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
			payment=False
			# 檢查資料是否缺漏
			if orderData["order"]["contact"]["phone"]=="" or orderData["order"]["contact"]["name"]=="" or orderData["order"]["contact"]["email"]=="" or orderData["order"]["price"]=="" or orderData["prime"]=="":
				return {"error":True,"message":"資料有缺漏"}
			else:
				# 整理request
				data={
					"prime":orderData["prime"],
					"partner_key":os.getenv('TapPay_partner_key'),
					"merchant_id":os.getenv('TapPay_merchant_id'),
					"amount":orderData["order"]["price"],
					"details":"taipeidayTrip",
					"cardholder":{
						"phone_number":orderData["order"]["contact"]["phone"],
						"name":orderData["order"]["contact"]["name"],
						"email":orderData["order"]["contact"]["email"],
					}
				}
				data=json.dumps(data).encode('utf-8')
				headers={"content-type": "application/json","x-api-key":os.getenv('TapPay_partner_key')}
				# 開始串接TapPay 
				tappayResponse=urllib.request.Request(url,data,headers)
				# 解碼TapPay Data
				tappayData=urllib.request.urlopen(tappayResponse).read().decode('utf-8')
				tappayData=json.loads(tappayData)
				# 整理seesion
				ordergetsession={
					"data":{
						"number":tappayData["rec_trade_id"],
						"price":orderData["order"]["price"],
						"trip":{
							"attraction":{
								"id":orderData["order"]["trip"]["attraction"]["id"],
								"name":orderData["order"]["trip"]["attraction"]["name"],
								"address":orderData["order"]["trip"]["attraction"]["address"],
								"image":orderData["order"]["trip"]["attraction"]["image"]
							},
							"date":orderData["order"]["trip"]["date"],
							"time":orderData["order"]["trip"]["time"]
						},
						"contact":{
							"name":orderData["order"]["contact"]["name"],
							"email":orderData["order"]["contact"]["email"],
							"phone":orderData["order"]["contact"]["phone"]
						},
						"status":tappayData["status"]
					}
				}

				if tappayData["status"]!=0:
					return {"error":True,"message":"訂單建立失敗"}
				else:
					session["order"]=ordergetsession
					session["booking"]=""
					payment=True
					return {"data":{"number":tappayData["rec_trade_id"],"payment":{"status":tappayData["status"],"message":"付款成功"}}}
		else:
			return {"error":True,"message":"會員未登入"}



@app.route("/api/booking",methods=["GET","POST","DELETE"])
def bookingAPI():	
	try:
		if request.method=="POST":
			# 檢查是否登入
			if session.get("member")!="":
				attractionpostData=json.loads(request.data.decode('utf-8'))
				# 檢查訂購資料是否有誤
				if attractionpostData["attractionId"] =="" or attractionpostData["date"] =="" or attractionpostData["time"] =="" or attractionpostData["price"] =="" :
					return {"error":True,"message":"訂購資料有缺誤"}
				else:
					# 抓取景點資料
					attractionId=attractionpostData["attractionId"]
					connection=DBconnect().get_connection()
					cursor=connection.cursor()
					cursor.execute("select * from taipeitrip.data where id=%s",[attractionId])
					bookingAtt=cursor.fetchone()
					connection.close()
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
				connection=DBconnect().get_connection()
				cursor=connection.cursor()
				cursor.execute("select * from taipeitrip.member where name=%s",[memberName])
				memberData=cursor.fetchone()
				connection.close()
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
			connection=DBconnect().get_connection()
			cursor=connection.cursor()
			cursor.execute("select * from taipeitrip.member where email=%s",[signinEmail])
			signinData=cursor.fetchone()
			connection.close()
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
				connection=DBconnect().get_connection()
				cursor=connection.cursor()
				cursor.execute("select * from taipeitrip.member where email=%s",[signupEmail])
				signup_member=cursor.fetchone()
				connection.close()
				if signup_member==None:
					connection=DBconnect().get_connection()
					cursor=connection.cursor()
					cursor.execute("insert into taipeitrip.member (name,email,password) values (%s,%s,%s) ",[signupName,signupEmail,signupPassword])
					connection.commit()
					connection.close()
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
			connection=DBconnect().get_connection()
			cursor=connection.cursor()
			if firstdata==0:
				cursor.execute("select * from taipeitrip.data ORDER BY `latitude` limit  %s ",[finaldata])
			else:
				cursor.execute("select * from taipeitrip.data order by `latitude` limit %s , %s ",[firstdata,finaldata])  #執行SQL
			database=cursor.fetchall()
			connection.close()
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
			connection=DBconnect().get_connection()
			cursor=connection.cursor()
			cursor.execute("select * from taipeitrip.data  where name like %s order by latitude",[keyword])
			database=cursor.fetchall()
			connection.close()
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
		connection=DBconnect().get_connection()
		cursor=connection.cursor()
		cursor.execute("select * from taipeitrip.data where id=%s",[attractionId])
		database=cursor.fetchall()
		connection.close()
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


app.run(port=80)
# app.run(host="0.0.0.0",port=80)