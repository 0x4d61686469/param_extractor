import sys

# Get the file names from stdin
domains_file = sys.argv[1]
paths_file = sys.argv[2]

# Read the domains from the domains file
with open(domains_file, 'r') as domain_file:
    domains = [line.strip() for line in domain_file.readlines()]

# Read the paths from the paths file
with open(paths_file, 'r') as path_file:
    paths = [line.strip() for line in path_file.readlines()]

# Combine domains and paths to create full URLs
for domain in domains:
    for path in paths:
        print(f"https://{domain}{path}")
