import sys

from django.shortcuts import render
from django.http import JsonResponse

from . import Platform_Objects, SQL_Caller, Platform_Alert, Platform_API

from datetime import datetime


# returns the actual webpage html file in templates, python program files in TEST
# start website using
# cd test
# python manage.py runserver 0.0.0.0:8000


def disaster(request):
    if request.method == 'POST':
        d_id = request.POST.get('d_ID')
        d_state = request.POST.get('d_State')
        fips = request.POST.get('fips')

        if d_id != "":
            res_disaster = SQL_Caller.get_obj('disasters', d_id)
            return render(request, "DisasterFEMA.html", {'top_disasters': res_disaster})
        if d_state != "" and fips == "":
            top_disasters = SQL_Caller.disaster_top_50(d_state)
            return render(request, "allalertsFEMA.html", {'top_disasters': top_disasters})
        elif d_state == "" and fips != "":
            res_disaster = SQL_Caller.search_obj('disasters', 'county_code = {}'.format(fips))
            return render(request, "DisasterFEMA.html", {'top_disasters': res_disaster})
        elif d_state != "" and fips != "":
            res_disaster = SQL_Caller.search_obj('disasters', 'county_code = {} and state = "{}"'.format(fips, d_state))
            return render(request, "DisasterFEMA.html", {'top_disasters': res_disaster})
        else:
            return render(request, "DisasterFEMA.html")
    else:
        return render(request, "DisasterFEMA.html")


def orders(request):
    if request.method == 'POST':
        o_id = request.POST.get('o_id')
        d_id = request.POST.get('d_id')
        d_State = request.POST.get('d_State')
        o_status = request.POST.get('o_status')

        if o_id != "":
            res_order = SQL_Caller.get_obj('orders', o_id)
            return render(request, "OrdersFEMA.html", {'orders': res_order})
        elif d_id == "" and d_State == "" and o_status != "":
            res_order = SQL_Caller.search_obj('orders', 'status="{}" limit 50'.format(o_status))
            return render(request, "OrdersFEMA.html", {'orders': res_order})
        elif d_id == "" and d_State != "" and o_status == "":
            res_order = SQL_Caller.order_top_50(d_State)
            return render(request, "OrdersFEMA.html", {'orders': res_order})
        elif d_id == "" and d_State != "" and o_status != "":
            res_order = SQL_Caller.order_status_state(o_status, d_State)
            return render(request, "OrdersFEMA.html", {'orders': res_order})
        elif d_id != "" and o_status == "":
            res_order = SQL_Caller.order_dy_disaster(d_id)
            return render(request, "OrdersFEMA.html", {'orders': res_order})
        elif d_id != "" and o_status != "":
            res_order = SQL_Caller.order_status_disaster(o_status, d_id)
            return render(request, "OrdersFEMA.html", {'orders': res_order})
        else:
            return render(request, "OrdersFEMA.html")
    else:
        return render(request, "OrdersFEMA.html")


def alerts(request):
    top_disasters = SQL_Caller.disaster_top_50()
    return render(request, "allalertsFEMA.html", {'top_disasters': top_disasters})


def details(request):
    if request.method == 'POST':
        d_id = request.POST.get('d_id')
        o_id = request.POST.get('o_id')
        s_id = request.POST.get('s_id')

        if d_id != '' and SQL_Caller.exist_check('disasters', d_id):
            disasters = SQL_Caller.get_obj('disasters', d_id)
            context = {'disasters': disasters}
            temp_disaster = Platform_Objects.Disaster()
            temp_disaster.load_from_database(d_id)
            zipcode = SQL_Caller.fips_to_zip(temp_disaster.state_code, temp_disaster.county_code)
            print("Zipcode for the disaster are: "+str(zipcode))
            # print(Platform_API.lookup_weather_forcast(zipcode))
        elif o_id != '' and SQL_Caller.exist_check('orders', o_id):
            orders = SQL_Caller.get_obj('orders', o_id)
            context = {'orders': orders}
            temp_order = Platform_Objects.Order()
            temp_order.sync_with_database(o_id)
            zipcode = temp_order.get_zip()
            print("Zipcode for the order are: " + str(zipcode))
            # print(Platform_API.lookup_weather_forcast(zipcode))
        elif s_id != '' and SQL_Caller.exist_check('shipments', s_id):
            shipments = SQL_Caller.get_obj('shipments', s_id)
            context = {'shipments': shipments}
            temp_shipment = Platform_Objects.Shipment()
            temp_shipment.sync_with_database(s_id)
            zipcode = SQL_Caller.fips_to_zip(temp_shipment.destination_state, temp_shipment.destination_county)
            # (Platform_API.lookup_weather_forcast(zipcode))
            print("Zipcode for the shipment are: " + str(zipcode))
        else:
            return render(request, "Info.html", {'cityid': Platform_API.zip_to_cityid()})
        if len(zipcode) == 5:
            temp_weather = Platform_Objects.Weather()
            temp_weather.load_current_weather(zipcode=zipcode)
            context['zipcode'] = zipcode
            context['a_map'] = "https://maps.apple.com/?q={}".format(zipcode)
            context['g_map'] = "https://www.google.com/maps/search/?api=1&query={}".format(zipcode)
            context['weather_statement'] = str(temp_weather).replace('<br>', '\n')
        return render(request, "Info.html", context)
    else:
        return render(request, "Info.html", {'zip': 10036})


