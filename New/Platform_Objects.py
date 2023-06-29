from . import Platform_Alert
from . import SQL_Caller
from . import Platform_API
from django.db import DatabaseError
from datetime import datetime
from . import db
from . import cursor
from asgiref.sync import sync_to_async


class Content:
    def __init__(self, c_id=None, life=None, unit=None, name=None):
        self.id = c_id
        self.life = life
        self.unit = unit
        self.name = name

    def load_from_database(self, c_id=None):
        if c_id is None:
            c_id = self.id
        res = SQL_Caller.get_obj('Content', c_id)
        if res == -1:
            return -1
        self.name = res[0][1]
        self.unit = res[0][2]
        self.life = res[0][3]
        self.id = c_id
        return self

    async def insert_to_database(self):
        try:
            sql = "INSERT INTO Content (content_name, unit, life_in_month) VALUES (%s, %s, %s);"
            val = (self.name, self.unit, self.life)
            cursor.execute(sql, val)
            sync_to_async(db.commit)
        except DatabaseError as err:
            print("Something went wrong: {}".format(err))
            return -1
        # print("Node", node_id, "Record inserted.")
        self.id = cursor.lastrowid
        return self.id

    async def update_to_database(self):
        try:
            sql = "UPDATE Content SET content_name = %s, unit = %s, life_in_month = %s WHERE id = %s;"
            val = (self.name, self.unit, self.life, self.id)
            cursor.execute(sql, val)
            sync_to_async(db.commit)
        except DatabaseError as err:
            print("Something went wrong: {}".format(err))
            return -1
        # print("Node", node_id, "Record inserted.")
        return self.id

    # Get corresponding vendors name and id based on the content id
    def get_cor_vendors(self):
        try:
            sql = "select V.company_name, V.id from Vendors V, Content C, content_vendor r where r.content_id= C.id and r.vendor_id=V.id and C.id=%s;"
            val = self.id
            cursor.execute(sql, val)
            result = cursor.fetchone()
            print("API level result for get_cor_vendors:\n")
            print(result)
            print("End\n")
        except DatabaseError as err:
            print("Something went wrong: {}".format(err))
            return -1
        return result

    def __str__(self):
        return "Content name: {} <br> Unit: {} <br> Shelf life (in months): {} <br>".format(self.name, self.unit,
                                                                                            self.life)


class Disaster:
    def __init__(self, lastRefresh=None, area=None, county_code=None, begin_date=None, state_code=None, title=None,
                 incident_type=None, declare_type=None, state=None, d_id=None):
        self.lastRefresh = lastRefresh
        self.area = area
        self.county_code = county_code
        self.begin_date = begin_date
        self.state_code = state_code
        self.title = title
        self.incident_type = incident_type
        self.declare_type = declare_type
        self.state = state
        self.id = d_id

    def load_from_database(self, d_id=None):
        if d_id is None:
            d_id = self.id
        res = SQL_Caller.get_obj('disasters', d_id)
        if res == -1:
            return -1
        self.id = d_id
        self.state = res[0][1]
        self.declare_type = res[0][2]
        self.incident_type = res[0][3]
        self.title = res[0][4]
        self.begin_date = res[0][5]
        self.state_code = res[0][6]
        self.county_code = res[0][7]
        self.area = res[0][8]
        self.lastRefresh = res[0][9]
        return self

    def sync_with_fema(self, d_id=None):
        if d_id is None:
            d_id = self.id
        data = Platform_API.disaster_status_fema(d_id)
        self.id = d_id
        self.state = data["DisasterDeclarationsSummaries"][0]["state"]
        self.declare_type = data["DisasterDeclarationsSummaries"][0]["declarationType"]
        self.incident_type = data["DisasterDeclarationsSummaries"][0]["incidentType"]
        self.title = data["DisasterDeclarationsSummaries"][0]["declarationTitle"]
        self.begin_date = data["DisasterDeclarationsSummaries"][0]["incidentBeginDate"]
        self.state_code = data["DisasterDeclarationsSummaries"][0]["fipsStateCode"]
        self.county_code = data["DisasterDeclarationsSummaries"][0]["fipsCountyCode"]
        self.area = data["DisasterDeclarationsSummaries"][0]["designatedArea"]
        self.lastRefresh = data["DisasterDeclarationsSummaries"][0]["lastRefresh"]

    def get_zip(self):
        if self.county_code and self.state_code:
            return SQL_Caller.fips_to_zip(self.state_code, self.county_code)
        else:
            return -1

    def __str__(self):
        return "Disaster ID: {} <br> Disaster state: {} <br> Disaster declare type: {} <br> Disaster incident type: {} <br> Disaster title: {} <br> Begin date: {} <br> State FIPS code: {} <br> County FIPS code: {} <br> Area name: {} <br>".format(
            self.id, self.state, self.declare_type, self.incident_type, self.title, self.begin_date, self.state_code,
            self.county_code, self.area)


