# geo_downloader

Tool to download data from Gene Expression Omnibus (GEO). 

Using a series (GSE) accession number (GSE#), you are able to download its corresponding FASTQ files (SRA) and supplementary files (peaks, txt, etc).

You can use this tool on Binder: https://mybinder.org/v2/gh/PenelopeKing/download_geo/main?labpath=download_geo_binder.ipynb



## How to Use `download_geo_binder.ipynb` on Binder

##### Step 1:
Get GSE accession number via [GEO](https://www.ncbi.nlm.nih.gov/geo/).

##### Step 2:
Download a CSV containing the series' metadata using the GSE accession number.

```
preview_data_visual(gse)
```

#### Step 3:
Preview metadata.

```
display_csv(csv_path)
```

##### Step 4:
Browse and select the files you wish to download using the path to the csv and the column you want to search by.

```
browse_and_select_rows_binder(csv_path, column_name)
```

#### Step 5:
Download the files from Binder onto your own system.

