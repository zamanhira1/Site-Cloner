from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse

app = Flask(__name__, template_folder='Templates')

def download_file(url, folder):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                return None
            
            filepath = os.path.join(folder, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filename
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        target_url = request.form.get('url')
        if not target_url.startswith('http'):
            target_url = 'https://' + target_url

        try:
            # Create folder for the site
            domain = urlparse(target_url).netloc.replace('.', '_')
            base_folder = os.path.join(os.getcwd(), domain)
            assets_folder = os.path.join(base_folder, 'assets')
            
            os.makedirs(assets_folder, exist_ok=True)

            # Get the HTML
            response = requests.get(target_url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Simple Asset Download (CSS/Images)
            for tag in soup.find_all(['img', 'link']):
                attr = 'src' if tag.name == 'img' else 'href'
                asset_url = tag.get(attr)
                
                if asset_url:
                    full_url = urljoin(target_url, asset_url)
                    filename = download_file(full_url, assets_folder)
                    if filename:
                        tag[attr] = f'assets/{filename}'

            # Save the cloned HTML
            with open(os.path.join(base_folder, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(soup.prettify())

            message = f"Successfully cloned to folder: {domain}"
        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)