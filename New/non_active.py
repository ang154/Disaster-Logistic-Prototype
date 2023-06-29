from django.db import connections
from django.db import DatabaseError
from . import Platform_API, SQL_Caller, Platform_Objects
from datetime import datetime
from . import db
from . import cursor
from asgiref.sync import sync_to_async


# Get the newest incident begin date of the disaster in the database
def newest_date():
    try:
        sql = "SELECT MAX(begin_date) AS newest_begin_date FROM disasters"
        cursor.execute(sql)
        result = cursor.fetchone()
        newest_begin_date = result[0]
        return newest_begin_date
    except DatabaseError as err:
        print("Something went wrong in function newest_date: {}".format(err))
        return None


# Input: Available disaster details
# Output: qualified disaster ID
def lookup_disaster(d_id=None, d_state=None, county_fips=None, declaration=None):
    qualifiers = ''
    if d_id is not None:
        res = SQL_Caller.get_obj('disasters', d_id)
        return res
    if d_state is not None:
        if len(qualifiers) == 0:
            qualifiers += 'state = {}'.format(d_state)
        else:
            qualifiers += ' and state = {}'.format(d_state)
    if county_fips is not None:
        if len(qualifiers) == 0:
            qualifiers += 'county_code = {}'.format(county_fips)
        else:
            qualifiers += ' and county_code = {}'.format(county_fips)
    if declaration is not None:
        if len(qualifiers) == 0:
            qualifiers += 'declaration_type = {}'.format(declaration)
        else:
            qualifiers += ' and declaration_type = {}'.format(declaration)
    if len(qualifiers) > 0:
        return SQL_Caller.search_obj('disasters', qualifiers)
    else:
        return 0


# Input: Available order details
# Output: qualified order ID
def lookup_order(o_id=None, destination_state=None, content_id=None, s_order_status=None):
    qualifiers = ''
    involvements = 'orders O'
    if o_id is not None:
        res = SQL_Caller.get_obj('orders', o_id)
        return res
    if destination_state is not None:
        involvements += ', disaster_orders r1, Disasters D'
        if len(qualifiers) != 0:
            qualifiers += ' and '
        qualifiers += 'r1.disaster_id = D.id and r1.order_id = O.id and D.state = {}'.format(destination_state)
    if (content_id is not None) or (s_order_status is not None):
        involvements += ', orders_shipments r2, Shipments S'
        if len(qualifiers) != 0:
            qualifiers += ' and '
        qualifiers += 'r2.shipment_id = S.id and r2.order_id = O.id'
        if content_id is not None:
            qualifiers += ' and S.content_id = {}'.format(content_id)
        if s_order_status is not None:
            qualifiers += ' and S.status = {}'.format(s_order_status)
    if len(qualifiers) > 0:
        return SQL_Caller.search_obj(involvements, qualifiers)
    else:
        return 0


# Input: Available shipment details
# Output: Shipment info
def lookup_shipment(s_id=None, destination_state=None, vendor_id=None, content_id=None, vehicle_type=None):
    qualifiers = ''
    involvements = 'shipments S'
    if s_id is not None:
        res = SQL_Caller.get_obj('shipments', s_id)
        return res
    if destination_state is not None:
        involvements += ', disaster_orders r1, Disasters D, Orders O, orders_shipments r2'
        if len(qualifiers) != 0:
            qualifiers += ' and '
        qualifiers += 'r1.disaster_id = D.id and r1.order_id = O.id and D.state = {} and r2.shipment_id = S.id and ' \
                      'r2.order_id = O.id'.format(destination_state)
    if vendor_id is not None:
        involvements += ', shipment_vendors r3, Vendors V'
        if len(qualifiers) != 0:
            qualifiers += ' and '
        qualifiers += 'r3.vendor_id = V.id and r3.shipment_id = S.id and V.id = {}'.format(vendor_id)
    if content_id is not None:
        if len(qualifiers) != 0:
            qualifiers += ' and '
        qualifiers += 'S.content_id = {}'.format(content_id)
    if vehicle_type is not None:
        if len(qualifiers) != 0:
            qualifiers += ' and '
        qualifiers += 'S.vehicle_type = {}'.format(vehicle_type)
    if len(qualifiers) > 0:
        return SQL_Caller.search_obj(involvements, qualifiers)
    else:
        return 0


# Input: Disaster ID
# Output: Disaster info database side
def disaster_status(d_id):
    return SQL_Caller.get_obj('disasters', d_id)


# Input: Order ID
# Output: Order info database side
def order_status(o_id):
    return SQL_Caller.get_obj('order', o_id)


# Input: Shipment ID
# Output: Shipment info database side
def shipment_status(s_id):
    return SQL_Caller.get_obj('disasters', s_id)


# Input: Order details
# Output: Confirmation id
def create_order(disaster_id):
    new_order = Platform_Objects.Order()
    new_order.status = "Active"
    new_order.create_date = datetime.now()
    new_order.id = new_order.insert_to_database()
    SQL_Caller.create_ref('disaster_orders', disaster_id, new_order.id)
    return new_order


# Input: Shipment details
# Output: Confirmation id
def create_shipment(order_id, vendor_id, destination_state, destination_county, vehicle_type, content_id, content_quantity):
    new_shipment = Platform_Objects.Shipment()
    new_shipment.vendor = vendor_id
    new_shipment.status = "New"
    new_shipment.destination_state = destination_state
    new_shipment.destination_county = destination_county
    new_shipment.content_id = content_id
    new_shipment.content_quantity = content_quantity
    new_shipment.vehicle_type = vehicle_type
    new_shipment.id = new_shipment.insert_to_database()
    SQL_Caller.create_ref('order_shipments', order_id, new_shipment.id)
    return new_shipment.id


def disaster_historical_weather(d_id):
    # Input: Disaster ID
    # Output: Past few days weather
    return 0


def disaster_future_weather(d_id):
    # Input: Disaster ID
    # Output: Forcast few days weather
    return 0


def similar_disasters(d_id):
    # Input: Disaster ID
    # Output: Qualified disasters' Disaster ID
    return 0


# Input: Disaster ID
# Output: Similar disaster's order
def suggest_order(d_id):
    if not SQL_Caller.exist_check('disasters', d_id):
        raise ValueError("Not a valid disaster ID")
    order_list = SQL_Caller.search_obj('disaster_orders', 'disaster_id = "{}"'.format(d_id))
    if len(order_list) >= 1:
        o_id = order_list[0][1]
        res_order = Platform_Objects.Order(o_id=o_id)
        res_order.sync_with_database()
        return res_order
    temp_disaster = Platform_Objects.Disaster(d_id=d_id)
    temp_disaster.load_from_database()
    d_id = SQL_Caller.newest_same_type(str(temp_disaster.incident_type))
    order_list = SQL_Caller.search_obj('disaster_orders', 'disaster_id = "{}"'.format(d_id))
    if len(order_list) >= 1:
        o_id = order_list[0][1]
        res_order = Platform_Objects.Order(o_id=o_id)
        res_order.sync_with_database()
        return res_order
    new_order = create_order(d_id)
    return new_order


def publish_order(o_id):
    # Input: Order Info
    # Output: Confirm and trigger to other functions
    return 0