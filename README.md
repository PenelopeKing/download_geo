# download_geo

Tool to download data from Gene Expression Omnibus (GEO). 

Using just the GSE code (GSE#), you are able to download FASTQ files and supplementary files (peaks, txt, etc).

You can use this on Binder: https://mybinder.org/v2/gh/PenelopeKing/download_geo/main?labpath=download_geo_binder.ipynb



## How to Use on `download_geo_binder.ipynb`

##### Step 1:
Get GSE code.

```preview_data_visual()```

##### Step 2:
Download a CSV containing GSE's metadata obtained from Step 1.

````display_csv(csv_path)```

##### Step 2:
Browse and select the files you wish to download using the path to the csv and the column want to search by

````browse_and_select_rows_binder(csv_path, column_name)```




