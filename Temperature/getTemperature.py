# importing requests and json
import requests, time
# base URL
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
CITY = "Lima"
API_KEY = "29244f2262bb6898c19715b2ae7ca9dc"
# upadting the URL
URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY
# HTTP request
while True:
    response = requests.get(URL)
    # checking the status code of the request
    if response.status_code == 200:
    # getting data in the json format
        data = response.json()
        # getting the main dict block
        main = data['main']
        # getting temperature
        temperature = str(int(main['temp']-273.2))
        #    # getting the humidity
        #    humidity = main['humidity']
        #    # getting the pressure
        #    pressure = main['pressure']
        #    # weather report
        #    report = data['weather']
        #    print(f"{CITY:-^30}")
        print("Temperature: "+temperature)
        #    print(f"Humidity: {humidity}")
        #    print(f"Pressure: {pressure}")
        #    print(f"Weather Report: {report[0]['description']}")
    else:
        # showing the error message
        print("Error in the HTTP request")
    time.sleep(1)