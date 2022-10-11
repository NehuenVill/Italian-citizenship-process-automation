import smtplib
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
import imaplib
import email
import ssl
from datetime import date, datetime
from getpass import getpass
from bs4 import BeautifulSoup
import json

url = 'https://prenotami.esteri.it/Home'

e_mail = ''
google_app_pass = ''
itgov_pass = ''
mail_pass = ''
option = ''
g_mail = ''

with open('user_info.json') as f:

    info = json.load(f)

    e_mail = info['email']
    google_app_pass = info['goggle app']
    itgov_pass = info['Italian government website password']
    mail_pass = info['email password']
    option = info['option']
    g_mail = info['gmail']

# Adapt options_list to the Montevideo embasy.
# Change all the prints to log the stages of the process better.

options_list = {
                'sc'   : 'SERVICIOS CONSULARES',
                'div'  : 'DOCUMENTOS DE IDENTIDAD Y DE VIAJE',
                'vfue' : ['VISADOS', 'Solamente familiares de ciudadanos UE'],
                'l'    : 'LEGALIZACIONES',
                'vtt'  : ['VISADOS', 'Todas tipologias de Visados'],
                'rpec' : 'REGISTRO DE LA POBLACIÓN Y ESTADO CIVIL',
                'vdvv' : ['VISADOS', 'Declaraciones de Valor y Visados de Estudio - Estudiantes con preinscripciòn Universitaly']}
    

def send_mail_notification(email, passw, msg):

    port = 465

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        
        server.login(email, passw)
        
        server.sendmail(email, email, msg)


def find_email_code(mail, password):

    imap_server = "outlook.office365.com"
    code = ''

    while code == '':

        sleep(5)

        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(mail, password)

        print('Trying to find the code...')

        imap.select("INBOX")
        
        _, messages = imap.search(None, "ALL")

        email_nums = messages[0].split()

        last_mail_num = email_nums[len(email_nums)-1]

        _, data = imap.fetch(last_mail_num, '(RFC822)')
            
        msg = email.message_from_bytes(data[0][1])

        subject = msg.get('Subject')

        body = str(msg.get_payload(None, True))

        print(f'Subject: {subject}')

        print(body)

        if 'OTP Code:' in body:

            code = body.replace("""b'<meta http-equiv="Content-Type" content="text/html; charset=utf-8">OTP Code:""", '').replace("'", '')

        print(code)
        
        imap.close()  
        imap.logout()
    
    print(f'The code is: {code}')

    return code



