import datetime
import requests
import socket
import time
import re

connection_data = ("irc.chat.twitch.tv", 6667)
token = "TWITCH_TOKEN"
user = "USERN_NAME"
channel = "#CHANNEL"


def call_cats_api():
    url = "https://cat-fact.herokuapp.com/facts/random"
    response = requests.get(url)
    jsonDict = response.json()
    catText = jsonDict["text"]
    return "/me InuyoFace " + catText + " InuyoFace"


def call_weather_api(cityName):
    language = "en"
    unitsFormat = "metric"
    apiKey = "API_KEY"

    completeUrl = "http://api.openweathermap.org/data/2.5/weather?q={}&units={}&appid={}&lang={}".format(cityName, unitsFormat, apiKey, language)

    response = requests.get(completeUrl)
    jsonDict = response.json()

    if jsonDict["cod"] == 200:
        weatherDesc = jsonDict["weather"][0]["description"]
        weatherTemp = jsonDict["main"]["temp"]
        weatherPres = jsonDict["main"]["pressure"]
        weatherHum = jsonDict["main"]["humidity"]
        weatherCountry = jsonDict["sys"]["country"]
        weatherSunr = jsonDict["sys"]["sunrise"]
        weatherSuns = jsonDict["sys"]["sunset"]
        weatherCity = jsonDict["name"]

        sunrTime = datetime.datetime.fromtimestamp(weatherSunr).strftime('%H:%M:%S')
        sunsTime = datetime.datetime.fromtimestamp(weatherSuns).strftime('%H:%M:%S')

        weatherMsg = "/me {} [{}]: {} || Temperature: {}°C || Pressure: {}hPa || Humidity: {}% || Sunrise: {} (GMT+2) || Sunset: {} (GMT+2) ||".format(weatherCity, weatherCountry, weatherDesc, weatherTemp, weatherPres, weatherHum, sunrTime, sunsTime)
        return weatherMsg


def send_msg(message):
    server.send(bytes("PRIVMSG {} :{}\r\n".format(channel, message), "utf-8"))


server = socket.socket()
server.connect(connection_data)
server.send(bytes("PASS " + token + "\r\n", "utf-8"))
server.send(bytes("NICK " + user + "\r\n", "utf-8"))
server.send(bytes("JOIN " + channel + "\r\n", "utf-8"))

msgReg = re.compile(r"^:(\w+)!\w+@\w+.tmi.twitch.tv PRIVMSG #\w+ :(.*)")
weatherReg = re.compile(r"(^!weather )(.*)")
catReg = re.compile(r"^!randomfact")

while True:
    readBuffer = server.recv(2048).decode("utf-8")
    if readBuffer == "PING :tmi.twitch.tv\r\n":
        server.send(bytes("PONG :tmi.twitch.tv\r\n", "utf-8"))
    else:
        msgMatch = re.search(msgReg, readBuffer)
        if msgMatch is not None:
            username = msgMatch.group(1)
            message = msgMatch.group(2)
            wtrMatch = re.search(weatherReg, message)
            catMatch = re.search(catReg, message)
            if wtrMatch is not None:
                cityName = wtrMatch.group(2)
                weatherApiRespond = call_weather_api(cityName)
                if weatherApiRespond is not None:
                    send_msg(weatherApiRespond)
                    time.sleep(2.5)
            if catMatch is not None:
                catsApiRespond = call_cats_api()
                send_msg(catsApiRespond)
                time.sleep(2.5)
            print(username + ": " + message)
    # print(readBuffer)
    time.sleep(0.2)
