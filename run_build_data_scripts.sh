#!/bin/bash

echo "Start run build_adding_highest_AF" 

# Activate virtual environment
# source venv/bin/activate

# Run build build_adding_highest_AF

echo "Start run build_adding_highest_AF" 

python manage.py build_adding_highest_AF
# python scripts/run_many_builds.py

echo "End run build_adding_highest_AF"

# Run other scripts

###

echo "End run build build_adding_highest_AF"

# Deactivate virtual environment
# deactivate