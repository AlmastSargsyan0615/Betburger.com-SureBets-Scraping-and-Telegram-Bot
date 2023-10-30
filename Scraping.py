import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
import string
import json
import sqlite3
import os
from datetime import datetime, timedelta
import re



# Initialize the webdriver
driver = webdriver.Chrome()
driver.maximize_window()
# Navigate to the login page
driver.get('https://www.betburger.com/users/sign_in')

# Enter your email/username and password

email_field =driver.find_element(By.NAME, 'betburger_user[email]')
email = 'perronemauro97@gmail.com'
for char in email:
    email_field.send_keys(char)
    time.sleep(0.1)

password_field = driver.find_element(By.NAME,'betburger_user[password]')
password = 'tQV6_ZGh_GvRUa*='

for char in password:
    password_field.send_keys(char)
    time.sleep(0.1)

# Click on the login button
login_button = driver.find_element(By.CSS_SELECTOR,'.submit')
login_button.click()

# Wait for the page to load
time.sleep(60)

driver.get('https://www.betburger.com/arbs')
driver.implicitly_wait(60)

# zoom_level = 0.4
# driver.execute_script(f"document.body.style.zoom = '{zoom_level}';")

def sanitize_table_name(name):
    # Remove special characters except underscores
    cleaned_name = re.sub(r'[^\w]+', '_', name)

    # Remove leading numbers
    cleaned_name = re.sub(r'^\d+', '', cleaned_name)

    # Truncate to a maximum length of 255 characters
    cleaned_name = cleaned_name[:255]

    return cleaned_name

def create_database():
    db_name = "realtime.db"
    if not os.path.exists(db_name):
        conn = sqlite3.connect(db_name)
        conn.close()
        print("Database 'realtime' created successfully.")
    else:
        print("Database 'realtime' already exists.")


def create_table(table_name):
    db_name = "realtime.db"
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Create a table with columns
    c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bookmarker_name TEXT,
                    percent TEXT,
                    updated_time TEXT,
                    sport_name TEXT,
                    date TEXT,
                    match TEXT,
                    league TEXT,
                    market TEXT,
                    coefficient TEXT
                )''')

    conn.commit()
    conn.close()
    print(f"Table '{table_name}' created successfully.")


def check_percent_exists(table_name, percent):
    db_name = "realtime.db"
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Check if a record with the same percent exists in the table
    c.execute(f"SELECT percent FROM {table_name} WHERE percent=?", (percent,))
    existing_percent = c.fetchone()

    conn.close()

    # Return True if a record with the same percent exists, False otherwise
    return existing_percent is not None

def remove_all_records(table_name):
    db_name = "realtime.db"
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute(f"DELETE FROM {table_name}")

    conn.commit()
    conn.close()

    print(f"All records have been removed from the table '{table_name}'")

def insert_record(table_name, bookmarker_name, percent, updated_time, sport_name, date, match, league, market, coefficient):
    db_name = "realtime.db"
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute(f'''INSERT INTO {table_name} (bookmarker_name, percent, updated_time, sport_name, date, match, league, market, coefficient)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (bookmarker_name, percent, updated_time, sport_name, date, match, league, market, coefficient))

    conn.commit()
    conn.close()

def get_exchange_rate():
        base_currency = 'EUR'
        target_currency = 'RON'
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url)
        data = response.json()
        exchange_rate = data['rates'][target_currency]
        return exchange_rate
def delete_tables_if_exceed_limit(database_path, table_limit):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)

    # Create a cursor object to interact with the database
    cur = conn.cursor()

    # Retrieve the list of table names
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = cur.fetchall()

    # Check the number of table names
    if len(table_names) > table_limit:
        # Iterate over each table name and execute the SQL statement to delete the table
        for table_name in table_names:
            cur.execute(f"DROP TABLE IF EXISTS {table_name[0]}")

        # Commit the changes
        conn.commit()
        print(f"All tables deleted. Total tables: {len(table_names)}")

    # Close the cursor and connection
    cur.close()
    conn.close()

create_database()

