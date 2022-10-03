from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
import smtplib, ssl


email = 'nehuenv620@gmail.com'
password = ''
url = 'https://prenotami.esteri.it/Home'

def send_mail_notification(email, passw, msg):

    port = 465

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        
        server.login(email, passw)
       
        server.sendmail(email, email, msg)

    
    

def automate(url, email, password):

    password = input('contraseña para aplicaciones: ')

    driver = webdriver.Chrome()

    driver.get(url)

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located, (By.ID, 'login-email'))

    email_in = driver.find_element(By.XPATH, "//input[@type='email']")

    pass_in = driver.find_element(By.XPATH, "//input[@type='password']")

    btn = driver.find_element(By.XPATH, "//button[@type='submit']")

    email_in.send_keys(email)

    pass_in.send_keys(password)

    btn.click()

    book_btns = driver.find_elements(By.CLASS_NAME, 'button.primary')

    for btn in book_btns:

        btn.click()

        check = WebDriverWait(driver, 5).until(EC.presence_of_element_located, (By.XPATH, "//input[@type='checkbox']"))

        continue_btn = driver.find_element(By.ID, 'btnAvanti')

        check.click()

        continue_btn.click()

        WebDriverWait(driver, 5).until(EC.alert_is_present())
        
        driver.switch_to.alert.accept()

        book = WebDriverWait(driver, 5).until(EC.presence_of_element_located, (By.ID, "btnPrenota"))

        dates = driver.find_elements(By.CLASS_NAME, 'day.availableDay')

        dates[0].click()

        month = driver.find_element(By.XPATH, "//th[@title='Select Month']").text.replace(' 2022', '')

        available_dates = []

        for date in dates:
            
            date_day = date.text

            final_date = f'{date_day} de {month}, 2022'

            available_dates.append(final_date)

        book.click()

        back_btn = WebDriverWait(driver, 5).until(EC.presence_of_element_located, (By.CLASS_NAME, 'button.primary'))

        back_btn.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located, (By.CLASS_NAME,'button.primary'))

        



if __name__ == '__main__':
    
    pass