class Order:
    def __init__(self, o_id=None, create_date=datetime.now(), status="Not Completed"):
        self.create_date = create_date.date()
        self.status = status
        self.id = o_id

    def sync_with_database(self, o_id=None):
        if o_id is None:
            o_id = self.id
        res = SQL_Caller.get_obj('Orders', o_id)
        if res == -1:
            return -1
        self.create_date = res[0][1]
        self.status = res[0][2]
        self.id = o_id
        return self

    async def insert_to_database(self, d_id):
        try:
            sql = "INSERT INTO orders (create_date, status) VALUES (%s, %s);"
            val = (str(self.create_date), self.status)
            cursor.execute(sql, val)
            sync_to_async(db.commit)
        except DatabaseError as err:
            print("Something went wrong: {}".format(err))
            return -1
        # print("Node", node_id, "Record inserted.")
        self.id = cursor.lastrowid
        await SQL_Caller.create_ref('disaster_orders', d_id, self.id)
        return self.id

    async def update_to_database(self):
        try:
            sql = "UPDATE orders SET status = %s WHERE id = %s;"
            val = (self.status, self.id)
            cursor.execute(sql, val)
            sync_to_async(db.commit)
        except DatabaseError as err:
            print("Something went wrong: {}".format(err))
            return -1
        # print("Node", node_id, "Record inserted.")
        return self.id

    def shipment_list(self, ):
        return SQL_Caller.search_obj('order_shipments', 'order_id = {}'.format(self.id))

    def shipment_locations(self, ):
        s_pair = self.shipment_list()
        s_list = []
        for x in s_pair:
            s_list.append(x[1])
        res = []
        for y in s_list:
            temp_shipment = Shipment.sync_with_database(y)
            res.append((temp_shipment.current_location_lon, temp_shipment.current_location_lat))
        return res

    def get_zip(self):
        disaster_id = SQL_Caller.search_obj('disaster_orders', 'order_id = {}'.format(self.id))[0][0]
        if disaster_id == -1:
            return -1
        else:
            cache_disaster = Disaster()
            cache_disaster.load_from_database(disaster_id)
        if cache_disaster.state_code and cache_disaster.county_code:
            return SQL_Caller.fips_to_zip(cache_disaster.state_code, cache_disaster.county_code)
        else:
            return -1

    def __str__(self):
        return "Order creation date: {} <br> Order status: {} <br> Order id: {} <br>".format(
            self.create_date, self.status, self.id)


class Shipment:
    def __init__(self, vendor=None, destination_state=None, destination_county=None, status="Created", vehicle_type=None,
                 current_location_lon=None, current_location_lat=None, content_id=None, content_quantity=None,
                 exp_date=None, s_id=None):
        self.vendor = vendor
        self.destination_state = destination_state
        self.destination_county = destination_county
        self.status = status
        self.vehicle_type = vehicle_type
        self.current_location_lon = current_location_lon
        self.current_location_lat = current_location_lat
        self.content_id = content_id
        self.content_quantity = content_quantity
        self.exp_date = exp_date
        self.id = s_id

    def sync_with_database(self, s_id=None):
        if s_id is None:
            s_id = self.id
        res = SQL_Caller.get_obj('shipments', s_id)
        if res == -1:
            return -1
        self.vendor = res[0][1]
        self.destination_state = res[0][2]
        self.destination_county = res[0][3]
        self.vehicle_type = res[0][4]
        self.current_location_lon = res[0][5]
        self.current_location_lat = res[0][6]
        self.content_id = res[0][7]
        self.content_quantity = res[0][8]
        self.exp_date = res[0][9]
        self.id = s_id
        return self

    async def insert_to_database(self, o_id):
        d_id = SQL_Caller.search_obj('disaster_orders', 'order_id = {}'.format(o_id))[0][0]
        dest_disaster = Disaster(d_id=d_id)
        dest_disaster.load_from_database()
        self.destination_state = dest_disaster.state_code
        self.destination_county = dest_disaster.county_code
        try:
            sql = "INSERT INTO shipments (vendor_id, state_fips, county_fips, status, vehicle_type, content_id, content_quantity) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            val = (self.vendor, self.destination_state, self.destination_county, self.status,
                   self.vehicle_type, self.content_id, self.content_quantity)
            cursor.execute(sql, val)
            sync_to_async(db.commit)
        except DatabaseError as err:
            print("Something went wrong: {}".format(err))
            return -1
        # print("Node", node_id, "Record inserted.")
        self.id = cursor.lastrowid
        await SQL_Caller.create_ref('order_shipments', o_id, self.id)
        return cursor.lastrowid

    async def update_to_database(self):
        try:
            sql = "UPDATE shipments SET vendor_id = %s, status = %s, vehicle_type = %s, content_id = %s, content_quantity = %s WHERE id = %s;"
            val = (self.vendor, self.status, self.vehicle_type, self.content_id, self.content_quantity, self.id)
            cursor.execute(sql, val)
            sync_to_async(db.commit)
        except DatabaseError as err:
            print("Something went wrong: {}".format(err))
            return -1
        # print("Node", node_id, "Record inserted.")
        return self.id

    def notify(self, destin_addr=None):
        if self.vendor is None:
            return -1
        if destin_addr:
            Platform_Alert.email_shipment_status(self, destin_addr)
        else:
            vendor_info = Vendor(self.vendor)
            vendor_info.sync_with_database()
            Platform_Alert.email_shipment_status(self, vendor_info.email)
        return 0

    def get_zip(self):
        if self.destination_state is not None and self.destination_county is not None:
            print("Initiate zip lookup")
            return SQL_Caller.fips_to_zip(self.destination_state, self.destination_county)
        else:
            return -1

    def __str__(self):
        return "Shipment ID: {} <br> Shipment vendor: {} <br> Destination state (FIPS): {} <br> Destination county (FIPS): {} <br> Shipment status: {} <br> Vehicle type: {} <br> Shipment longitude: {} <br> Shipment latitude: {} <br> Content id: {} <br> Content qunatity: {} <br> Expiration date: {} <br>".format(
            self.id, self.vendor, self.destination_state, self.destination_county, self.status, self.vehicle_type,
            self.current_location_lon, self.current_location_lat, self.content_id, self.content_quantity, self.exp_date)


