from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
import smtplib, ssl
import imaplib
import email
from email.header import decode_header
from datetime import datetime
from getpass import getpass

e_mail = 'nehuenv620@gmail.com'
url = 'https://prenotami.esteri.it/Home'

options_list = {'sc'   : 'SERVICIOS CONSULARES',
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

def find_email_code(email, password):

    imap_server = "outlook.office365.com"
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(email, password)

    while True:

        status, messages = imap.select("INBOX")

        last_message = int(messages[0])

        res, msg = imap.fetch(last_message, "(RFC822)")

        msg = email.message_from_bytes(msg[0][1])

        subject, encoding = decode_header(msg["Subject"])[0]

        subject = subject.decode(encoding)

        print(f"last mail subject: {subject}")
        print('*'*50,)

        if subject == 'OTP Code':

            message = msg.walk()[0].get_payload(decode = True).decode()

            code = message.replace('OTP Code:', '')

            break

        else:

            sleep(1)

            continue

    return code    

# Note to myself: Replace all the WebDriverWait with driver.find_element, since I've just realized,
# that the first one doesn't return the element after waiting for its existence.

def automate(url, email):

    hour = datetime.now().hour

    print('......................Comenzando proceso......................')

    password = getpass('Contraseña para aplicaciones de google: ')

    user_pass = getpass('Contraseña para la página del gobierno italiano: ')

    email_pass = getpass('Contraseña de tu e-mail: ')

    opcion = getpass('Opcion: ')

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

    # input#idOtp, button.btn.btn-blue (ok button)

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located, (By.ID, 'idOtp'))

    sleep(1)

    code_input = driver.find_element(By.ID, 'idOtp')

    ok_btn = driver.find_element(By.CLASS_NAME, 'btn.btn-blue')

    code = find_email_code(email, email_pass)

    code_input.send_keys(code)

    ok_btn.click()

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

    send_mail_notification(email, password, msg)

    print('......................Proceso terminado......................')




if __name__ == '__main__':
    
    automate(url, e_mail)

