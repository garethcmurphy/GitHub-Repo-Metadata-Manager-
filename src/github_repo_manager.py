#!/usr/bin/env python3
"""
get-github-repos.py: A Python script to fetch all
repositories for the authenticated user and update
repositories with missing descriptions or topics
using Google Gemini API.
"""

import os
import sys

import pandas as pd
import requests
from dotenv import load_dotenv

from gemini_text_fetcher import GeminiTextFetcher

# Load environment variables from .env file
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


class GitHubRepoManager:
    """A class to manage GitHub repositories."""

    def __init__(self, github_username, headers):
        # try get fgithub token from env except exit
        if not GITHUB_TOKEN:
            print("Error: GITHUB_TOKEN is missing.")
            sys.exit(1)

        self.github_username = github_username
        self.headers = headers
        self.gen = GeminiTextFetcher(GOOGLE_API_KEY)
        self.gen.configure_api()

    def fetch_repositories(self):
        """Fetch all repositories for the authenticated user."""
        url = f"https://api.github.com/users/{self.github_username}/repos"
        params = {"per_page": 100}
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=5,
            )
            params["page"] = 2
            response2 = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=5,
            )
            print(response2.json())
            response.raise_for_status()
            # merge these two responses
            response.json().extend(response2.json())
            df = pd.DataFrame(response.json())
            df2 = pd.DataFrame(response2.json())
            df = pd.concat([df, df2])
            df.to_excel("repos.xlsx")
            df.to_csv("repos.csv")
            return df
            # get next page

        except requests.RequestException as e:
            print(f"Error fetching repositories: {e}")
            return []

    def generate_content(self, prompt):
        """Generate content using LLM."""
        response = self.gen.generate_text(prompt)
        return response

    def update_repository(self, repo, description=None, topics=None):
        """Update the repository with a new description or topics."""
        url = f"https://api.github.com/repos/{self.github_username}/{repo['name']}"
        payload = {}
        if description:
            payload["description"] = description
        if topics:
            payload["topics"] = topics
        headers = {
            **self.headers,
            "Accept": "application/vnd.github.mercy-preview+json",
        }
        try:
            response = requests.patch(url, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error updating repository: {e}")
            return None

    def process_repositories(self):
        """Fetch repositories and update missing fields."""
        repos = self.fetch_repositories()

        # check if topic column is has any missing values
        if repos["topics"].isnull().sum() > 0:
            repos["topics"] = repos["topics"].fillna("")
        # find most common topics
        topics = repos["topics"].str.split(",").explode().value_counts()
        print(topics)



# Usage
if __name__ == "__main__":
    manager = GitHubRepoManager(GITHUB_USERNAME, HEADERS)
    manager.process_repositories()
