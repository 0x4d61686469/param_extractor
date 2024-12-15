import os
import json
import argparse
from bs4 import BeautifulSoup
from charset_normalizer import detect



def normalize_parameter(param):
    """
    Normalize parameters by:
    - Removing leading `/`.
    - Stripping file extensions (.css, .js, .png, etc.).
    """
    if param.startswith('/'):
        param = param[1:]  # Remove leading slash
    if '.' in param:
        param = param.split('.')[0]  # Remove file extension
    return param


def extract_parameters_from_html(html_content):
    """
    Extracts parameters from HTML content and normalizes them.
    Looks for attributes like `name`, `id`, `href`, `src`, `action`, and `value`.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    parameters = set()

    # Extract `name` and `id` attributes from input fields and other elements
    for tag in soup.find_all(['input', 'textarea', 'select', 'button', 'form']):
        if tag.has_attr('name'):
            parameters.add(normalize_parameter(tag['name']))
        if tag.has_attr('id'):
            parameters.add(normalize_parameter(tag['id']))

    # Extract parameters from `href` and `src` attributes in links and scripts
    for tag in soup.find_all(['a', 'script', 'link', 'img', 'iframe']):
        if tag.has_attr('href'):
            parameters.add(normalize_parameter(tag['href']))
        if tag.has_attr('src'):
            parameters.add(normalize_parameter(tag['src']))

    # Extract `action` attributes from forms
    for tag in soup.find_all('form'):
        if tag.has_attr('action'):
            parameters.add(normalize_parameter(tag['action']))

    # Extract `value` attributes from inputs
    for tag in soup.find_all('input'):
        if tag.has_attr('value'):
            parameters.add(normalize_parameter(tag['value']))

    return list(parameters)


def process_html_file(html_file_path):
    """Reads an HTML file with dynamic encoding detection and extracts parameters."""
    with open(html_file_path, 'rb') as file:
        raw_data = file.read()
        encoding = detect(raw_data)['encoding']  # Detect the file encoding

    html_content = raw_data.decode(encoding)
    return extract_parameters_from_html(html_content)


def process_html_files_in_directory(directory_path):
    """Processes all HTML files in a directory."""
    all_parameters = set()

    for filename in os.listdir(directory_path):
        if filename.endswith('.html'):
            html_file_path = os.path.join(directory_path, filename)
            print(f"Processing: {html_file_path}")
            parameters = process_html_file(html_file_path)
            all_parameters.update(parameters)

    return list(all_parameters)


def save_to_json(parameters, output_file):
    """Saves extracted parameters to a JSON file."""
    output_data = {"parameters": parameters}
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(output_data, json_file, indent=4)
    print(f"Output saved to {output_file}")


if __name__ == '__main__':
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Extract parameters from HTML files.")
    parser.add_argument('html_path', help="Path to an HTML file or directory containing HTML files.")
    parser.add_argument('output_json', help="Path to the output JSON file where results will be saved.")
    
    args = parser.parse_args()

    # Get the file or directory path and output JSON file path from arguments
    html_path = args.html_path
    output_file = args.output_json

    # Check if the input path is a valid file or directory
    if os.path.isfile(html_path):
        parameters = process_html_file(html_path)
        print("Parameters found:", parameters)
        save_to_json(parameters, output_file)
    elif os.path.isdir(html_path):
        parameters = process_html_files_in_directory(html_path)
        print("All parameters found:", parameters)
        save_to_json(parameters, output_file)
    else:
        print("Invalid file or directory path!")
