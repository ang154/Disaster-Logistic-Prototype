from django.db import models
from . import Platform_API
from . import Platform_Alert
from datetime import datetime


class Vendor(models.Model):
    company_name = models.CharField(max_length=250)
    rep_name = models.CharField(max_length=250)
    phone_num = models.CharField(max_length=250)
    email = models.CharField(max_length=250)


class Vehicle(models.Model):
    capacity = models.FloatField()
    cap_unit = models.CharField(max_length=250)
    height = models.FloatField()
    width = models.FloatField()
    length = models.FloatField()
    name = models.CharField(max_length=250)
    dimension_unit = models.CharField(max_length=100)


class Content(models.Model):
    life = models.FloatField()
    unit = models.CharField(max_length=30)
    name = models.CharField(max_length=50)
    vendors = models.ManyToManyField(Vendor)

    def get_cor_vendors(self):
        return self.vendors.all()

    def __str__(self):
        return "Content name: {} <br> Unit: {} <br> Shelf life (in months): {} <br>".format(self.name, self.unit,self.life)


class FIPSZip(models.Model):
    fips = models.CharField(max_length=5)
    zipcode = models.CharField(max_length=5)


class Shipment(models.Model):
    vendor = models.CharField(max_length=250)
    destination_state = models.PositiveIntegerField()
    destination_county = models.CharField(max_length=10)
    status = models.CharField(max_length=250)
    vehicle_type = models.PositiveIntegerField()
    current_location_lon = models.FloatField()
    current_location_lat = models.FloatField()
    content_id = models.PositiveIntegerField()
    content_quantity = models.PositiveIntegerField()
    exp_date = models.DateField()

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
            fips = str(self.destination_state)+self.destination_county
            print("Initiate zip lookup for:"+fips)
            first_pair = FIPSZip.objects.filter(fips=fips)[0]
            return first_pair.zipcode
        else:
            return -1

    def __str__(self):
        return "Shipment ID: {} <br> Shipment vendor: {} <br> Destination state (FIPS): {} <br> Destination county (FIPS): {} <br> Shipment status: {} <br> Vehicle type: {} <br> Shipment longitude: {} <br> Shipment latitude: {} <br> Content id: {} <br> Content qunatity: {} <br> Expiration date: {} <br>".format(
            self.id, self.vendor, self.destination_state, self.destination_county, self.status, self.vehicle_type,
            self.current_location_lon, self.current_location_lat, self.content_id, self.content_quantity, self.exp_date)


class Order(models.Model):
    status = models.CharField(max_length=250)
    create_date = models.DateField()
    shipments = models.ManyToManyField(Shipment)

    def shipment_list(self, ):
        return self.shipments.all()

    def shipment_locations(self, ):
        s_list = self.shipments.all()
        res = []
        for y in s_list:
            res.append((y.current_location_lon, y.current_location_lat))
        return res

    def get_zip(self):
        disaster = Disaster.objects.get(orders=Order)
        if disaster.state_code and disaster.county_code:
            return disaster.get_zip()
        else:
            return -1

    def __str__(self):
        return "Order creation date: {} <br> Order status: {} <br> Order id: {} <br>".format(self.create_date,
                                                                                             self.status, self.id)


class Disaster(models.Model):
    id = models.CharField(max_length=250, primary_key=True)
    lastRefresh = models.DateField()
    area = models.CharField(max_length=250)
    state_code = models.PositiveIntegerField()
    county_code = models.PositiveIntegerField()
    begin_date = models.DateField()
    title = models.CharField(max_length=250)
    incident_type = models.CharField(max_length=250)
    declare_type = models.CharField(max_length=250)
    state = models.CharField(max_length=5)
    orders = models.ManyToManyField(Order)

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
        self.save()

    def get_zip(self):
        if self.county_code and self.state_code:
            fips = str(self.state_code) + self.county_code
            print("Initiate zip lookup for:" + fips)
            first_pair = FIPSZip.objects.filter(fips=fips)[0]
            return first_pair.zipcode
        else:
            return -1

    def __str__(self):
        return "Disaster ID: {} <br> Disaster state: {} <br> Disaster declare type: {} <br> Disaster incident type: {} <br> Disaster title: {} <br> Begin date: {} <br> State FIPS code: {} <br> County FIPS code: {} <br> Area name: {} <br>".format(
            self.id, self.state, self.declare_type, self.incident_type, self.title, self.begin_date, self.state_code,
            self.county_code, self.area)


class Weather(models.Model):
    weather_name = models.CharField(max_length=250)
    weather_id = models.PositiveIntegerField()
    weather_type = models.CharField(max_length=10)
    wind_direction = models.FloatField()
    wind_speed = models.PositiveIntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    begin_date = models.DateField()
    gust = models.FloatField()
    clouds = models.FloatField()
    rain = models.FloatField()
    snow = models.FloatField()
    pop = models.FloatField()

    def load_current_weather(self, state_fips=0, county_fips=0, zipcode=None):
        if len(zipcode) != 5:
            fips = str(state_fips) + str(county_fips)
            print("Initiate zip lookup for:" + fips)
            zipcode = FIPSZip.objects.filter(fips=fips)[0]
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
