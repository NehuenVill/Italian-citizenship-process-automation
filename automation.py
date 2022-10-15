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
import json

url = 'https://prenotami.esteri.it/Home'

e_mail = ''
google_app_pass = ''
itgov_pass = ''
mail_pass = ''
option = ''
embassy = ''
g_mail = ''

with open('user_info.json') as f:

    info = json.load(f)

    e_mail = info['email']
    google_app_pass = info['goggle app']
    itgov_pass = info['Italian government website password']
    mail_pass = info['email password']
    option = info['option']
    g_mail = info['gmail']
    embassy = info['embassy']

# Adapt options_list to the Montevideo embasy.
# Change all the prints to log the stages of the process better.

options_list = {

    'urm' : {
                'div'  : 'DOCUMENTOS DE IDENTIDAD Y DE VIAJE', 
                'l'    : 'LEGALIZACIONES', 
                'rpec' : 'REGISTRO DE LA POBLACIÓN Y ESTADO CIVIL', 
                'ci' : ['CIUDADANÍA', 'Ciudadanía - reservas a partir del 01/11/2021'],
                'cihma' : ['CIUDADANÍA', 'Ciudadanía para hijos mayores de edad de ciudadanos ya registrados - calendaro desde el 01/11/2021']
            },

    'ba' : {
                'divepas'  : ['DOCUMENTOS DE IDENTIDAD Y DE VIAJE', 'Entrega de pasaportes'],
                'divspas'  : ['DOCUMENTOS DE IDENTIDAD Y DE VIAJE', 'Solicitud de Pasaporte'],
                'rsi' : ['REGISTRO DE LA POBLACIÓN Y ESTADO CIVIL', 'Vice Consulado Honorario en San Isidro'],
                'rtf' : ['REGISTRO DE LA POBLACIÓN Y ESTADO CIVIL', 'Corresponsal Consular en Tres de Febrero'],
                'rz' : ['REGISTRO DE LA POBLACIÓN Y ESTADO CIVIL', 'Corresponsal Consular en Zarate'],
                'rm' : ['REGISTRO DE LA POBLACIÓN Y ESTADO CIVIL', 'Corresponsal Consular en Merlo'],
                'ci' : ['CIUDADANÍA', 'Hijos directos mayores de edad'],
                'cirec' : ['CIUDADANÍA', 'Reconstrucción de Ciudadania'],
                'scn' : ['SERVICIOS CONSULARES', 'Notarial'],
                'sce' : ['SERVICIOS CONSULARES', 'Estudios'],
                'scln' : ['SERVICIOS CONSULARES', 'Legalizaciones para Naturalización'],
                'scrc' : ['SERVICIOS CONSULARES', 'Certificación de traducciones actas del Registro Civil'],
                'scps' : ['SERVICIOS CONSULARES', 'Oficina de Pensiones - Certificado Supervivencia'],
                'scn' : ['SERVICIOS CONSULARES', 'Visas'],

            },
    
    'cor' : {  
                'div'  : 'DOCUMENTOS DE IDENTIDAD Y DE VIAJE', 
                'l'    : 'LEGALIZACIONES', 
                'sc'   : 'SERVICIOS CONSULARES',
                'ci' : 'CIUDADANÍA'
            },

    'ros' : {
                'divp'  : ['DOCUMENTOS DE IDENTIDAD Y DE VIAJE', 'Pasaportes'],
                'divpos'  : ['DOCUMENTOS DE IDENTIDAD Y DE VIAJE', 'PASSAPORTI POSADAS - Emisión de pasaportes'],
                'divcon'  : ['DOCUMENTOS DE IDENTIDAD Y DE VIAJE', 'CONCORDIA - Emisión de pasaportes'],
                'ldoc'    : ['LEGALIZACIONES', 'Legalización de documentación para trámites de ciudadanía italiana a presentar en Italia'], 
                'ldv'    : ['LEGALIZACIONES', 'Declaración de valor'], 
                'sc'   : 'SERVICIOS CONSULARES',
                'ci' : 'CIUDADANÍA',
                'cf' : 'CÓDIGO FISCAL',
                'rpec' : 'REGISTRO DE LA POBLACIÓN Y ESTADO CIVIL',     
            }

}

options_list2 = {
                'sc'   : 'SERVICIOS CONSULARES',
                'div'  : 'DOCUMENTOS DE IDENTIDAD Y DE VIAJE',
                'vfue' : ['VISADOS', 'Solamente familiares de ciudadanos UE'],
                'l'    : 'LEGALIZACIONES',
                'vtt'  : ['VISADOS', 'Todas tipologias de Visados'],
                'rpec' : 'REGISTRO DE LA POBLACIÓN Y ESTADO CIVIL',
                'vdvv' : ['VISADOS', 'Declaraciones de Valor y Visados de Estudio - Estudiantes con preinscripciòn Universitaly']}
    

def find_option_chosen(em:str, op, driver, rows):

    for i in range(len(rows)):

        if len(options_list[em][op]) == 2:

            print(f'La opción elegida es: {options_list[em][op][0]}')
    
            properties = driver.find_elements(By.TAG_NAME, 'tr')[i].find_elements(By.TAG_NAME, 'td')

            if len(properties) == 0:

                continue

            if properties[0].text == options_list[em][op][0] and properties[2].text == options_list[em][op][1]:

                book_btn = properties[3].find_element(By.TAG_NAME, 'button')

                book_btn.click()

                return True

                break
                    
            else:
                continue

        else:

            print(f'La opción elegida es: {options_list[em][op]}')
       
            properties = driver.find_elements(By.TAG_NAME, 'tr')[i].find_elements(By.TAG_NAME, 'td')

            if len(properties) == 0:

                continue
                    
            if properties[0].text == options_list[em][op]:

                book_btn = properties[3].find_element(By.TAG_NAME, 'button')

                book_btn.click()

                return True

                break

            else:

                continue