class Vehicle:
    def __init__(self, vehicle_id=None, capacity=None, cap_unit=None, height=None, width=None, length=None, name=None,
                 dimension_unit=None):
        self.id = vehicle_id
        self.capacity = capacity
        self.cap_unit = cap_unit
        self.height = height
        self.width = width
        self.length = length
        self.name = name
        self.dimension_unit = dimension_unit

    def sync_with_database(self, vehicle_id, ):
        res = SQL_Caller.get_obj('Vehicles', self.id)
        if res == -1:
            return -1
        self.id = vehicle_id
        self.capacity = res[0][1]
        self.cap_unit = res[0][2]
        self.height = res[0][3]
        self.width = res[0][4]
        self.length = res[0][5]
        self.name = res[0][6]
        self.dimension_unit = res[0][7]
        return self


class Vendor:
    def __init__(self, vendor_id=None, company_name=None, rep_name=None, phone_num=None, email=None):
        self.id = vendor_id
        self.company_name = company_name
        self.rep_name = rep_name
        self.phone_num = phone_num
        self.email = email

    def sync_with_database(self,  vendor_id=None):
        if vendor_id is None:
            vendor_id = self.id
        res = SQL_Caller.get_obj('Vendors', vendor_id)
        if res == -1:
            return -1
        self.id = vendor_id
        self.company_name = res[0][1]
        self.rep_name = res[0][2]
        self.phone_num = res[0][3]
        self.email = res[0][4]
        return self


class Weather:
    def __init__(self, begin_date=None, latitude=None, longitude=None, weather_name=None, weather_id=None,
                 weather_type=None, wind_speed=None,
                 wind_direction=None, gust=None, clouds=None, rain=None, snow=None, pop=None):
        self.begin_date = begin_date
        self.latitude = latitude
        self.longitude = longitude
        self.weather_name = weather_name
        self.weather_id = weather_id
        self.weather_type = weather_type
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.gust = gust
        self.clouds = clouds
        self.rain = rain
        self.snow = snow
        self.pop = pop

    def load_current_weather(self, state_fips=0, county_fips=0, zipcode=None):
        if len(zipcode) != 5:
            zipcode = SQL_Caller.fips_to_zip(state_fips, county_fips)
        res = Platform_API.lookup_weather_forcast(zipcode)
        if res == -1:
            return -1
        self.latitude = res["coord"]["lat"]
        self.longitude = res["coord"]["lon"]
        self.weather_name = res["weather"][0]["main"]
        self.weather_id = res["weather"][0]["id"]
        self.weather_type = res["weather"][0]["description"]
        self.wind_speed = res["wind"]["speed"]
        self.wind_direction = res["wind"]["deg"]
        if "gust" in res["wind"]:
            self.gust = res["wind"]["gust"]
        self.clouds = res["clouds"]["all"]
        if "Rain" in res:
            self.rain = res["rain"]["1h"]
        if "Snow" in res:
            self.snow = res["snow"]["1h"]

    def __str__(self):
        return "City geo longitude: {} <br> City geo longitude: {} <br> Weather Status: {} <br> Weather Discription: {} <br> Wind Speed: {} <br> Wind Direction: {} <br> Gust Speed: {} <br> Cloud Coverage: {} <br> Rain Amount: {} <br> Snow Amount: {} <br>".format(
            self.longitude, self.latitude, self.weather_name, self.weather_type, self.wind_speed, self.wind_direction,
            self.gust, self.clouds, self.rain, self.snow)
