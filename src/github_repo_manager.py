#!/usr/bin/env python3
"""
get-github-repos.py: A Python script to fetch all
repositories for the authenticated user and update
repositories with missing descriptions or topics
using OpenAI's GPT-3.
"""

import os
import sys

import requests


from gemini_text_fetcher import GeminiTextFetcher

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}



class GitHubRepoManager:
    """A class to manage GitHub repositories."""
    def __init__(self, github_username, headers):
        self.github_username = github_username
        self.headers = headers
        self.gen = GeminiTextFetcher(GOOGLE_API_KEY)
        self.gen.configure_api()

    def fetch_repositories(self):
        """Fetch all repositories for the authenticated user."""
        url = f"https://api.github.com/users/{self.github_username}/repos"
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching repositories: {e}")
            return []

    def check_missing_fields(self, repos):
        """Check for repositories missing descriptions or topics."""
        missing_fields = []
        for repo in repos:
            if not repo.get("description") or not repo.get("topics"):
                missing_fields.append(repo)
        return missing_fields

    def generate_content(self, prompt):
        """Generate content using OpenAI."""
        try:
            response =self.gen.generate_text(prompt)
            return response
        except Exception as e:
            print(f"Error generating content: {e}")
            sys.exit(1)



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
        if not repos:
            return

        missing_fields = self.check_missing_fields(repos)
        if not missing_fields:
            print("All repositories have descriptions and topics!")
            return

        print(
            f"{len(missing_fields)} repositories are missing descriptions or topics.\n"
        )

        for repo in missing_fields:
            print(f"Processing repository: {repo['name']}")
            description = repo.get("description")
            topics = repo.get("topics")

            if not description:
                prompt = f"""
                Generate a concise GitHub repository description
                 for a project named '{repo['name']}'."""
                description = self.generate_content(prompt)
                print(f"Generated Description: {description}")

            if not topics:
                prompt = f"""
                Suggest 3-5 tags for a GitHub repository
                 named '{repo['name']}' for better discoverability.
                 """
                # topics_text = self.generate_content(prompt)
                # topics = [tag.strip() for tag in topics_text.split(",") if tag.strip()]
                # print(f"Generated Topics: {topics}")

            # Update the repository
            print("Updating repository...")
            # updated_repo = self.update_repository(repo, description, topics)
            # if updated_repo:
            #    print(f"Repository '{repo['name']}' updated successfully.\n")


# Usage
if __name__ == "__main__":
    manager = GitHubRepoManager(GITHUB_USERNAME, HEADERS)
    manager.process_repositories()
