from fitbitPackage import fitbit_api, get_right_dateFormat

print(fitbit_api.get_authorize_url())
fitbit_api.start_response_poll()

client = fitbit_api.get_auth_client()

today_date = get_right_dateFormat()
yesterday_date = get_right_dateFormat(-1)

fit_statsHR = client.intraday_time_series('activities/steps', base_date=today_date, detail_level='15min')
print('Steps at ' + today_date + ': ' + fit_statsHR['activities-steps'][0]['value'])