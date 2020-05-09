"""Send email or sms with forecast
"""
import smtplib

import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

from quickstart import if_work


def get_forecast(hour):
    """Download weather forecast from website and return it in formatted string
    """
    print('Downloading forecast...')
    page = requests.get('https://pogoda.interia.pl/prognoza-szczegolowa-gdansk,cId,8048')
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find single weather entry on the website
    forecast_list = soup.find('div', class_="weather-forecast-hbh-main-list")
    forecast_item = forecast_list.find_all(class_="weather-forecast")
    today = forecast_item[0]
    weather_entry = today.find_all(class_='weather-entry')

    # Create a dictionary with formatted forecast data
    weather_dict = {}
    for entry in weather_entry:
        if entry.find('span', class_='hour').get_text() == hour:
            weather_dict['hour'] = f"{entry.find('span', class_='hour').get_text()}:00"
            weather_dict['temp'] = entry.find(class_='forecast-temp').get_text()
            weather_dict['feel_temp'] = entry.find(class_='forecast-feeltemp').get_text()[11::]
            weather_dict['desc'] = entry.find(class_='forecast-phrase').get_text()
            weather_dict['wind'] = f"{(entry.find(class_='speed-value').get_text())}km/h"
            weather_dict['cloudy'] = (entry.find(class_='entry-precipitation-value cloud-cover').get_text())
            weather_dict['rain'] = (entry.find(class_='entry-precipitation-value rain').get_text())

    # Put all the data into one formatted string
    forecast_formatted = f"Pogoda na godzinę {weather_dict['hour']}:\n{weather_dict['desc']}\nTemperatura: {weather_dict['temp']} " \
                         f"/ Odczuwalna: {weather_dict['feel_temp']}\nWiatr: {weather_dict['wind']}\n" \
                         f"Zachmurzenie: {weather_dict['cloudy']}\nDeszcz: {weather_dict['rain']}"

    return forecast_formatted


def send_email(hour):
    """Send email with forecast string
    """
    gmail_user = 'user@gmail.com'
    gmail_password = 'password'
    subject = 'Pogoda na dzisiaj!'
    body = get_forecast(hour)
    msg = f'Subject: {subject}\n\n{body}'

    try:
        print('Sending email...')
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, gmail_user, msg.encode('utf8'))
        server.close()
        print('Email sent!')
    except:
        print('Something went wrong')


def send_sms(hour):
    """Send sms with forecast string
    """
    account_sid = '111'
    auth_token = '111'
    client = Client(account_sid, auth_token)

    twilio_number = '+12111111111'
    my_number = '+48111111111'

    message = client.messages.create(
        body=get_forecast(hour),
        from_=twilio_number,
        to=my_number
    )

    print(message.sid)


hours = if_work()
