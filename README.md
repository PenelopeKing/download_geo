# download_geo

Tool to download data from Gene Expression Omnibus (GEO). It can download FASTQ files and supplementary files (peaks, txt, etc).
Step 1:
Download a CSV containing GSE code's metadata.
get_descriptions("GSEcode" , "/output/directory/")

Step 2:
Browse and select the files you wish to download.
browse_and_select_rows("path/to/csv" , "column_name_searching_by")


https://mybinder.org/v2/gh/PenelopeKing/download_geo/main?labpath=download_geo_binder.ipynb
(WIP)