def index(request):
    if request.method == 'POST':
        d_id = request.POST.get('d_ID')
        d_state = request.POST.get('d_State')
        fips = request.POST.get('fips')

        if d_id != "":
            res_disaster = SQL_Caller.get_obj('disasters', d_id)
            return render(request, "DisasterFEMA.html", {'top_disasters': res_disaster})
        if d_state != "" and fips == "":
            top_disasters = SQL_Caller.disaster_top_50(d_state)
            return render(request, "allalertsFEMA.html", {'top_disasters': top_disasters})
        elif d_state == "" and fips != "":
            res_disaster = SQL_Caller.search_obj('disasters', 'county_code = {}'.format(fips))
            return render(request, "DisasterFEMA.html", {'top_disasters': res_disaster})
        elif d_state != "" and fips != "":
            res_disaster = SQL_Caller.search_obj('disasters', 'county_code = {} and state = "{}"'.format(fips, d_state))
            return render(request, "DisasterFEMA.html", {'top_disasters': res_disaster})
        else:
            return render(request, "index.html")
    else:
        return render(request, "index.html")


async def create_o(request):
    if request.method == 'POST':
        d_id = request.POST.get('d_id')
        o_status = request.POST.get('o_status')
        email_addr = request.POST.get('email')
        if SQL_Caller.exist_check('disasters', d_id):
            cache_order = Platform_Objects.Order()
            cache_order.status = o_status
            await cache_order.insert_to_database(d_id)
            o_id = cache_order.id
            context = {'o_id': o_id}
            suggestion = SQL_Caller.suggest_order(d_id)
            if SQL_Caller.exist_check('orders', suggestion.id):
                suggest_list = suggestion.shipment_list()
                if len(suggest_list) > 0:
                    suggest_shipments = []
                    for s_id in suggest_list:
                        suggest_shipments.append(SQL_Caller.get_obj('shipments', s_id))
                        print("Suggest shipments: " + s_id)
                    context['suggest_shipments'] = suggest_shipments
            if email_addr != "":
                Platform_Alert.email_new_order(cache_order, email_addr)
            return render(request, "CreateOrdersFEMA.html", context)
    else:
        return render(request, "CreateOrdersFEMA.html")


def shipments(request):
    if request.method == 'POST':
        d_id = request.POST.get('d_id')
        o_id = request.POST.get('o_id')
        s_id = request.POST.get('s_id')
        s_state = request.POST.get('s_state')
        s_vendor = request.POST.get('vendors')
        c_id = request.POST.get('type')

        search_table = 'shipments S'
        selector = 'S.*'
        quantifiers = ''
        if s_id == o_id == d_id == s_state == s_vendor == c_id == '':
            return render(request, "ShipmentsFEMA.html")
        elif s_id != "":
            res_shipments = SQL_Caller.get_obj(search_table, s_id)
            return render(request, "ShipmentsFEMA.html", {'res_shipments': res_shipments})
        elif o_id != "":
            search_table += ', order_shipments R1'
            quantifiers += 'R1.order_id = {} and R1.shipment_id = S.id'.format(o_id)
        elif d_id != "":
            search_table += ', order_shipments R1, disaster_orders R2'
            quantifiers += 'R2.disaster_id = "{}" and R1.order_id = R2.order_id and R1.shipment_id = S.id'.format(d_id)
        elif s_state != "":
            quantifiers += 'S.state_fips = {}'.format(s_state)
        elif s_vendor != "":
            quantifiers += 'S.vendor_id = {}'.format(s_vendor)
        elif c_id != "":
            quantifiers += 'S.content_id = {}'.format(c_id)
        res_shipments = SQL_Caller.search_obj(search_table, quantifiers, selector)
        if res_shipments != 0 and res_shipments != -1:
            return render(request, "ShipmentsFEMA.html", {'res_shipments': res_shipments})
    else:
        return render(request, "ShipmentsFEMA.html")


async def create_s(request):
    if request.method == 'POST':
        o_id = request.POST.get('o_id')
        vendors = request.POST.get('vendors')
        vehicle = request.POST.get('vehicle')
        c_id = request.POST.get('c_id')
        amount = request.POST.get('amount')
        email_addr = request.POST.get('email')
        if SQL_Caller.exist_check('orders', o_id):
            cache_shipment = Platform_Objects.Shipment(vendor=vendors, vehicle_type=vehicle, content_id=c_id, content_quantity=amount)
            await cache_shipment.insert_to_database(o_id)
            s_id = cache_shipment.id
            res_shipments = SQL_Caller.get_obj('shipments', s_id)
            if email_addr != "":
                Platform_Alert.email_new_order(cache_shipment, email_addr)
            return render(request, "CreateShipmentsFEMA.html", context={'res_shipments': res_shipments})
        return render(request, "CreateShipmentsFEMA.html")
    else:
        return render(request, "CreateShipmentsFEMA.html")


async def update_s(request):
    if request.method == 'POST':
        s_id = request.POST.get('s_id')
        vendors = request.POST.get('vendors')
        vehicle = request.POST.get('vehicle')
        c_id = request.POST.get('c_id')
        amount = request.POST.get('amount')
        if SQL_Caller.exist_check('shipments', s_id):
            cache_shipment = Platform_Objects.Shipment(s_id=s_id)
            cache_shipment.vendor = vendors
            cache_shipment.vehicle_type = vehicle
            cache_shipment.content_id = c_id
            cache_shipment.content_quantity = amount
            await cache_shipment.update_to_database()
            s_id = cache_shipment.id
            res_shipments = SQL_Caller.get_obj('shipments', s_id)
            return render(request, "UpdateShipmentsFEMA.html", context={'res_shipments': res_shipments})
    else:
        return render(request, "UpdateShipmentsFEMA.html")
