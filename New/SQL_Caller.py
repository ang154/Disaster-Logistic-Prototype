from django.db import connections
from django.db import DatabaseError
from . import Platform_API
from . import Platform_Objects
from . import db
from . import cursor
from asgiref.sync import sync_to_async
from datetime import datetime


# Get the array of objects from database with id, return -1 if error
def get_obj(table_name, val):
    try:
        sql = "select * from {} where id = '{}';".format(table_name, val)
        cursor.execute(sql)
        result = cursor.fetchall()
    except DatabaseError as err:
        print("Something went wrong in function get_obj with input {}, {}: {}".format(val, table_name, err))
        return -1
    # print("Node", node_id, "Stamp and Value received.")
    return result


# Check tables with id compatibility
def exist_check(table_name, val):
    try:
        sql = "select * from {} where id = '{}';".format(table_name, val)
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False
    except DatabaseError as err:
        print("Something went wrong in function exist_check: {}".format(err))
        return -1


# Get the newest incident of the same type of the disaster in the database
def newest_same_type(incident_type):
    try:
        sql = "select * FROM disasters WHERE incident_type = '{}' order by begin_date desc".format(incident_type)
        cursor.execute(sql)
        result = cursor.fetchall()
        newest_id = result[0][0]
        return newest_id
    except DatabaseError as err:
        print("Something went wrong in function newest_same_type: {}".format(err))
        return None


# Input: Disaster ID
# Output: Similar disaster's order
def suggest_order(d_id):
    if not exist_check('disasters', d_id):
        raise ValueError("Not a valid disaster ID")
    order_list = search_obj('disaster_orders', 'disaster_id = "{}"'.format(d_id))
    if len(order_list) >= 1:
        o_id = order_list[0][1]
        res_order = Platform_Objects.Order(o_id=o_id)
        res_order.sync_with_database()
        return res_order
    temp_disaster = Platform_Objects.Disaster(d_id=d_id)
    temp_disaster.load_from_database()
    d_id = newest_same_type(str(temp_disaster.incident_type))
    order_list = search_obj('disaster_orders', 'disaster_id = "{}"'.format(d_id))
    if len(order_list) >= 1:
        o_id = order_list[0][1]
        res_order = Platform_Objects.Order(o_id=o_id)
        res_order.sync_with_database()
        return res_order
    new_order = create_order(d_id)
    return new_order


# Input: Order details
# Output: Confirmation id
def create_order(disaster_id):
    new_order = Platform_Objects.Order()
    new_order.status = "Active"
    new_order.create_date = datetime.now()
    new_order.id = new_order.insert_to_database()
    create_ref('disaster_orders', disaster_id, new_order.id)
    return new_order


# Get the array of objects from database with quantifiers(xxx = xxx and yyy = yyy) acquired at the frontend,
# return -1 if error
def search_obj(table_name, quantifiers, selector='*'):
    try:
        sql = "select {} from {} where {};".format(selector, table_name, quantifiers)
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
    except DatabaseError as err:
        print("Something went wrong with search_obj: {}".format(err))
        return -1
    return result


# Create a reference on table for a and b, order matters due to foreign key
async def create_ref(table, a, b):
    try:
        sql = "INSERT INTO {} VALUES (%s, %s);".format(table)
        val = (a, b)
        cursor.execute(sql, val)
        sync_to_async(db.commit)
    except DatabaseError as err:
        print("Something went wrong: {}".format(err))
        return -1
    print("Relationship at ", table, "Added.")
    return 0


# Get table structure and order
def get_struct(table):
    try:
        sql = "DESCRIBE {};".format(table)
        cursor.execute(sql)
        result = cursor.fetchall()
    except DatabaseError as err:
        print("Something went wrong: {}".format(err))
        return -1
    # print("Relationship at ", table, "Added.")
    return result


# Get table structure name in order
def get_struct_name(table):
    structure = get_struct(table)
    result = []
    for x in structure:
        result.append(x[0])
    print("Structure names are: \n", result)
    return result


# Get table's max id
def get_max_id(table):
    sql = "SELECT MAX(id) from {};".format(table)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


# Create a relationship on table for a and b, order matters due to foreign key
async def remove_ref(table, a, b):
    table_struct_name = get_struct_name(table)
    quant = str(table_struct_name[0] + " = " + a + " and " + table_struct_name[1] + " = " + b)
    try:
        sql = "delete from %s where %s;"
        val = (table, quant)
        print(sql, val)
        await cursor.execute(sql, val)
        await sync_to_async(db.commit)()
    except DatabaseError as err:
        print("Something went wrong: {}".format(err))
        return -1
    # print("Relationship at ", table, "Added.")
    return 0