def send_mail_notification(email, passw, msg):

    port = 465

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        
        server.login(email, passw)
        
        server.sendmail(email, email, msg, rcpt_options=['SMTPUTF8'])


def find_email_code(mail, password):

    imap_server = "outlook.office365.com"
    code = ''

    while code == '':

        sleep(5)

        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(mail, password)

        print('Buscando el código...')

        imap.select("INBOX")
        
        _, messages = imap.search(None, "ALL")

        email_nums = messages[0].split()

        last_mail_num = email_nums[len(email_nums)-1]

        _, data = imap.fetch(last_mail_num, '(RFC822)')
            
        msg = email.message_from_bytes(data[0][1])

        subject = msg.get('Subject')

        body = str(msg.get_payload(None, True))

        if 'OTP Code:' in body:

            code = body.replace("""b'<meta http-equiv="Content-Type" content="text/html; charset=utf-8">OTP Code:""", '').replace("'", '')
        
        imap.close()  
        imap.logout()
    
    print(f'El código es: {code}')

    return code



def automate(url, email, user_pass, email_pass, google_app_pass, gmail, opcion, embassy):

    print('......................Comenzando proceso......................')

    chrome_options = Options()

    #chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located, (By.ID, 'login-email'))

    email_in = driver.find_element(By.XPATH, "//input[@type='email']")

    pass_in = driver.find_element(By.XPATH, "//input[@type='password']")

    btn = driver.find_element(By.XPATH, "//button[@type='submit']")

    email_in.send_keys(email)

    pass_in.send_keys(user_pass)

    btn.click()

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located, (By.ID, "advanced"))

    book_section = driver.find_element(By.ID, "advanced")

    book_section.click()

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located, (By.XPATH, "//a[text()[contains('SPA')]]"))

    spanish = driver.find_element(By.XPATH, "//a[contains(text(),'SPA')]")

    spanish.click()

    try:

        WebDriverWait(driver, 5).until(EC.presence_of_element_located, (By.TAG_NAME, "tr"))

        sleep(2)

        rows = driver.find_elements(By.TAG_NAME, 'tr')
    
        if embassy == 'bs':

            if find_option_chosen(embassy, opcion, driver, rows):

                pass

            else:

                next_btn = driver.find_element(By.ID, 'dataTableServices_next')

                next_btn.click()

                sleep(1)

                WebDriverWait(driver, 5).until(EC.presence_of_element_located, (By.TAG_NAME, "tr"))

                rows = driver.find_elements(By.TAG_NAME, 'tr')

                find_option_chosen(embassy, opcion, driver, rows)

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

        try:

            selected_date = driver.find_element(By.CLASS_NAME, 'day.active')

        except Exception:

            selected_date = dates[0]

            selected_date.click()

        selected_day = selected_date.text

        print(f'El día seleccionado es: {selected_day}')

        available_dates = []

        month = driver.find_element(By.XPATH, "//th[@title='Select Month']").text.replace(' 2022', '')

        for date in dates:
                
            date_day = date.text

            final_date = f'{date_day} de {month}, 2022'

            available_dates.append(final_date)

        if selected_date.get_attribute('class') == 'day disabled notAvailableDay active':

            selected_date = dates[0]

            selected_date.click()

        print(f'Hay {len(dates)} fechas disponibles.')

        app_date = f'{selected_day} de {month}, 2022'

        sleep(2)

        book.click()

        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located, (By.ID, 'idOtp'))

        sleep(1)

        #check the ok_btn change all btn classes to xpaths or something.

        code_input = driver.find_element(By.ID, 'idOtp')

        ok_btn = driver.find_element(By.XPATH, "//button[text()='ok']")

        code = find_email_code(email, email_pass)

        code_input.send_keys(code)

        ok_btn.click()

        sleep(3)

        msg = f"""
        El proceso de reclamar un turno para {options_list[opcion][0] if len(options_list[opcion]) == 2 else options_list[opcion]} ha sido terminado satisfactoriamente,
        Este turno quedo agendado para el dia {app_date}.
        Otras fechas disponibles son:
        {available_dates}
        """

        msg = msg.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')

        print(msg)

        send_mail_notification(gmail, google_app_pass, msg)

        print('......................Proceso terminado......................')

        driver.close()

        driver.quit()

        return True

    except Exception as e:

        print(f'erorr is: {e}')

        print('No se pudo concretar un turno / no hay turno disponible.')

        driver.close()

        driver.quit()

        return False


def scheduler():

    while True:

        succes = automate(url, e_mail, itgov_pass, mail_pass, google_app_pass, g_mail, option, embassy)

        if succes:

            break

        now = datetime.now()

        hour = now.hour

        minute = now.minute

        time_next_run = None

        if minute >= 30:

            next_run_hour = hour + 1
            next_run_minute = 0
            day = now.day

            if next_run_hour == 24:

                next_run_hour = 0
                day += 1

            next_run = datetime(now.year, now.month, day, next_run_hour, next_run_minute, 0)

            print(f'El programa volverá a ejecutarse a las {next_run.hour}')

            time_diff = next_run - now

            time_next_run = time_diff.total_seconds()

        elif minute < 30:

            next_run_hour = hour
            next_run_minute = 30

            next_run = datetime(now.year, now.month, now.day, next_run_hour, next_run_minute, 0)

            print(f'El programa volverá a ejecutarse a las {next_run.hour}:{next_run.minute}')
            
            time_diff = next_run - now

            time_next_run = time_diff.total_seconds()

        sleep(time_next_run)




if __name__ == '__main__':
    
   scheduler()