def automate(url, email, user_pass, email_pass, google_app_pass, gmail, opcion):

    print('......................Comenzando proceso......................')

    #password = getpass('Contraseña para aplicaciones de google: ')

    #user_pass = getpass('Contraseña para la página del gobierno italiano: ')

    #email_pass = getpass('Contraseña de tu e-mail: ')

    #opcion = getpass('Opcion: ')

    driver = webdriver.Chrome()

    driver.get(url)

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located, (By.ID, 'login-email'))

    email_in = driver.find_element(By.XPATH, "//input[@type='email']")

    pass_in = driver.find_element(By.XPATH, "//input[@type='password']")

    btn = driver.find_element(By.XPATH, "//button[@type='submit']")

    email_in.send_keys(email)

    pass_in.send_keys(user_pass)

    btn.click()

    element = WebDriverWait(driver, 100).until(EC.presence_of_element_located, (By.ID, "advanced"))

    book_section = driver.find_element(By.ID, "advanced")

    book_section.click()

    element = WebDriverWait(driver, 100).until(EC.presence_of_element_located, (By.XPATH, "//a[text()[contains('SPA')]]"))

    spanish = driver.find_element(By.XPATH, "//a[contains(text(),'SPA')]")

    spanish.click()


    try:

        WebDriverWait(driver, 5).until(EC.presence_of_element_located, (By.TAG_NAME, "tr"))

        sleep(2)

        rows = driver.find_elements(By.TAG_NAME, 'tr')
        print('')
        print(len(rows))
        print('')
        for i in range(len(rows)):

            if opcion == 'vdvv' or opcion == 'vtt' or opcion == 'vfue':

                print(opcion)

                try:
                        
                    properties = driver.find_elements(By.TAG_NAME, 'tr')[i].find_elements(By.TAG_NAME, 'td')

                except Exception:

                    print('Not actual field')
                    continue

                if properties[0].text == options_list[opcion][0] and properties[2].text == options_list[opcion][1]:

                    book_btn = properties[3].find_element(By.PARTIAL_LINK_TEXT, '/Services/Booking')

                    book_btn.click()

                    break
                    
                else:
                    continue

            else:

                print(opcion)
            
                properties = driver.find_elements(By.TAG_NAME, 'tr')[i].find_elements(By.TAG_NAME, 'td')

                if len(properties) == 0:

                    print('Not field')

                    continue
                    
                if properties[0].text == options_list[opcion]:

                    book_btn = properties[3].find_element(By.TAG_NAME, 'button')

                    book_btn.click()

                    break

                else:

                    continue

        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located, (By.XPATH, "//input[@type='checkbox']"))

        check = driver.find_element(By.XPATH, "//input[@type='checkbox']")

        continue_btn = driver.find_element(By.ID, 'btnAvanti')

        check.click()

        continue_btn.click()

        WebDriverWait(driver, 5).until(EC.alert_is_present())
            
        driver.switch_to.alert.accept()

        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located, (By.CLASS_NAME, 'day.availableDay'))

        book = driver.find_element(By.ID, "btnPrenota")

        sleep(1)

        dates = driver.find_elements(By.CLASS_NAME, 'day.availableDay')

        selected_date = driver.find_element(By.CLASS_NAME, 'day.active')

        selected_day = selected_date.text

        print(selected_day)

        available_dates = []

        month = driver.find_element(By.XPATH, "//th[@title='Select Month']").text.replace(' 2022', '')

        for date in dates:
                
            date_day = date.text

            final_date = f'{date_day} de {month}, 2022'

            available_dates.append(final_date)

        if selected_date.get_attribute('class') == 'day disabled notAvailableDay active':

            selected_date = dates[0]

            selected_date.click()

        print(f'theres {len(dates)} available dates.')

        app_date = f'{selected_day} de {month}, 2022'

        sleep(2)

        book.click()

        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located, (By.ID, 'idOtp'))

        sleep(1)

        #check the ok_btn change all btn classes to xpaths or something.

        code_input = driver.find_element(By.ID, 'idOtp')

        ok_btn = driver.find_element(By.CLASS_NAME, 'btn.btn-blue')

        code = find_email_code(email, email_pass)

        code_input.send_keys(code)

        ok_btn.click()

        sleep(1)

        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located, (By.CLASS_NAME, 'button.primary'))

        back_btn = driver.find_element(By.CLASS_NAME, 'button.primary')

        back_btn.click()

        WebDriverWait(driver, 35).until(EC.presence_of_element_located, (By.CLASS_NAME,'button.primary'))

        msg = f"""
        El proceso de reclamar un turno para {options_list[opcion][0] if len(options_list[opcion]) == 2 else options_list[opcion]} ha sido terminado satisfactoriamente,
        Este turno quedó agendado para el día {app_date}.
        Otras fechas disponibles son:
        {available_dates}
        """

        send_mail_notification(gmail, google_app_pass, msg)

        print('......................Proceso terminado......................')

        return True

    except Exception:

        print('No hay turno disponible.')

        not_available = driver.find_element(By.CLASS_NAME, 'jconfirm-buttons')

        not_available.click()

        driver.close()

        driver.quit()

        return False


def scheduler():

    while True:

        succes = automate(url, e_mail, itgov_pass, mail_pass, google_app_pass, g_mail, option)

        if succes:

            break

        now = datetime.now()

        hour = now.hour

        minute = now.minute

        time_next_run = None

        if minute >= 30:

            next_run_hour = hour + 1
            next_run_minute = 0

            next_run = datetime(now.year, now.month, now.day, next_run_hour, next_run_minute, 0)

            time_diff = now - next_run

            time_next_run = time_diff.total_seconds()

        elif minute < 30:

            next_run_hour = hour
            next_run_minute = 30

            next_run = datetime(now.year, now.month, now.day, next_run_hour, next_run_minute, 0)

            time_diff = now - next_run

            time_next_run = time_diff.total_seconds()

        sleep(time_next_run)




if __name__ == '__main__':
    
    scheduler()
    