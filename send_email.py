import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from get_flight_info import FlightInfo

# TODO Valuable Information

# Set up logging
logging.basicConfig(level=logging.INFO)

# Import flight_data
FLIGHT_DATA = FlightInfo()
CITY_DATA = FLIGHT_DATA.get_city_data_dict()

# Additional Variables
CUSTOMER_EP = "https://api.sheety.co/9aad2a16529f732d9919e82247b52109/signUpSheet/sheet1"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kteliteagain@gmail.com"
SMTP_PASSWORD = "suhfxarxljnkngjx"
FROM_MAIL = "kteliteagain@gmail.com"


def customer_emails():
    with requests.get(url=CUSTOMER_EP) as response:
        if response.status_code == 200:
            json_data = response.json()
            # Do something with the object
            members_list = json_data['sheet1']
            members_dict = {item['name']: item['email'] for item in members_list}
            return members_dict
        else:
            print(f"Failed to fetch spreadsheet data. Error: {response.text}")


class SendMail:
    def __init__(self):
        self.members = customer_emails()
        self.message = self.message_object()

    def message_object(self):
        msg = MIMEMultipart()
        msg['From'] = FROM_MAIL
        msg['Subject'] = 'Flight Jackpots!'
        return msg

    def send_mail(self):
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)

            for member_name, member_email in self.members.items():
                self.message['To'] = member_email

                for city, flights in CITY_DATA.items():
                    for flight in flights:
                        price = flight['price']
                        low_price = flight['low_price']
                        local_departure = flight['local_departure']
                        local_arrive = flight['local_arrival']
                        # short_url = flight['short_url']

                        if price < low_price:
                            send_message = f"""\
                            <html>
                              <body>
                                <p>Jackpot! There is an available flight to {city} that costs ZAR:{price}</p>
                                <p>Flight Information:</p>
                                <ul>
                                  <li>Flight is expected to leave SA on: {local_departure}</li>
                                  <li>And arrive in {city} on: {local_arrive}</li>
                                  <li>Short Link to flight info: None</li>
                                </ul>
                              </body>
                            </html>
                            """
                            self.message.attach(MIMEText(send_message, 'html'))

                try:
                    server.send_message(self.message)
                    print(f"Email sent successfully to {member_email}!")
                except smtplib.SMTPException as error:
                    print("An error occurred while sending the email:")
                    print(error)
