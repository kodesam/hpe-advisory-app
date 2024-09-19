import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os
from plyer import notification
import schedule
import time

class HPEAdvisoryChecker:
    def __init__(self, username, password, servers):
        self.username = username
        self.password = password
        self.servers = servers
        self.session = requests.Session()
        self.base_url = 'https://hpewebsite.com'  # Replace with the actual HPE website URL
        self.login_url = self.base_url + '/login'
        self.advisory_url = self.base_url + '/advisories'
        self.local_advisories_file = 'advisories.json'

    def login(self):
        """Simulates login to the HPE website using session and credentials."""
        payload = {
            'username': self.username,
            'password': self.password
        }
        # Simulate login process
        response = self.session.post(self.login_url, data=payload)
        if response.status_code == 200:
            st.write("Login successful")
        else:
            st.write(f"Login failed: {response.status_code}")

    def fetch_advisories(self):
        """Fetches advisory notifications and returns them."""
        response = self.session.get(self.advisory_url)
        if response.status_code != 200:
            st.write(f"Failed to retrieve advisories: {response.status_code}")
            return []

        # Parse the advisories from the response content
        soup = BeautifulSoup(response.content, 'html.parser')
        advisories = []

        # Assuming the advisories are in some structured format like a table or list:
        advisory_list = soup.find_all('div', class_='advisory')
        for advisory in advisory_list:
            title = advisory.find('h3').text
            details = advisory.find('p').text
            link = advisory.find('a')['href']
            advisories.append({
                'title': title,
                'details': details,
                'link': link
            })
        return advisories

    def filter_advisories(self, advisories):
        """Filters advisories based on selected servers."""
        filtered = []
        for advisory in advisories:
            for server in self.servers:
                if server.lower() in advisory['details'].lower():
                    filtered.append(advisory)
        return filtered

    def check_new_advisories(self):
        """Compares current advisories with stored ones and sends notifications if new advisories are found."""
        new_advisories = self.fetch_advisories()
        filtered_advisories = self.filter_advisories(new_advisories)

        # Load previously stored advisories
        if os.path.exists(self.local_advisories_file):
            with open(self.local_advisories_file, 'r') as file:
                old_advisories = json.load(file)
        else:
            old_advisories = []

        # Find new advisories
        for advisory in filtered_advisories:
            if advisory not in old_advisories:
                self.send_notification(advisory)

        # Save the latest advisories
        with open(self.local_advisories_file, 'w') as file:
            json.dump(filtered_advisories, file)

    def send_notification(self, advisory):
        """Sends a desktop notification about a new advisory."""
        st.write(f"New Advisory: {advisory['title']}")
        notification.notify(
            title=f"New Advisory for HPE Server",
            message=f"{advisory['title']}: {advisory['details']}",
            app_name="HPE Advisory Checker"
        )

# Streamlit App

st.title("HPE Advisory Checker")

# Input fields for username, password, and server list
username = st.text_input("Enter your HPE username")
password = st.text_input("Enter your HPE password", type="password")
servers = st.text_area("Enter the servers to track (comma-separated)")

# Button to start the advisory checking process
if st.button("Check Advisories"):
    if not username or not password or not servers:
        st.write("Please enter all required fields (username, password, servers).")
    else:
        # Convert server input into a list
        server_list = [s.strip() for s in servers.split(',') if s.strip()]
        
        # Initialize the HPEAdvisoryChecker with user input
        hpe_checker = HPEAdvisoryChecker(username, password, server_list)

        # Log in to the HPE website
        hpe_checker.login()

        # Check for new advisories
        hpe_checker.check_new_advisories()
