from flask import Flask
from flask import render_template,request
import json
import mysql.connector
from discord_webhook import DiscordWebhook, DiscordEmbed
app = Flask(__name__)

# Web dashboard
@app.route("/")
def hello_world():
    #if request.method == "POST":
        #username = request.form['student_id']
        #print("Hello")
    return render_template("index.html") # open file index.html 

# REST API

# API for control esp8266
# url/data_request
@app.route('/data_request', methods=['GET'])
def data_request():
    if request.method == "GET":
        mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          password="12345678",
          database="FIC"
        )
        mycursor = mydb.cursor()
        sql = "SELECT status.id,status.pump,status.fan,parameter.pump_max_temp,parameter.pump_min_temp,parameter.pump_max_humi,parameter.fan_min_temp,parameter.fan_min_humi,status.manual_state FROM status INNER JOIN parameter ON status.id = parameter.id"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        if myresult[0][8] == 1:

            pump = myresult[0][1]
            pump_state = ""
            if pump == 0:pump_state = "Close"
            else: pump_state ="Open"

            fan = myresult[0][2]
            fan_state = ""
            if fan == 0:fan_state = "Close"
            else: fan_state = "Open"

            webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1186979233696854046/kGgrw3__1UhXbGDFZvJkFKraWi2Ca9HiF-S7YuWNuGUAH9YDZY5XbG_PdgVTiVJU9Gxw")
            embed = DiscordEmbed(title="Manual activated", description=f"pump : {pump_state} ,fan : {fan_state}", color="03b2f8")
            webhook.add_embed(embed)
            webhook.execute()
        return myresult,200
    else:
        return {"status" : "404 err"},404




# API for esp8266 send data to server
# url/data_upload
@app.route('/data_upload', methods=['POST'])
def data_upload():
    if request.method == "POST":
        data = json.loads(request.data)
        #check Nan
        temperature_1 = ""
        humidity_1 = ""
        soil_humidity_1 = ""

        temperature = data["temperature"]
        humidity = data["humidity"]
        soil_humidity = data["soil_humidity"]
        if temperature == "nan":
            temperature_1 = 0
        else:
            temperature_1 = temperature
        if humidity == "nan":
            humidity_1 = 0
        else:
            humidity_1 = humidity
        if soil_humidity == "nan":
            soil_humidity_1 = 0
        else:
            soil_humidity_1 = soil_humidity

        Token = data["token"]
        #data base connect
        mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          password="12345678",
          database="FIC"
        )
        mycursor = mydb.cursor()
        #sql
        sql = "INSERT INTO Sensor_data (Temperature,Humidity,Soil_humidity) VALUES (%s, %s, %s)"
        val = (f"{temperature_1}",f"{humidity_1}",f"{soil_humidity_1}")
        mycursor.execute(sql, val)
        #fetch
        mydb.commit()
        #debug sql
        print(mycursor.rowcount, "record inserted.")
        mycursor = mydb.cursor()
        sql = "UPDATE device SET status = 1 WHERE device_token = (%s)"
        mycursor.execute(sql,(Token,))
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")
        #debug
        # print("------------------------------------------")
        # print(f"temperature = {temperature}")
        # print(f"humidity = {humidity}")
        # print(f"soil_humidity = {soil_humidity}")
        # print("------------------------------------------")
        #debug
        return {"status" : "200 ok"},200
    else:
        return {"status" : "404 err"},404
# if __name__ == '__main__':
#     # run app in debug mode on port 5000
#     app.run(debug=True, port=5000, host='0.0.0.0')