# Convert FIPS code to a list of matched zip code
def fips_to_zip(state_fips, county_fips):
    res_zip = search_obj('fips_zip', 'fips = {}'.format(str(state_fips) + str(county_fips)))[0][1]
    if len(str(res_zip)) == 5:
        return str(res_zip)
    else:
        return '0'+str(res_zip)


# Convert content ID to it's name
def content_name(content_id):
    return get_obj('content', content_id)[0][1]


# Convert content ID to it's name
def vendor_name(vendor_id):
    return get_obj('vendors', vendor_id)[0][1]


# Convert content ID to it's name
def vehicle_name(vehicle_id):
    return get_obj('vehicles', vehicle_id)[0][6]


# Search disasters by State
def disaster_top_50(state_acronym="PA"):
    return search_obj('disasters', 'state="{}" order by begin_date DESC limit 50'.format(state_acronym))


# Search orders by State
def order_top_50(state_acronym="PA"):
    try:
        sql = "select O.* from disasters D, orders O, disaster_orders R  where D.state = '{}' and R.order_id = O.id and R.disaster_id = D.id order by D.begin_date DESC limit 50;".format(state_acronym)
        cursor.execute(sql)
        result = cursor.fetchall()
    except DatabaseError as err:
        print("Something went wrong order_top_50: {}".format(err))
        return -1
    return result


# Search order by disaster id
def order_dy_disaster(disaster_id):
    try:
        sql = "select O.* from orders O, disaster_orders R  where R.disaster_id = '{}' and R.order_id = O.id order by O.create_date DESC limit 50;".format(disaster_id)
        cursor.execute(sql)
        result = cursor.fetchall()
    except DatabaseError as err:
        print("Something went wrong order_dy_disaster: {}".format(err))
        return -1
    return result


# Search order by State and Order Status
def order_status_disaster(order_status, disaster_id):
    try:
        sql = "select O.* from orders O, disaster_orders R  where R.order_id = O.id and R.disaster_id = '{}' and O.status = {} order by O.create_date DESC limit 50;".format(
            disaster_id, order_status)
        cursor.execute(sql)
        result = cursor.fetchall()
    except DatabaseError as err:
        print("Something went wrong order_status_disaster: {}".format(err))
        return -1
    return result


# Search order by State and Vendor ID
def shipment_state_vendor(vendor_id, state_acronym="PA"):
    try:
        sql = "select O.* from disasters D, orders O, disaster_orders R1, shipments S, order_shipments R2  where D.state = '{}' and R1.order_id = O.id and R1.disaster_id = D.id and S.vendor_id = '{}' and R2.order_id = O.id and R2.shipment_id = S.id order by D.begin_date DESC limit 50;".format(state_acronym, vendor_id)
        cursor.execute(sql)
        result = cursor.fetchall()
        print("API level result for order_state_vendor:\n")
        print(result)
        print("End\n")
    except DatabaseError as err:
        print("Something went wrong shipment_state_vendor: {}".format(err))
        return -1
    return result


# Search order by State and Order Status
def order_status_state(order_status, state_acronym="PA"):
    try:
        sql = "select O.* from disasters D, orders O, disaster_orders R  where D.state = '{}' and R.order_id = O.id and R.disaster_id = D.id and O.status = {} order by D.begin_date DESC limit 50;".format(
            state_acronym, order_status)
        cursor.execute(sql)
        result = cursor.fetchall()
        print("API level result for order_status_state:\n")
        print(result)
        print("End\n")
    except DatabaseError as err:
        print("Something went wrong order_status_state: {}".format(err))
        return -1
    return result


# Search order by Vendor ID and order status
def order_status_vendor(vendor_id, order_status):
    try:
        sql = "select O.* from orders O, shipments S, order_shipments R  where S.vendor_id = '{}' and R.order_id = O.id and R.shipment_id = S.id and O.status = {} order by O.create_date DESC;".format(vendor_id, order_status)
        cursor.execute(sql)
        result = cursor.fetchall()
        print("API level result for order_status_vendor:\n")
        print(result)
        print("End\n")
    except DatabaseError as err:
        print("Something went wrong order_status_vendor: {}".format(err))
        return -1
    return result


# Search order by State and Vendor ID
def order_state_vendor_status(vendor_id, order_status, state_acronym="PA"):
    try:
        sql = "select O.* from disasters D, orders O, disaster_orders R1, shipments S, order_shipments R2  where D.state = '{}' and R1.order_id = O.id and R1.disaster_id = D.id and S.vendor_id = '{}' and R2.order_id = O.id and O.status = {} and R2.shipment_id = S.id order by D.begin_date DESC limit 50;".format(
            state_acronym, vendor_id, order_status)
        cursor.execute(sql)
        result = cursor.fetchall()
        print("API level result for order_state_vendor:\n")
        print(result)
        print("End\n")
    except DatabaseError as err:
        print("Something went wrong order_state_vendor_status: {}".format(err))
        return -1
    return result
