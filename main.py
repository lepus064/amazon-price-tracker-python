import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import time

def get_item(item_id, which_amazon='https://www.amazon.co.jp/dp/'):
    data = requests.get(which_amazon + item_id)
    soup = BeautifulSoup(data.text, "lxml")
    price_content = soup.find(id='price')
    price = price_content.find(id="priceblock_ourprice")
    if(price == None):
        price = price_content.find(id="priceblock_dealprice")
    price = int(price.string.split(" ")[-1].replace(',',''))
    productTitle = soup.find(id='productTitle').string.lstrip().rstrip()
    return productTitle, price, str(which_amazon + item_id)

def send_email(info,msg_content):

    try:
        # Try to login smtp server
        s = smtplib.SMTP(info['smtp_url'])
        s.ehlo()
        s.starttls()
        s.login(info['sender'], info['sender-password'])
    except smtplib.SMTPAuthenticationError:
        # Log in failed
        print(smtplib.SMTPAuthenticationError)
        print('[Mail]\tFailed to login')
    else:
        # Log in successfully
        print('[Mail]\tLogged in! Composing message..')

        for receiver in info['receivers']:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = msg_content['Subject']
            msg['From'] = info['sender']
            msg['To'] = receiver

            text = msg_content['Content']

            part = MIMEText(text, 'plain')
            msg.attach(part)
            s.sendmail(info['sender'], receiver, msg.as_string())
            print('[Mail]\tMessage has been sent to %s.' % (receiver))


def main():

    nowtime = datetime.now()
    nowtime_Str = nowtime.strftime('%Y-%m-%d %H:%M:%S')

    email_info = {
        "smtp_url": "smtp.gmail.com:587",
        "sender": "GMAIL_acount",
        "sender-password": "PASSWORD",
        "receivers": ["EAMIL_ADRESS_LIST"]
    }

    item_ids = ['B0792PG3S9']

    set_price = 880
    price_is_not_lower = True

    print('Start tracking...')
    print('Set price is: ',set_price)

    while(price_is_not_lower):

        print('Now checking the price...')

        for item in item_ids:

            productName, price, item_page_url = get_item(item_id=item)
            if(price < set_price):
                msg_content = {}
                msg_content['Subject'] = '[Amazon] %s Price Alert - %s' % (productName, price)
                msg_content['Content'] = '[%s]\nThe price is currently %s !!\nURL to webpage: %s' % (
                nowtime_Str, price, item_page_url)
                msg_content['Price'] = price
                msg_content['URL'] = item_page_url
                msg_content['Product'] = productName
                msg_content['ServerState'] = ""
                msg_content['code'] = 1  # 2 is server state

                print('Current price is lower than set price!!')

                send_email(email_info, msg_content)
                price_is_not_lower = False
                print('End the program')
            else:
                print('The price now is: ', price)


        if(price_is_not_lower):
            thisIntervalTime = 900

            # calculate next triggered time
            dt = datetime.now() + timedelta(seconds=thisIntervalTime)
            print('Sleeping for %d seconds, next time start at %s\n' % (thisIntervalTime, dt.strftime('%Y-%m-%d %H:%M:%S')))
            time.sleep(thisIntervalTime)





if __name__ == '__main__':
    main()