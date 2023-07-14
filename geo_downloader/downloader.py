from geofetch import Geofetcher
import pysradb.sraweb
import pandas as pd
import os
import urllib.request
import sys
import requests
import time
from bs4 import BeautifulSoup
import regex as re


### Metadata functions ###
def find_sub_gse(super_gse):
    """
    Helper Function
    Using a super series accession code, gets the sub series accession codes via webscrapping
    input: super_gse (str)
    output: sub_gse (str list)
    """
    
    # get sub-gse info from ncbi website
    base_link = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='
    response = requests.get(base_link+super_gse)
    start = time.time()
    soup = BeautifulSoup(response.text, features='lxml')
    pattern = re.compile(r'^GSE') # pattern looking for in text
    href = '/geo/query/acc.cgi?acc' # pattern looking for in links
    a_href = soup.find_all('a', href=True, text=pattern)
    
    # finds sub gse accession codes
    sub_gse = []
    for sub in a_href:
        temp = sub.text.strip().upper()
        if temp != super_gse:
            sub_gse.append(temp)
    
    # to accomodate robots.txt, must wait 5 seconds before web scrape again
    end = time.time()
    to_wait = 5 - (end-start)
    if to_wait < 0:
        to_wait = 0
    time.sleep(to_wait)
    
    return sub_gse

def get_series_files(gse):
    """
    Helper Function
    uses geofetch to get supplemental data files using a GSE accession #
    
    input: gse (str)
    output: df of supp data file info
    """
    
    # get supplemental data
    geof = Geofetcher(processed=True, data_source='all', just_metadata=True, discard_soft = True)
    proj = geof.get_projects(gse)
    
    # check if supplemental data exists
    gse_series = gse + '_series'
    if gse_series in proj.keys():
        df = proj[gse_series].sample_table
        # clean columns, names for consistency when concatenating df's
        keep = ['file','sample_name', 'series_sample_organism', 'series_sample_id', 'file_url', 'series_overall_design','series_type']
        df= df[keep]
        df.insert(loc = df.shape[1], column = 'study_alias', value = [gse] * df.shape[0])
        return df.rename(columns={'series_sample_organism': 'organism_name',
                                 'sample_name':'title',
                                 'series_sample_id':'GSM',
                                 'series_overall_design':'description'}).reset_index(drop=True)
    else:
        return pd.DataFrame()

    
def get_descriptions(gse, output_path):
    """
    Gets a compliation of metadata for a GSE accession number, saves it in the output path
    
    PARAMETERS:
        gse (str): GSE accession number
        output_path (str): desired output path to put saved csv file
        
    RETURNS:
        pandas DataFrame object containing metadata for the inputted GSE accession number
    """
    
    ### input validation ###
    gse = gse.strip()
    gse = gse.upper()
    print('Downloading {}...'.format(gse))
    if (not type(gse) is str) or (gse[:3] != 'GSE'):
        print("Incorrect formatting! Input must be a string starting with GSE followed by numbers")
        return
    if (gse == ''):
        print("please enter input")
        return
    ### end of validation ###
    
    def clean_df(df):
        '''
        helper function
        '''
        cols_keep = ['run_accession', 'experiment_title', 'study_alias', 'organism_name', 'experiment_alias', 
                    'experiment_desc','total_spots', 'total_size', 'run_total_spots','run_total_bases']
        output =  df[cols_keep].rename(columns={'run_accession':'file',
                                    'experiment_title':'title', 
                                     'experiment_desc': 'description',
                                    'experiment_alias' : 'GSM'})
        return output
      
    
    # gets relevant information
    geo_helper = pysradb.sraweb.SRAweb()
    gsm_srx = geo_helper.gse_to_gsm(gse)
    
    try:
        srp = geo_helper.gse_to_srp(gse)['study_accession'][0] # gets the srp code
    
    # catches error that happens if gse is a super_gse, performs webscraping
    except ValueError:
        sub_gse_lst = find_sub_gse(gse)
    else:
        sub_gse_lst = [gse]
    
    finally:
        output = pd.DataFrame()
        series_df = pd.DataFrame()
        
        for sub_gse in sub_gse_lst:
            # for sra data
            srp = geo_helper.gse_to_srp(sub_gse)['study_accession'][0] # gets the srp code
            df = geo_helper.sra_metadata(srp) # contains meta info of data for gse
            sub_output = pd.merge(gsm_srx, df)
            output = pd.concat([output, sub_output], axis=0, ignore_index=True).reset_index(drop=True)
            # for supplemental data
            sub_series = get_series_files(sub_gse)
            series_df = pd.concat([series_df, sub_series], axis=0, ignore_index=True).reset_index(drop=True)
        
        # clean output data frame
        output =  clean_df(output)
        if series_df.shape != (0,0):
            # concat srr (fastq) and supp series data frames
            output = pd.concat([output, series_df], axis=0, ignore_index=True).reset_index(drop=True)

        # turn output into csv, download it
        filename = gse + '_metadata.csv'
        filename = os.path.join(output_path, filename)
        output.to_csv(filename)
        print('\nA .csv version of this dataframe has been saved at {}'.format(filename))
    return output

### Downloading file functions ###

def download_files(df, output_path, idx_list=[]):
    """
    downloads files from csv path OR pandas DataFrame using index list as a marker of what to download
    
    PARAMETERS:
        df: a result of calling get_descriptions(); either a path to a csv or a pandas.DataFrame() object
        output_path: output to put saved /download_files/
        idx_list: (optional) what specific row indexes you want to download
            if nothing is selected or idx_list is empty, downloads all rows of the entire .csv/DataFrame
    
    RETURNS: 
        none
    """
    
    # if file path
    if type(df) == str:
        df = pd.read_csv(df)
        
    # if no idx_list was provided, will download ALL the files in the csv file
    if len(idx_list) == 0:
        # split btw fastq and supplemental files
        lst = df['file']
        srr_to_download = lst[lst.apply(lambda x: 'SRR' in x)].to_list()
        supp_to_download = lst[~lst.apply(lambda x: 'SRR' in x)].index.to_list()
    else:
        # split btw fastq and supplemental files
        lst = df['file'].iloc[idx_list]
        srr_to_download = lst[lst.apply(lambda x: 'SRR' in x)].to_list()
        supp_to_download = lst[~lst.apply(lambda x: 'SRR' in x)].index.to_list()
    
    # makes folder for files to download
    download_path = os.path.join(output_path, 'downloaded_files')
    try: 
        os.mkdir(download_path)
    except:
        pass
    
    ### downloading supplemental files ###
    print('Downloading supplemental files...\n')
    for supp_idx in supp_to_download:
        download_link = 'https://' + df.iloc[supp_idx]['file_url'].split("//")[-1]
        file_name = os.path.join(download_path, download_link.split("/")[-1])
        urllib.request.urlretrieve(download_link, file_name)

    ### downloading fastq files ###
    print('Downloading FASTQ files... this make take a bit...\n')
    for srr in srr_to_download:
        # prefetch srr files for quicker download
        download_path = os.path.join(output_path, 'downloaded_files')
        pf_cmd = 'prefetch {} -O {}'.format(srr, download_path)
        print(pf_cmd)
        os.system(pf_cmd)
        # download fastq
        path = os.path.join(download_path,os.path.join(srr, srr+'.sra'))
        fastq_cmd = 'fasterq-dump --outdir {} {}'.format(os.path.join(download_path, srr), output_path)
        print(fastq_cmd)
        os.system(fastq_cmd)

    print('\nComplete\n')
