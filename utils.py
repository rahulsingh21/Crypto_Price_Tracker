from datetime import datetime, timedelta
from collections import namedtuple
import os, smtplib
import traceback


DateCondition = namedtuple("DateCondition", "start, end")

def get_from_and_to_from_date(date):
    date_obj = datetime.strptime(date, "%d-%m-%Y")
    from_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    to_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    print(f"From Date : {from_date}, To Date : {to_date}")
    return DateCondition(from_date, to_date)

def send_alert(price, lower_or_upper, threshold):
    try:
        message = f"""\
        Subject: BTC price alert
        To: {os.environ['ALERT_EMAIL']}
        From: {os.environ['SENDER']}

        The price of BTC ({price} USD) breached the {lower_or_upper} threshold of {threshold}."""

        with smtplib.SMTP(os.environ['HOST'], os.environ['PORT']) as server:
            server.login(os.environ['USERNAME'], os.environ['PASSWORD'])
            breakpoint()
            res = server.sendmail(os.environ['SENDER'], os.environ['ALERT_EMAIL'], message)
    except Exception:
        print("Some error occured while sending the email ")
        traceback.print_exc()