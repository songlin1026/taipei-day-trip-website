from flask import *

import json
import mysql.connector
import getpass

#mysql.connector
password=getpass.getpass(prompt='請輸入資料庫密碼: ', stream=None)
connection=mysql.connector.connect(
    host="localhost",
    user="root",
    password= password,
    database='taipeitrip',
    charset='utf8')
cursor=connection.cursor()


app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

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

@app.route("/api/attractions")
def attractions():
	try:
		page=request.args.get("page",0)
		keyword=request.args.get("keyword",None)
		result=[]
		firstdataId=1+(12*int(page))
		finaldataId=12+(12*int(page))
		# 是否有關鍵字
		if keyword==None:
			cursor.execute("select * from taipeitrip.data where id between %s and %s",[firstdataId,finaldataId])  #執行SQL
			database=cursor.fetchall()
			dataDict={}
			data=[]
			n=0
			# 抓取12筆資料
			while n<12:
				dataDict={
					"id":database[n][0],
					"name":database[n][1],
					"category":database[n][2],
					"description":database[n][3],
					"address":database[n][4],
					"transport":database[n][5],
					"mrt":database[n][6],
					"latitude":database[n][7],
					"longitude":database[n][8],
					"images":database[n][9]
				} 
				data.append(dataDict)
				n+=1
			return {"nextpage":page,"data":data}
		else:
			# 抓取關鍵字資料
			cursor.execute("select * from taipeitrip.data where name=%s",[keyword])
			database=cursor.fetchall()
			databaseNumber=len(database)
			dataDict={}
			data=[]
			n=0
			while n<databaseNumber:
				dataDict={
						"id":database[n][0],
						"name":database[n][1],
						"category":database[n][2],
						"description":database[n][3],
						"address":database[n][4],
						"transport":database[n][5],
						"mrt":database[n][6],
						"latitude":database[n][7],
						"longitude":database[n][8],
						"images":database[n][9]
					} 
				data.append(dataDict)
				n+=1
			return {"nextpage":page,"data":data}
	except:
		return{"error": True,"message": "連線失敗"}



@app.route("/api/attraction/<attractionId>")
def attractionId(attractionId):
	try:
		# 抓取id資料
		cursor.execute("select * from taipeitrip.data where id=%s",[attractionId])
		database=cursor.fetchall()
		databaseNumber=len(database)
		dataDict={}
		if database!=None:
			print("234")
			dataDict={
					"id":database[0][0],
					"name":database[0][1],
					"category":database[0][2],
					"description":database[0][3],
					"address":database[0][4],
					"transport":database[0][5],
					"mrt":database[0][6],
					"latitude":database[0][7],
					"longitude":database[0][8],
					"images":database[0][9]
				} 
			return {"data":dataDict}	
		else:
			return{"error": True,"message": "景點編號不正確"}
	except:
		return {"error": True,"message": "伺服器發生錯誤"}



app.run(host="0.0.0.0",port=3000)