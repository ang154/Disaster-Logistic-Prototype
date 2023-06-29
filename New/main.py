from . import non_active, Platform_Objects, Platform_API, SQL_Caller


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test_disaster = Platform_Objects.Disaster(d_id='01aeec6d-4577-437c-a02c-649330d88bf3')
    test_disaster.load_from_database('01aeec6d-4577-437c-a02c-649330d88bf3')
    print(SQL_Caller.search_obj('disasters', 'state="PA" order by begin_date DESC limit 50'))
    # Pass:
    """
    print(test_disaster)
    Platform_Alert.email_alert(test_disaster)
    """
    # SQL_Caller.remove_ref('disaster_orders', "asd", "asdf")
    # print(SQL_Caller.fips_to_zip(test_disaster.state_code, test_disaster.county_code))
    # test_weather = Platform_Objects.Weather()
    # test_weather.load_current_weather(test_disaster.state_code, test_disaster.county_code, )
    # Email_Sender.send_email("New Disaster Detected", (str(test_disaster)+"<p> <b>Here are the current weather:</b> </p>" + str(test_weather)))
    # Progress:
    # newest_date = SQL_Caller.newest_date()
    # Platform_API.newest_disasters_fema(str(newest_date))
