# ANAC Open Data downloader

![PyPI - Python Version](https://img.shields.io/badge/python-3.12-3776AB?logo=python)

## Goal
The script downloads the Open Data from the ANAC website, unzips them, merges the ```cig_*.csv``` type data, filters them according to the parameters in the ```anac_od_select.json``` file, and finally extracts the data by region.
Starting website: [https://dati.anticorruzione.it/opendata](https://dati.anticorruzione.it/opendata).  
The script also downloads PA-related data from the websites of ISTAT and Open BDAP.  

### > Directories

#### config
Configuration directory with ```config.yml```
- [ ] Define the starting/ending years to download ```YEAR_START_DOWNLOAD``` and ```YEAR_END_DOWNLOAD``` (it contains the ```bando_cig_*``` merged files from dynamic URLs).
- [ ] Define the filters in the file referenced by ```ANAC_OD_SELECT```.
- [ ] Define the filters in the file referenced by ```ANAC_OD_REGION``` to create CSV filtered by region.

#### data
Directory with filtered data starting from the one downloaded.

#### download
Directory with download files from ANAC (zip and csv). 

#### pa_registry
Directory with PA registry (for PA type); source: [https://openbdap.rgs.mef.gov.it](https://openbdap.rgs.mef.gov.it)

#### stats
Directory with procurements stats.

#### utility_manager
Directory with utilities functions.

### > Script Execution

#### ```01_anac_od_download.py```
Application to download public notices (tenders) from the ANAC website and create a global dataset.

#### ```01_istat_bdap_od_download.py```
Application to download ISTAT and Open BDAP data. After downloading, move the CSV and XLSX files to ```OD_ISTAT_DIR``` and ```OD_BDAP_DIR```.

#### ```02_anac_od_select.py```
Application to select ANAC Open Data of interest from the global dataset. Filter the main data obtained from ```01_anac_od_download.py```.

#### ```anac_od_region.json```
List of filters according to ANAC region names and convenience output name (generates one file per region).

#### ```anac_od_select.json```
List of filters according to ANAC nomenclature.

#### ```anac_urls_dynamic.json```
List of dynamic URLs (files) to download; source [https://dati.anticorruzione.it/opendata](https://dati.anticorruzione.it/opendata)

#### ```anac_urls_static.json```
List of static URLs (files) to download; source [https://dati.anticorruzione.it/opendata](https://dati.anticorruzione.it/opendata)

#### ```bdap_urls_static.json```
List of static URLs (files) to download; source [https://bdap-opendata.rgs.mef.gov.it](https://bdap-opendata.rgs.mef.gov.it)

#### ```istat_urls_static.json```
List of static URLs (files) to download; source [https://dati.anticorruzione.it/opendata](https://dati.anticorruzione.it/opendata)

#### ``ssl_adapter.py``
Class to execute requests via HTTPS.

### > Script Dependencies
See ```requirements.txt``` for the required libraries (```pip install -r requirements.txt```).  

## Share
If you use it, please cite:

```
@article{NAI2023105887,
title = {Public tenders, complaints, machine learning and recommender systems: a case study in public administration},
journal = {Computer Law & Security Review},
volume = {51},
pages = {105887},
year = {2023},
issn = {0267-3649},
doi = {https://doi.org/10.1016/j.clsr.2023.105887},
url = {https://www.sciencedirect.com/science/article/pii/S0267364923000973},
author = {Roberto Nai and Rosa Meo and Gabriele Morina and Paolo Pasteris},
keywords = {Public procurement, Legal prediction, Complaint detection, Knowledge discovery, Natural language processing, Machine learning, Recommender system},
}
```