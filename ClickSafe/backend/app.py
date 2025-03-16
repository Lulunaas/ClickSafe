from flask import Flask, request, jsonify
import joblib
import re
import os
from tld import get_tld
from flask_cors import CORS 
import logging
from dotenv import load_dotenv 

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load your .joblib model
model = joblib.load('./ClickSafe/backend/ClickSafe.joblib')  # Replace with your .joblib model file

# Function to check if the URL contains an IP address
def having_ip_address(url):
    match = re.search(
        '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
        '([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|'  # IPv4
        '((0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\/)'  # IPv4 in hexadecimal
        '(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}', url)  # IPv6
    if match:
        return 1
    else:
        return 0
#abnormal url

from urllib.parse import urlparse

def abnormal_url(url):
    hostname = urlparse(url).hostname
    hostname = str(hostname)
    match = re.search(hostname, url)
    if match:
        # print match.group()
        return 1
    else:
        # print 'No matching pattern found'
        return 0

def count_dot(url):
    count_dot = url.count('.')
    return count_dot

def count_www(url):
    url.count('www')
    return url.count('www')

def count_atrate(url):
     
    return url.count('@')

def no_of_dir(url):
    urldir = urlparse(url).path
    return urldir.count('/')
def no_of_embed(url):
    urldir = urlparse(url).path
    return urldir.count('//')
# Check for shortening services


def shortening_service(url):
    watch = re.search(
        r'bit\.ly|goo\.gl|shorte\.st|go21\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.in|is\.gd|cli\.gs|'
        r'yfrog\.com|migre\.me|ff\.im|tiny\.cc|ur14\.eu|twit\.ac|su\.pr|twurl\.nl|snipur\.com|'
        r'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkitel\.com|snipr\.com|fic\.kr|loopt\.us|'
        r'dolop\.com|short\.de|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|lnkd\.in|db\.tt|'
        r'qr\.ae|adf\.ly|bitly\.com|cur\.lv|tinyurl\.com|ity\.in|q\.gs|po\.st|bc\.vc|twitthis\.com|'
        r'ul\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|prettylinkpro\.com|scrnch\.me|'
        r'filoops\.info|vzturl\.com|qr\.net|lurl\.com|tweez\.me|v\.gd|link\.zip\.net', url)
    return 1 if watch else 0

def count_https(url):
    return url.count('https')

def count_http(url):
    return url.count('http')

def count_per(url):
    return url.count('%')

def count_ques(url):
    return url.count('?')

def count_hyphen(url):
    return url.count('-')

def count_equal(url):
    return url.count('=')

#Length of URL

def url_length(url):
    return len(str(url))

#Hostname Length

def hostname_length(url):
    return len(urlparse(url).netloc)

def suspicious_words(url):
    match = re.search('PayPal|login|signin|bank|account|update|free|lucky|service|bonus|ebayisapi|webscr',
                      url)
    if match:
        return 1
    else:
        return 0

def digit_count(url):
    digits = 0
    for i in url:
        if i.isnumeric():
            digits = digits + 1
    return digits

def letter_count(url):
    letters = 0
    for i in url:
        if i.isalpha():
            letters = letters + 1
    return letters

from urllib.parse import urlparse
from tld import get_tld
import os.path

#First Directory Length
def fd_length(url):
    urlpath= urlparse(url).path
    try:
        return len(urlpath.split('/')[1])
    except:
        return 0

def tld_length(tld):
    try:
        return len(tld)
    except (TypeError, AttributeError):
        return -1




@app.route('/predict', methods=['POST'])
def predict():
    # Get the URL from the request
    try:
        # Get the URL from the request
        data = request.get_json()
        logger.info(f"Received request with data: {data}")

        if not data or 'url' not in data:
            logger.error("Missing URL in request")
            return jsonify({'error': 'Missing URL in request'}), 400

        url = data['url']
        logger.info(f"Processing URL: {url}")

    # Preprocess the URL
        features = preprocess_url(url)

    # Make prediction using the loaded model
        prediction = model.predict([features])
        return jsonify({'prediction': int(prediction[0])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def preprocess_url(url):
    status = []
    
    status.append(having_ip_address(url))
    status.append(abnormal_url(url))
    status.append(count_dot(url))
    status.append(count_www(url))
    status.append(count_atrate(url))
    status.append(no_of_dir(url))
    status.append(no_of_embed(url))
    
    status.append(shortening_service(url))
    status.append(count_https(url))
    status.append(count_http(url))
    
    status.append(count_per(url))
    status.append(count_ques(url))
    status.append(count_hyphen(url))
    status.append(count_equal(url))
    
    status.append(url_length(url))
    status.append(hostname_length(url))
    status.append(suspicious_words(url))
    status.append(digit_count(url))
    status.append(letter_count(url))
    status.append(fd_length(url))
    tld = get_tld(url,fail_silently=True)
      
    status.append(tld_length(tld))
    
    return status

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