while True:

    target_timestamp = 1686804725
    current_timestamp = int(time.time())  # Get the current Unix timestamp

    delete_tables_if_exceed_limit('realtime.db', 500)

    if current_timestamp >= target_timestamp:
        # Perform the desired action when the target timestamp is reached
        print("Target timestamp reached. Exiting the loop.")
        break

    #initializing  scroll bar
    number_list = len(driver.find_elements(By.CSS_SELECTOR, '.arbs-list li'))
    time.sleep(0.1)
    print(f'----------Number of Data :{number_list}----------')

    li_all = driver.find_elements(By.CSS_SELECTOR, '.arbs-list >li')
    time.sleep(0.1)
    
    for i,li in enumerate(li_all, start=1):
        if li:
            try:
                percent = li.find_element(By.CSS_SELECTOR, "span.percent")
                sport_name = li.find_element(By.CSS_SELECTOR, "span.sport-name")
                updated_time = li.find_element(By.CSS_SELECTOR, "span.updated-at")
                bookmarker_names = li.find_elements(By.CSS_SELECTOR, ".bookmaker-name .text-ellipsis")
                dates = li.find_elements(By.CSS_SELECTOR, ".date")
                matches = li.find_elements(By.CSS_SELECTOR, ".name a.text-ellipsis")
                leagues = li.find_elements(By.CSS_SELECTOR, ".league")
                markets = li.find_elements(By.CSS_SELECTOR, ".market a span")
                coefficients = li.find_elements(By.CSS_SELECTOR, "a.coefficient-link") 
                try:
                    percent_text = (''.join((percent.get_attribute("textContent")).splitlines())).replace(' ', '')
                except:
                    li_all = driver.find_elements(By.CSS_SELECTOR, '.arbs-list li')
                    percent_text = (''.join((percent.get_attribute("textContent")).splitlines())).replace(' ', '')
                    print("A")
                try:
                    updated_time_text = (''.join((updated_time.get_attribute("textContent")).splitlines())).replace(' ', '')
                except:
                    li_all = driver.find_elements(By.CSS_SELECTOR, '.arbs-list li')
                    updated_time_text = (''.join((updated_time.get_attribute("textContent")).splitlines())).replace(' ', '')
                    print("B")

                sport_name_text = (''.join((sport_name.get_attribute("textContent")).splitlines())).replace(' ', '')

                print(f'{i})) {percent_text} {sport_name_text} {updated_time_text}')
                # Generate a unique table name
                table_name = sport_name_text

                n = 0
                for bookmarker_name in bookmarker_names:
                    bookmarker_name_text = (''.join((bookmarker_name.get_attribute("textContent")).splitlines())).replace(' ', '') 
                    date = dates[n]
                    date_text = (''.join((date.get_attribute("textContent")).splitlines())).replace(' ', '')
                    match = matches[n]
                    match_text = (''.join((match.get_attribute("textContent") ).splitlines())).replace(' ', '')
                    league = leagues[n]
                    league_text = (''.join((league.get_attribute("textContent")).splitlines())).replace(' ', '')
                    market = markets[n]
                    market_text = (''.join((market.get_attribute("textContent")).splitlines())).replace(' ', '')
                    try:
                        coefficient = coefficients[n]
                        coefficient_text = (''.join((coefficient.get_attribute("textContent")).splitlines())).replace(' ', '')
                    except:
                        li_all = driver.find_elements(By.CSS_SELECTOR, '.arbs-list li')
                        coefficient = coefficients[n]
                        coefficient_text = (''.join((coefficient.get_attribute("textContent")).splitlines())).replace(' ', '')
                        print("C")
                    # table_name = table_name + bookmarker_name_text + market_text
                    table_name = table_name + bookmarker_name_text + match_text

                    date_text_forName = date_text
                    n = n + 1
                    print(f'    {n}) {bookmarker_name_text} | {date_text} | {match_text} | {league_text} | {market_text} | {coefficient_text}')
                table_name = table_name + date_text_forName

                print(table_name)
                table_name = sanitize_table_name(table_name)
                print(table_name)
                create_table(table_name)
                if check_percent_exists(table_name, percent_text):
                    print("Record with the given percent value exists.")
                    print(percent_text)
                else:
   
                    # 
                    bot_data ={}
                    percent_data, sport_name_data, updated_data, bookmarker_data, date_data, match_data, league_data, market_data, coefficient_data = ([] for i in range(9))
                    percent_data.append(percent_text)
                    sport_name_data.append(sport_name_text)
                    updated_data.append(updated_time_text)
                    print(percent_text) 
                    remove_all_records(table_name)
                    print(percent_text)
                    n = 0
                    for bookmarker_name in bookmarker_names:
                        bookmarker_name_text = (''.join((bookmarker_name.get_attribute("textContent")).splitlines())).replace(' ', '') 
                        bookmarker_name_text1 = (''.join((bookmarker_name.get_attribute("textContent")).splitlines())).replace('   ', '')
                        date = dates[n]
                        date_text = (''.join((date.get_attribute("textContent")).splitlines())).replace(' ', '')
                        date_text1 = (''.join((date.get_attribute("textContent")).splitlines())).replace('   ', '')
                        match = matches[n]
                        match_text = (''.join((match.get_attribute("textContent") ).splitlines())).replace(' ', '')
                        match_text1 = (''.join((match.get_attribute("textContent") ).splitlines())).replace('   ', '')
                        league = leagues[n]
                        league_text = (''.join((league.get_attribute("textContent")).splitlines())).replace(' ', '')
                        league_text1 = (''.join((league.get_attribute("textContent")).splitlines())).replace('   ', '')
                        market = markets[n]
                        market_text = (''.join((market.get_attribute("textContent")).splitlines())).replace(' ', '')
                        market_text1 = (''.join((market.get_attribute("textContent")).splitlines())).replace('   ', '')
                        try:
                            coefficient = coefficients[n]
                            coefficient_text = (''.join((coefficient.get_attribute("textContent")).splitlines())).replace(' ', '')
                            coefficient_text1 = (''.join((coefficient.get_attribute("textContent")).splitlines())).replace('   ', '')
                        except:
                            li_all = driver.find_elements(By.CSS_SELECTOR, '.arbs-list li')
                            coefficient = coefficients[n]
                            coefficient_text = (''.join((coefficient.get_attribute("textContent")).splitlines())).replace(' ', '')
                            coefficient_text1 = (''.join((coefficient.get_attribute("textContent")).splitlines())).replace('   ', '')
                            print("D")

                        date_text_forName = date_text
                        try:
                            insert_record(table_name, bookmarker_name_text, percent_text, updated_time_text, sport_name_text, date_text, match_text, league_text, market_text, coefficient_text)
                            time.sleep(0.1)
                            # ////////////////////
                            bookmarker_data.append(bookmarker_name_text)
                            date_data.append(date_text1)
                            match_data.append(match_text1)
                            league_data.append(league_text1)
                            market_data.append(market_text1)
                            coefficient_data.append(coefficient_text1)
                        except:
                            print("===============================>Error")
                
                        n = n + 1
                    if(n != 0):
                        data_list = [percent_data, sport_name_data, updated_data, bookmarker_data, date_data, match_data, league_data, market_data, coefficient_data]
                        keys =['percent','sport_name', 'updated_at','bookmarkers','dates','teams','leagues','markets','coefficients']
                        bot_data =dict(zip(keys,data_list))
                        keys_to_clean = ['percent', 'sport_name', 'updated_at']
                        export_data ={}
                        for key, values in bot_data.items():
                            if key in keys_to_clean:
                                export_data[key] = values[0]
                            else:
                                export_data[key] = values
                    
                                            
                        export_data['rate'] = get_exchange_rate()
                        print(f'=========================>{percent_text}')
                        with open('bot.json', 'w') as file:
                            json.dump(export_data, file, indent=2)
                        with open('bot2.json', 'w') as file:
                            json.dump(export_data, file, indent=2)
            except:
                print("E")
                continue
