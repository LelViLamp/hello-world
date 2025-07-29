#!/bin/bash

# OpenAPI Endpoint Checklist Generator
# Generates a coloured checklist of API endpoints for Obsidian

if [ $# -eq 0 ]; then
    echo "Usage: $0 <openapi-spec.yaml>"
    echo "Generates a coloured checklist of API endpoints from an OpenAPI specification"
    exit 1
fi

YAML_FILE="$1"

if [ ! -f "$YAML_FILE" ]; then
    echo "Error: File '$YAML_FILE' not found"
    exit 1
fi

# Check if yq is installed
if ! command -v yq &> /dev/null; then
    echo "Error: yq is not installed. Please install it first:"
    echo "  brew install yq  # On macOS"
    echo "  sudo apt install yq  # On Ubuntu/Debian"
    exit 1
fi

echo "# API Endpoints Checklist"
echo

yq eval '.paths | to_entries | .[] | .key as $path | .value | to_entries | .[] | (.key | upcase) + " " + $path' "$YAML_FILE" | \
sed -E 's/^GET /- [ ] <span style="background-color: #61affe; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">GET<\/span> /' | \
sed -E 's/^POST /- [ ] <span style="background-color: #49cc90; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">POST<\/span> /' | \
sed -E 's/^PUT /- [ ] <span style="background-color: #fca130; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">PUT<\/span> /' | \
sed -E 's/^PATCH /- [ ] <span style="background-color: #50e3c2; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">PATCH<\/span> /' | \
sed -E 's/^DELETE /- [ ] <span style="background-color: #f93e3e; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">DELETE<\/span> /'
