from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup  # <-- Add this import
import os

app = Flask(__name__)

# Directory where files will be temporarily stored
DOWNLOAD_DIR = "downloads"
ENSEMBL_URL = "https://ftp.ensembl.org/pub/release-112/fasta/mus_musculus/dna/"
UNIPROT_URL = "https://rest.uniprot.org/uniprotkb/search?query=organism_id:10090&format=json"


@app.route('/')
def index():
    ensembl_files = fetch_file_list(ENSEMBL_URL)
    return render_template('index.html', ensembl_files=ensembl_files)


@app.route('/download')
def download():
    file_name = request.args.get('file')
    if not file_name:
        return "File name not provided", 400

    ftp_url = ENSEMBL_URL + file_name
    file_path = os.path.join(DOWNLOAD_DIR, file_name)

    try:
        download_file(ftp_url, file_path)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e), 500


@app.route('/download_uniprot')
def download_uniprot():
    file_path = os.path.join(DOWNLOAD_DIR, "mouse_proteome.fasta")

    try:
        json_data = fetch_uniprot_data()
        fasta_data = convert_to_fasta(json_data)

        # Save FASTA data to a file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            file.write(fasta_data)

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e), 500


def fetch_file_list(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    files = [node.get('href') for node in soup.find_all('a') if node.get('href').endswith('.gz')]
    return files


def download_file(url, path):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    print(f"Downloaded {url} to {path} successfully.")


def fetch_uniprot_data():
    response = requests.get(UNIPROT_URL)
    response.raise_for_status()
    return response.json()


def convert_to_fasta(json_data):
    fasta_entries = []
    for entry in json_data.get('results', []):
        protein_id = entry.get('primaryAccession')
        protein_sequence = entry.get('sequence', {}).get('value')
        protein_name = entry.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value',
                                                                                                              'Unnamed protein')

        fasta_entry = f">{protein_id} {protein_name}\n{protein_sequence}\n"
        fasta_entries.append(fasta_entry)

    return "".join(fasta_entries)


if __name__ == '__main__':
    app.run(debug=True)
