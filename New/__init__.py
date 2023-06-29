from django.db import connections
global db, cursor
import tracemalloc
tracemalloc.start()
from asgiref.sync import sync_to_async
db = db_connection = connections['data']
cursor = db_connection.cursor()

from New import Email_Sender
from New import Platform_API
from New import Platform_Alert
from New import SQL_Caller
from New import Platform_Objects
from datetime import datetime

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

