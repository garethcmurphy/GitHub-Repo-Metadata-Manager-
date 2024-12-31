#!/usr/bin/env python3
"""class to fetch text using the
Google Generative AI API."""

import os
import sys

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError


class GeminiTextFetcher:
    """class to fetch text using the
    Google Generative AI API."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.model = None

    def configure_api(self):
        """configure the API key for the model."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash-002")
        except GoogleAPIError as e:
            print(f"Google API error occurred: {e}")
            return False
        return True

    def generate_text(self, prompt):
        """generate text using the model."""
        if not self.model:
            print("Model is not configured properly.")
            return None

        try:
            response = self.model.generate_content(prompt)
            # print(response)
            return response
        except GoogleAPIError as e:
            print(f"Google API error occurred: {e}")
        return None

    def save_response_to_markdown(self, response, file_path):
        """save the response to a markdown file."""
        response_dict = response.to_dict()
        print("response _dict ", response_dict)
        candidates = response_dict["candidates"]  # Access the 'candidates' attribute
        for candidate in candidates:
            content = candidate["content"]  # Access 'content'
            parts = content["parts"]  # Access 'parts', assumed to be a list

            for part in parts:
                text = part["text"]  # Access the 'text' attribute within 'parts'
                print("Text Part:", text)
                with open(
                    file_path,
                    "w",
                    encoding="ascii",
                ) as file:
                    file.write(text + "\n")
        print(f"Response saved to {file_path}")


def main():
    """Main function to fetch text using the Google Generative AI API."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("API key not found in environment variables.")
        sys.exit(1)

    fetcher = GeminiTextFetcher(api_key=api_key)
    if fetcher.configure_api():
        prompt = """
        can you make a list of topics and a description for this repo v20-kafka
        """
        response = fetcher.generate_text(prompt)
        if response:
            fetcher.save_response_to_markdown(response, "response.md")


if __name__ == "__main__":
    main()
