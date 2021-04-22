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
		firstdata=0+(12*int(page))
		finaldata=12+(12*int(page))
		# 是否有關鍵字
		if keyword==None:
			# 根據緯度排序後抓取資料
			if firstdata==0:
				cursor.execute("select * from taipeitrip.data ORDER BY `latitude` limit  %s ",[finaldata])
			else:
				cursor.execute("select * from taipeitrip.data order by `latitude` limit %s , %s ",[firstdata,finaldata])  #執行SQL
			database=cursor.fetchall()
			dataDict={}
			data=[]
			n=0
			# 抓取12筆資料
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