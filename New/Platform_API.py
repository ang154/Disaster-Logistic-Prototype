import json
import requests


def lookup_disaster_fema():
    # Input: Available disaster details
    # Output: Disaster IDs
    return 0


# Input: Disaster ID
# Output: Disaster info FEMA side
def newest_disasters_fema(current_date: str):
    url = 'https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$filter=incidentBeginDate%20ge%20%27{}%27&$orderby=incidentBeginDate&$format=json'.format(
        current_date)
    response = requests.get(url)
    data = response.json()
    print("API level result for newest_disasters_fema:\n")
    print(data)
    print("End\n")
    return data


# Input: Disaster ID
# Output: Disaster info FEMA side
def disaster_status_fema(d_id):
    url = 'https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$filter=id%20eq%20%27{}%27'.format(
        d_id)
    response = requests.get(url)
    data = response.json()
    print("API level result for disaster_status_fema:\n")
    print(data)
    print("End\n")
    return data


def lookup_weather_forcast(zipcode: int):
    if zipcode is None:
        print("lookup_weather_forcast failed due to no input")
        return -1
    url = 'http://api.openweathermap.org/data/2.5/weather?zip={},us&appid=ae6dc58345f5a7046e91af6581e40304'.format(zipcode)
    response = requests.get(url)
    data = response.json()
    print("API level result for lookup_weather_forcast:\n")
    print(data)
    print("End\n")
    return data


# Input: zip
# Output: lon and alt
def zip_to_cords(zipcode: int):
    api_key = "ae6dc58345f5a7046e91af6581e40304"
    zip_code = zipcode
    country_code = 'US'
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},{country_code}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    print("Requested with:"+ str(zipcode) +"Ended up with:"+ str(data))
    latitude = data["coord"]["lat"]
    longitude = data["coord"]["lon"]
    return longitude, latitude


# Input: zip
# Output: lon and alt
def zip_to_cityid(zipcode=10036):
    api_key = "ae6dc58345f5a7046e91af6581e40304"
    zip_code = zipcode
    country_code = 'US'
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},{country_code}&appid={api_key}"
        response = requests.get(url)
        data = response.json()
        print("Requested with:"+ str(zipcode) +"Ended up with:"+str(data))
        latitude = data["coord"]["lat"]
        longitude = data["coord"]["lon"]
        # Get nearest city from geocode
        url = f"http://api.openweathermap.org/data/2.5/find?lat={latitude}&lon={longitude}&cnt=1&appid={api_key}"
        response = requests.get(url)
        data = response.json()
        city_id = data["list"][0]["id"]
        return city_id
    except KeyError:
        return 3163858


def shipment_tracking_update():
    # Input: Shipment ID and location
    # Output: Confirmation
    return 0

