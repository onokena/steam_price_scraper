import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import psycopg2
from psycopg2 import sql

def scrape_case_prices(market_url, max_pages=4):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    case_prices = {}

    page_number = 1
    while page_number <= max_pages:
        current_url = f"{market_url}#p{page_number}_default_desc"
        response = requests.get(current_url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract case names and prices
            item_containers = soup.find_all('div', {'class': 'market_listing_row'})
            for item_container in item_containers:
                case_name_tag = item_container.find('span', {'class': 'market_listing_item_name'})
                case_price_tag = item_container.find('span', {'class': 'price_value'})

                if case_name_tag and case_price_tag:
                    if case_price_tag.text.strip() != "starting_at:":
                        try:
                            # Assuming price is a comma-separated value:
                            case_price = float(case_price_tag.text.strip().replace(',', ''))
                            case_prices[case_name] = case_price
                        except ValueError:
                            print(f"Invalid price format for {case_name}")
            else:
                print(f"Case {case_name} has no price listed.")

            page_number += 1
            # Introduce a delay between requests to avoid rate limiting
            time.sleep(3)
        elif response.status_code == 429:
            print(f"Rate limited. Waiting for 60 seconds.")
            time.sleep(60)
        else:
            print(f"Failed to fetch data from page {page_number}. Status code: {response.status_code}")
            return None

    return case_prices

def print_case_prices(case_prices):
    for case_name, price in case_prices.items():
        print(f"{case_name} - {price}")
        
def save_prices_to_postgres(case_prices, connection_details):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        connection = psycopg2.connect(**connection_details)
        cursor = connection.cursor()

        for case_name, case_price in case_prices.items():
            insert_query = sql.SQL("INSERT INTO case_prices (case_name, case_price, latest_date_checked) VALUES (%s, %s, %s)")
            cursor.execute(insert_query, (case_name, case_price, timestamp))

        connection.commit()
        print("Data successfully inserted into PostgreSQL.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    market_url = 'https://steamcommunity.com/market/search?category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_Type%5B%5D=tag_CSGO_Type_WeaponCase&appid=730&q=Case'

    # Replace the connection details with your PostgreSQL database information
    postgres_connection_details = {
        'host': 'localhost',
        'database': 'steamscraper',
        'user': 'postgres',
        'password': 'test123',
        'port': '5432'
    }

    while True:
        case_prices = scrape_case_prices(market_url, max_pages=4)

        if case_prices:
            for case_name, price in case_prices.items():
                print(f"{case_name} - {price}")

            save_prices_to_postgres(case_prices, postgres_connection_details)
        else:
            print("Failed to fetch case prices.")

        # Scrape every 24 hours (86400 seconds)
        time.sleep(86400)
