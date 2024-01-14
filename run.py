from flask import Flask, request, render_template
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

app = Flask(__name__)

# This will get the current directory where the script is located
current_directory = os.path.dirname(os.path.abspath(__file__))
geckodriver_path = os.path.join(current_directory, 'geckodriver')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    job_title = request.form['job_title']
    location = request.form['location']
    results = perform_search(job_title, location)
    save_to_excel(results)
    return 'Search Complete! Check the Excel file.'


def perform_search(job_title, location, max_results=100):
    print(f"Starting search for: {job_title} in {location}")  # Debugging print
    search_query = f"{job_title} site:linkedin.com/in/ AND {location}"
    

    options = Options()
    # options.add_argument('--headless')  # Uncomment for headless mode
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)

    print("Opening Google...")  # Debugging print
    driver.get("https://www.google.com")
    search_box = driver.find_element(By.NAME, 'q')
    print("Entering search query...")  # Debugging print
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)  # Adjust as needed


    names_links = []
    i=0;

    try:
        for _ in range(max_results // 10):  # Assuming 10 results load per scroll
            print(f"Scrolling down, iteration {i+1}...")  # Debugging print
            i+=1
            # Scroll down to load more results
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Adjust as needed
            
            print("Extracting results...")  # Debugging print

            # Extract results
            results = driver.find_elements(By.XPATH, "//a[@jsname='UWckNb'][contains(@href, 'linkedin.com')]")
            for result in results:
                name = result.find_element(By.XPATH, "./h3").text
                link = result.get_attribute('href')
                if (name, link) not in names_links:
                    names_links.append((name, link))
                    print(f"Found: {name}, {link}")  # Debugging print


            # Check if reached required number of results
            if len(names_links) >= max_results:
                print("Reached max number of results.")  # Debugging print
                break
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Save results to Excel
        print("Saving results to Excel...")  # Debugging print
        save_to_excel(names_links)
        driver.quit()
        print("Driver closed and results saved.")  # Debugging print

    return names_links

def save_to_excel(data):
    df = pd.DataFrame(data, columns=['Name', 'LinkedIn URL'])
    df.to_excel('candidates.xlsx', index=False)

if __name__ == '__main__':
    app.run(debug=True)
