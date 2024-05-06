# ANAC Open Data downloader and filter by region and year

![PyPI - Python Version](https://img.shields.io/badge/python-3.12-3776AB?logo=python)

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

### > Files

#### ```01_anac_od_download.py```
Application to download public notices (tenders) from the ANAC website and create a global dataset.

#### ```02_anac_od_select.py```
Application to select ANAC Open Data of interest from the global dataset. Filter the main data obtained from ```01_anac_od_download.py```.

#### ```anac_od_select.json```
List of filters according to ANAC nomenclature.

#### ```anac_od_region.json```
List of filters according to ANAC region names and convenience output name (generates one file per region).

#### ```anac_urls_dynamic.json```
List of dynamic URLs (files) to download; source [https://dati.anticorruzione.it/opendata](https://dati.anticorruzione.it/opendata)

#### ```anac_urls_static.json```
List of static URLs (files) to download; source [https://dati.anticorruzione.it/opendata](https://dati.anticorruzione.it/opendata)

#### ``ssl_adapter.py``
Class to execute requests via HTTPS.