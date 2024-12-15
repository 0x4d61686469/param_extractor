#!/usr/bin/python3

import re
import os
import json
import argparse

# Function to extract variable declarations from JavaScript (including inside functions and destructuring)
def extract_variables(js_content):
    # Regex for simple variable declarations (var, let, const)
    var_pattern = re.compile(r'\b(var|let|const)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:=|;)', re.MULTILINE)
    variables = re.findall(var_pattern, js_content)

    # Extract just the variable names (ignore the declaration type like var/let/const)
    variable_names = [var[1] for var in variables]

    # Regex to capture function expressions (anonymous functions, arrow functions)
    func_expr_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*\s*)?=\s*(function\s?\(.*\)|\(.+?\)\s*=>)', re.DOTALL)
    func_exprs = re.findall(func_expr_pattern, js_content)

    # Capture function parameters from function expressions
    func_expr_vars = []
    for expr in func_exprs:
        params = re.findall(r'\((.*?)\)', expr[1])  # Find parameters inside parentheses
        for param in params:
            param = param.strip()
            if param and param not in func_expr_vars:
                func_expr_vars.append(param)

    # Regex for destructuring assignments (object and array destructuring)
    destructuring_pattern = re.compile(r'\{([a-zA-Z0-9_,\s]+)\}|\[([a-zA-Z0-9_,\s]+)\]', re.DOTALL)
    destructuring_vars = re.findall(destructuring_pattern, js_content)

    # Flatten and clean the results for destructuring
    destructuring_vars = [var.strip() for group in destructuring_vars for var in group if var.strip()]

    # Regex to find function parameters in named functions
    func_pattern = re.compile(r'function\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\((.*?)\)', re.DOTALL)
    functions = re.findall(func_pattern, js_content)

    # Extract variables in function parameters
    func_vars = []
    for func in functions:
        params = func.split(',')
        for param in params:
            param = param.strip()
            if param and param not in func_vars:
                func_vars.append(param)

    return variable_names + destructuring_vars, func_vars + func_expr_vars

# Function to read and process a JS file
def process_js_file(js_file_path):
    with open(js_file_path, 'r', encoding='utf-8') as file:
        js_content = file.read()
    
    return extract_variables(js_content)

# Function to scan a directory of JS files
def process_js_files_in_directory(directory_path):
    all_variables = set()
    all_func_vars = set()
    
    # Iterate over all files in the given directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.js'):
            js_file_path = os.path.join(directory_path, filename)
            print(f"Processing: {js_file_path}")
            variables, func_vars = process_js_file(js_file_path)
            all_variables.update(variables)
            all_func_vars.update(func_vars)
    
    return all_variables, all_func_vars

# Function to save output in JSON format
def save_to_json(variables, func_vars, output_file):
    output_data = {
        "variables": list(variables),
        "function_parameters": list(func_vars)
    }
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(output_data, json_file, indent=4)
    print(f"Output saved to {output_file}")

# Main function to accept user input from command-line arguments
if __name__ == '__main__':
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Extract JavaScript variables and function parameters.")
    parser.add_argument('js_path', help="Path to a JS file or directory containing JS files.")
    parser.add_argument('output_json', help="Path to the output JSON file where results will be saved.")
    
    args = parser.parse_args()
    
    # Get the file or directory path and output JSON file path from arguments
    js_file_path = args.js_path
    output_file = args.output_json
    
    # Check if the input path is a valid file or directory
    if os.path.isfile(js_file_path):
        variables, func_vars = process_js_file(js_file_path)
        print("Variables found:", variables)
        print("Function parameters found:", func_vars)
        save_to_json(variables, func_vars, output_file)
    elif os.path.isdir(js_file_path):
        variables, func_vars = process_js_files_in_directory(js_file_path)
        print("All variables found:", variables)
        print("All function parameters found:", func_vars)
        save_to_json(variables, func_vars, output_file)
    else:
        print("Invalid file or directory path!")
