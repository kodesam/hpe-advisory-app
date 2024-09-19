import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os

class HPEAdvisoryChecker:
    def __init__(self, username, password, servers):
        self.username = username
        self.password = password
        self.servers = servers
        self.session = requests.Session()
        self.base_url = 'https://auth.hpe.com'  # Replace with the actual HPE website
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

        # Check if login was successful
        if response.status_code == 200:
            st.write("Login successful")
        else:
            st.write(f"Login failed: {response.status_code}")
            return False
        return True

    def fetch_advisories(self):
        """Fetches advisory notifications and returns them."""
        response = self.session.get(self.advisory_url)

        # Debug: Display the response URL and status
        st.write(f"Advisory Page Status Code: {response.status_code}")
        st.write(f"Advisory Page URL: {response.url}")

        # If the response isn't successful, print error
        if response.status_code != 200:
            st.write(f"Failed to retrieve advisories: {response.status_code}")
            return []

        # Debug: Display the response content to inspect the page
        st.write("Advisory Page Content Preview:")
        st.code(response.text[:1000])  # Show the first 1000 characters of the page content for inspection

        # Parse the advisories from the response content
        soup = BeautifulSoup(response.content, 'html.parser')
        advisories = []

        # Assuming the advisories are in some structured format like a table or list
        advisory_list = soup.find_all('div', class_='advisory')  # Adjust selector based on actual page

        if not advisory_list:
            st.write("No advisories found.")

        for advisory in advisory_list:
            title = advisory.find('h3').text if advisory.find('h3') else 'No Title'
            details = advisory.find('p').text if advisory.find('p') else 'No Details'
            link = advisory.find('a')['href'] if advisory.find('a') else 'No Link'

            advisories.append({
                'title': title,
                'details': details,
                'link': link
            })

        if not advisories:
            st.write("No new advisories available.")
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
        new_advisory_count = 0
        for advisory in filtered_advisories:
            if advisory not in old_advisories:
                new_advisory_count += 1
                st.write(f"New Advisory: {advisory['title']}")
                st.write(f"Details: {advisory['details']}")
                st.write(f"Link: {advisory['link']}")

        if new_advisory_count == 0:
            st.write("No new advisories.")

        # Save the latest advisories
        with open(self.local_advisories_file, 'w') as file:
            json.dump(filtered_advisories, file)

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
        if hpe_checker.login():
            # Check for new advisories
            hpe_checker.check_new_advisories()
