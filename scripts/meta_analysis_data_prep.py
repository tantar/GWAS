import pandas as pd
import os
import glob
import re
from functools import reduce
import subprocess
import argparse

# convert rvtest .tab files ---> PLINK .assoc files and rvtest .tab files ---> metasoft .txt files
parser = argparse.ArgumentParser(description='Arguments for GWAS Meta-analysis
# parser.add_argument('--assoc', type=str, default='nope', help='GWAS: (string file path). Path to PLINK format .assoc files, full path as follows: /path/to/files/dir/ [default: nope].')
parser.add_argument('--tab', type=str, default='nope', help='GWAS: (string file path). Path to rvtest format .tab files, everything before the ".assoc" [default: nope].')
parser.add_argument('--out_plink', type=str, default='out', help='Prefix for plink .assoc output (including path)')
parser.add_argument('--out_metasoft', type=str, default='out', help='Prefix for metasoft .txt output (including path)')
                                 
args = parser.parse_args()



basedir = '/data/vitaled2/summary_stats/rvtest_files/'
file_list = glob.glob(basedir + '*.tab')
suffixes = [re.search(r'\.(.*?)\.', cohort).group(1) for cohort in file_list]



# the following generates .assoc files for plink --meta-analysis method from rvtest .tab files
def plink_meta_parse(assoc_path, out_path):
    summary_data_list = [pd.read_csv('/data/vitaled2/summary_stats/rvtest_files/' + file, sep='\t') for file in file_list]
    for i in range(len(summary_data_list)):
        df = summary_data_list[i]
        df2 = df[['markerID', 'beta', 'se', 'P']]
        df2.columns = ['SNP','OR','SE','P']
        split = df.markerID.str.split(':', expand=True)
        df2['CHR'] = split[0]
        df2['BP'] = split[1]
        df2['A1'] = df.minorAllele
        df2['A2'] = df.majorAllele
        df_final = df2.sort_values('P').drop_duplicates(['SNP'], keep='first')
        df_final.to_csv('/data/vitaled2/summary_stats/' + suffixes[i] + '_random_effect_data.assoc', sep='\t', index=False)


# the following generates .txt files with "snp" "beta1" "se1" "beta2" "se2"... "betaN" "seN" for N number of GWAS inputs for metasoft java meta analysis implementation from rvtests .tab files
def metasoft_meta_parse(in_path, out_path):
    summary_data_list_cleaned = []
    for i in range(len(file_list)):
        df = pd.read_csv(file_list[i], sep='\t', usecols=['markerID','beta','se','P'])
        df_sorted = df.sort_values('P').drop_duplicates(['markerID'], keep='first')
        df_cleaned = df_sorted.drop(columns=['P'])
        summary_data_list_cleaned.append(df_cleaned)

    # select markers that exist across all datasets
    merged = reduce(lambda x, y: pd.merge(x, y, on=['markerID'], how='inner'), summary_data_list_cleaned) 
    merged.to_csv(basedir + "random_effect_test_5_cohorts.txt", index=False, header=False, sep='\t')


    
    
    
    
    
#     plink2 --meta-analysis COURAGE_UK_random_effect_data.assoc HBS_random_effect_data.assoc IPDGC_random_effect_data.assoc PDBP_random_effect_data.assoc PPMI_random_effect_data.assoc


############This method combines all into a single df for R 'meta' implementation
# for i in range(len(summary_data_list)):
#     summary_data_list[i]['cohort'] = suffixes[i]

# summary_df = pd.concat(summary_data_list)

# # # drop duplicate markers within cohorts, keeping maker with lowest pval
# summary_df_cleaned = summary_df.sort_values('P').drop_duplicates(['markerID','cohort'], keep='first')



# markers_list = []
# for i in range(len(file_list)):
#     markers = pd.read_csv('/data/vitaled2/summary_stats/rvtest_files/' + file_list[i], sep='\t', usecols=['markerID', 'beta', 'se'])
#     markers_list.append(markers)

# summary_data_list = [pd.read_csv(basedir + file, sep='\t', usecols=['markerID','beta','se','P']) for file in file_list]    
    
    
# marker_list = list(merged.drop(merged.columns.difference(['markerID']), axis=1).drop_duplicates('markerID').markerID)

# final_df = summary_df_cleaned[summary_df_cleaned.markerID.isin(marker_list)]
# final_sorted = final_df.sort_values(['markerID'])
# final = final_sorted[['markerID', 'beta', 'se']]

# final.to_csv("random_effect_test_5_cohorts.csv", index=False, sep='\t')
