# Pharmacogenomics database
In the rapidly evolving field of pharmacogenomics, the demand for efficient and user-friendly tools to access and analyze genetic data in the context of medication-use has never been greater. Researchers and healthcare professionals seek solutions that empower them to explore the intricate relationship between an individual's genetic makeup and their response to various drugs. To meet this need, we have developed an interactive web-based resource, PGxDB, offering a dynamic platform for comprehensive pharmacogenomics research and hypothesis testing covering diverse data types. 
## Introduction
This repo serves as a code base for PGxDB
## How to start
### Prerequisites
* Python 3.8++
* Virtualenv
* PostgreSQL 12++
### Installation
**Note**: This tutorial is tested on Macbook M1 with MacOS Ventura 13.3.1. It should work on Ubuntu or other Linux distributions.
* Clone this repository
* Go to project folder
* Create virtual environment with command `python -m venv venv`
* Activate virtual environment with command `source venv/bin/activate`
* Install libraries with command `python -m pip install -r requirements.txt`
* Create `.env` file in project folder with content from `.env.example` file: `cp .env.example .env`. Then update values in `.env` file
* Run command `python manage.py migrate` to create database
* Run command `python manage.py runserver` to start server

### Import data
* Download data from [this Google Drive link](https://drive.google.com/file/d/1atLQWvx2kSH_iF5ueNi1ZBcoIfxHT2z-/view?usp=sharing)
* Create `data` folder then extract data to this folder
* Run command `python scripts/run_many_builds.py` to import data to database

### Develop API
All APIs are developed in `api` app.

#### Example
`GET /api/v1/gene/{gene_id}/` to get gene information

#### DRF (Django Rest Framework)
* Install (pip install -r requirements.txt)
* Add urls to /restapi/urls.py
* Add views to /restapi/views.py
* [DRF browsable API](https://www.django-rest-framework.org/topics/browsable-api/)