from flask import Flask, request, jsonify
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse

app = Flask(__name__)

def fetch_long_url(short_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    retry_strategy = Retry(
        total=1,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST", "PUT", "DELETE"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        # Perform the request and follow redirects automatically
        response = session.get(short_url, headers=headers, allow_redirects=True)
        response.raise_for_status()  # Raise an error for bad responses
        # If the request succeeds, get the final long URL (after redirect)
        long_url = response.url
        # Parse the URL and get only the path (no query params)
        parsed_url = urlparse(long_url)

        # Assuming the path will have the desired structure
        path_parts = parsed_url.path.split('/')
        
        if len(path_parts) >= 4:
            # Construct the new desired URL by adding "https://vsco.co/" and transforming the path
            transformed_url = f"https://vsco.co/{path_parts[1]}/media/{path_parts[3]}"
            return transformed_url
        else:
            return "Error: Unable to extract valid media ID from the URL"

    except requests.exceptions.RequestException as e:
        # Handle error and print the URL portion from the error message
        error_message = str(e)
        # Extract URL portion from error message
        if "url" in error_message:
            url_part = error_message.split('url: ')[-1].split()[0]  # Extract the URL after 'url:'
            return f"https://vsco.co{url_part}"  # Return the URL with base
        else:
            return "Error: Unable to extract URL"

@app.route('/fetch_long_url', methods=['GET'])
def get_long_url():
    short_url = request.args.get('short_url')
    if short_url:
        transformed_url = fetch_long_url(short_url)
        return jsonify({"transformed_url": transformed_url})
    else:
        return jsonify({"error": "No short URL provided"}), 400

if __name__ == '__main__':
    app.run(debug=True)
