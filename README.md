# ANAC Open Data Downloader

![PyPI - Python Version](https://img.shields.io/badge/python-3.12-3776AB?logo=python)

## Contents
1. [Objective](#objective)
2. [Project Structure](#project-structure)
3. [Main Scripts](#main-scripts)
4. [Configuration Files](#configuration-files)
5. [Installation](#installation)
6. [Citation](#citation)

---

## Objective

This script downloads open data from the ANAC website, extracts them, merges `cig_*.csv` type data, filters them according to parameters in the `anac_od_select.json` file, and finally extracts data by region.

- **Primary Source**: [https://dati.anticorruzione.it/opendata](https://dati.anticorruzione.it/opendata)
- **Additional Data**: Also downloads Public Administration-related data from ISTAT and Open BDAP websites

---

## Project Structure

```
.
├── config/                          # Configuration
│   ├── config.yml                   # Main parameters
│   └── config_reader.py             # Configuration reader
├── utility_manager/                 # Utility functions
│   └── utilities.py
├── stats/                           # Procurement statistics
├── download_anac/                   # Downloaded ANAC files (zip and csv)
├── download_istat/                  # Downloaded ISTAT files
├── download_bdap/                   # Downloaded BDAP files
├── open_data_anac/                  # Filtered ANAC data
├── open_data_istat/                 # ISTAT data
├── open_data_bdap/                  # BDAP data
├── 01_anac_od_download.py           # ANAC download script
├── 01_istat_bdap_od_download.py     # ISTAT/BDAP download script
├── 02_anac_od_select.py             # Data filtering script
├── ssl_adapter.py                   # SSL adapter for HTTPS
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## Main Scripts

### 01_anac_od_download.py
Downloads public tender data from the ANAC website and creates a global dataset.

**Functionality:**
- Generates dynamic URLs for configured years
- Downloads ZIP files
- Extracts files
- Merges CSV files with `cig_*.csv` prefix
- Logs all operations to `01_anac_od_download.log`

### 01_istat_bdap_od_download.py
Downloads ISTAT and Open BDAP data related to Public Administrations.

**Functionality:**
- Downloads files from ISTAT and Open BDAP
- Extracts files
- Moves CSV/XLSX to dedicated folders

### 02_anac_od_select.py
Filters and processes ANAC data downloaded by the first script.

**Functionality:**
- Filters data according to *anac_od_select.json*
- Performs a join with PA data from ANAC and Open BDAP
- Generates regional files according to *anac_od_region.json*

---

## Configuration Files

### config/config.yml
Main project parameters:
- `YEAR_START_DOWNLOAD` - Download start year
- `YEAR_END_DOWNLOAD` - Download end year
- `ANAC_DYNAMIC_URLS_JSON` - Dynamic URLs file (varies by year/month)
- `ANAC_STATIC_URLS_JSON` - Static URLs file
- `ANAC_OTHER_DATASET_NAMES` - List of additional dataset names
- Output folder paths

### *anac_urls_dynamic.json*
Dynamic URLs with placeholders:
- `{YYYY}` - Year (4 digits)
- `{MM}` - Month (2 digits with leading zero)
- `{DD}` - Day (2 digits with leading zero)
- `{dataset-name}` - Dataset name

Example:
```json
{
  "cig": ["https://dati.anticorruzione.it/opendata/download/dataset/cig-{YYYY}/filesystem/cig_csv_{YYYY}_{MM}.zip"],
  "others": ["https://dati.anticorruzione.it/opendata/download/dataset/{dataset-name}/filesystem/{YYYY}{MM}{DD}-{dataset-name}_csv.zip"]
}
```

### *anac_urls_static.json*
Static URLs (files that do not change over time)

### *anac_od_select.json*
Filters for selecting data of interest from ANAC

### *anac_od_region.json*
Filters for generating separate CSV files by region

### *bdap_urls_static.json*
URLs for downloading data from [https://openbdap.rgs.mef.gov.it](https://openbdap.rgs.mef.gov.it)

### *istat_urls_static.json*
URLs for downloading ISTAT data

---

## Installation

### Prerequisites
- Python 3.12+
- pip

### Procedure
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure parameters in `config/config.yml`
4. Run the scripts:
   ```bash
   python 01_anac_od_download.py
   python 01_istat_bdap_od_download.py
   python 02_anac_od_select.py
   ```

### Logging
The script 01_anac_od_download.py generates a log file with the same name:
- `01_anac_od_download.log` - Tracks all downloaded URLs and errors

---

## Technologies

- **pandas** - CSV data processing
- **PyYAML** - Configuration file reading
- **Requests** - HTTP/HTTPS file downloading
- **urllib3** - SSL connection management

---

## Citation

If you use this project, please cite [https://www.nature.com/articles/s41597-024-04342-5](https://www.nature.com/articles/s41597-024-04342-5):

```bibtex
@article{sd_Nai2024,
  author = {Nai, Roberto and Sulis, Emilio and Meo, Rosa},
  year = {2024},
  title = {ITH: an open database on Italian Tenders 2016--2023},
  journal = {Scientific Data},
  volume = {11},
  number = {1},
  pages = {1452},
  abstract = {Governments procure large amounts of goods and services to help them implement policies and deliver public services; in Italy, this is an essential sector, corresponding to about 12\% of the gross domestic product. Data are increasingly recorded in public repositories, although they are often divided into multiple sources and not immediately available for consultation. This paper provides a description and analysis of an effort to collect and arrange a legal public administration database. The main source of interest involves the National Anti-Corruption Authority in Italy, which describes more than 3 million tenders. To improve usability, the database is integrated with two other relevant data sources concerning information on public entities and territorial units for statistical purposes. The period identified by domain experts covers 2016--2023. The analysis also identifies key challenges that arise from the current Open Data catalogue, particularly in terms of data completeness. A practical application is described with an example of use. The final dataset, called Italian Tender Hub (ITH), is available in a repository with a description of its use.},
  issn = {2052-4463},
  url = {https://doi.org/10.1038/s41597-024-04342-5},
  doi = {10.1038/s41597-024-04342-5}
}
```
