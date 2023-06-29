from . import Email_Sender
from . import Platform_Objects


def email_alert(disaster, destin_email="tony.q.xiang@icloud.com"):
    # Input: New actable alert details
    # Output: Email sent to FEMA
    Email_Sender.send_email("New Disaster Detected", str(disaster), destin_email)
    return 0


def email_disaster_status(disaster, destin_email="tony.q.xiang@icloud.com"):
    # Input: Updated disaster details
    # Output: Email sent to FEMA
    Email_Sender.send_email("Disaster Status Updated", str(disaster), destin_email)
    return 0


def email_order_status(order, destin_email="tony.q.xiang@icloud.com"):
    # Input: Updated shipment or order status details
    # Output: Email sent to FEMA
    Email_Sender.send_email("Order Status Updated", str(order), destin_email)
    return 0


def email_shipment_status(shipment, destin_email="tony.q.xiang@icloud.com"):
    # Input: Updated shipment or order status details
    # Output: Email sent to FEMA
    Email_Sender.send_email("Shipment Status Updated", str(shipment), destin_email)
    return 0


def email_new_order(order, destin_email="tony.q.xiang@icloud.com"):
    # Input: New order details
    # Output: Emails sent to all related vendors, Google or Microsoft form with response received
    Email_Sender.send_email("New Actable Order Created", str(order), destin_email)
    return 0

