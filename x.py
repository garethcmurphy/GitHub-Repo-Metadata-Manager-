#!/usr/bin/env python3
"""
get-github-repos.py: A Python script to fetch all
repositories for the authenticated user and update
  repositories with missing descriptions or topics
    using OpenAI's GPT-3.
    """

import openai
import requests

# Configuration
GITHUB_TOKEN = "your_github_token_here"
OPENAI_API_KEY = "your_openai_api_key_here"
GITHUB_USERNAME = "your_github_username"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# OpenAI Configuration
openai.api_key = OPENAI_API_KEY


def fetch_repositories():
    """Fetch all repositories for the authenticated user."""
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def check_missing_fields(repos):
    """Check for repositories missing descriptions or topics."""
    missing_fields = []
    for repo in repos:
        if not repo.get("description") or not repo.get("topics"):
            missing_fields.append(repo)
    return missing_fields


def generate_content(prompt):
    """Generate content using OpenAI."""
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
    )
    return response.choices[0].text.strip()


def update_repository(repo, description=None, topics=None):
    """Update the repository with a new description or topics."""
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo['name']}"
    payload = {}
    if description:
        payload["description"] = description
    if topics:
        payload["topics"] = topics
    headers = {**HEADERS, "Accept": "application/vnd.github.mercy-preview+json"}
    response = requests.patch(
        url,
        json=payload,
        headers=headers,
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def main():
    """Main function to fetch repositories and update missing fields."""
    repos = fetch_repositories()
    missing_fields = check_missing_fields(repos)

    if not missing_fields:
        print("All repositories have descriptions and topics!")
        return

    print(f"{len(missing_fields)} repositories are missing descriptions or topics.\n")

    for repo in missing_fields:
        print(f"Processing repository: {repo['name']}")
        description = repo.get("description")
        topics = repo.get("topics")

        if not description:
            prompt = f"""
            Generate a concise GitHub repository description
              for a project named '{repo['name']}'."""
            description = generate_content(prompt)
            print(f"Generated Description: {description}")

        if not topics:
            prompt = f"""
            Suggest 3-5 tags for a GitHub repository
              named '{repo['name']}' for better discoverability."""
            topics_text = generate_content(prompt)
            topics = [tag.strip() for tag in topics_text.split(",") if tag.strip()]
            print(f"Generated Topics: {topics}")

        # Update the repository
        print("Updating repository...")
        update_repository(repo, description, topics)
        print(f"Repository '{repo['name']}' updated successfully.\n")


if __name__ == "__main__":
    main()
