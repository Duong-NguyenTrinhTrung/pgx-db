#!/bin/bash

echo "Start run build data scripts" 

# Activate virtual environment
# source venv/bin/activate

# Run build data scripts

echo "Start run many builds" 

python manage.py build_variant_mapping
# python scripts/run_many_builds.py

echo "End run many builds"

# Run other scripts

###

echo "End run build data scripts"

# Deactivate virtual environment
# deactivate