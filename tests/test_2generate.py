#!/usr/bin/env python

######################################################.
# 	        Testing GENERATE with pytest 	         #
######################################################.

import os
import glob
import pytest
import shutil
import subprocess
import pandas as pd
from pathlib import Path

# saves the working directory
path_main = os.getcwd()
path_generate = os.getcwd() + "/GENERATE"

# GENERATE tests
@pytest.mark.parametrize(
    "test_job",
    [
        (
            "reduced"
        ),  # test with less models and partition sizes
        (
            "reduced_noPFI"
        ),  # test to disable the PFI analysis
        (
            "reduced_PFImax"
        ),  # test to select the number of PFI features
        (
            "reduced_rnd"
        ),  # test for random (RND) splitting
        (
            "reduced_others"
        ),  # test for other models        
        (
            "reduced_clas"
        ),  # test for clasification models
        (
            "standard"
        ),  # standard test
    ],
)
def test_GENERATE(test_job):

    # leave the folders as they were initially to run a different batch of tests
    if os.path.exists(f"{path_generate}"):
        shutil.rmtree(f"{path_generate}")
        # remove DAT and CSV files generated by GENERATE
        dat_files = glob.glob("*.dat")
        for dat_file in dat_files:
            if "GENERATE" in dat_file:
                os.remove(dat_file)
    if test_job == 'reduced_clas' and os.path.exists(f"{path_main}/GENERATE_clas"):
        shutil.rmtree(f"{path_main}/GENERATE_clas")

    # runs the program with the different tests
    if test_job == 'reduced_clas':
        csv_name = 'tests/Robert_example_clas.csv'
    else:
        csv_name = 'CURATE/Robert_example_CURATE.csv'
    cmd_robert = [
        "python",
        "-m",
        "robert",
        "--generate",
        "--csv_name", csv_name,
        '--y', 'Target_values',
        "--ignore", "['Name']",
        "--epochs", "10",
        "--seed", "[0]"
        ]

    if test_job != 'standard':
        if test_job != 'reduced_others':
            model_list = ['RF']
        else:
            model_list = ['Adab','VR','GP']
        if test_job == 'reduced_clas':
            train_list = [80]
        else:
            train_list = [60]

        if test_job == "reduced_noPFI":
            cmd_robert = cmd_robert + ["--pfi_filter", "False"]
        elif test_job == 'reduced_PFImax':
            cmd_robert = cmd_robert + ["--pfi_max", "2"]
        elif test_job == 'reduced_rnd':
            cmd_robert = cmd_robert + ["--auto_kn", "False"]
        elif test_job == 'reduced_clas':
            cmd_robert = cmd_robert + ["--type", "clas"]
    else: # needed to define the variables, change if default options change
        model_list = ['RF','GB','NN','MVL']
        train_list = [60,70,80]
    
    cmd_robert = cmd_robert + [
        "--model", f"{model_list}",
        "--train", f"{train_list}"]

    subprocess.run(cmd_robert)

    # check that the DAT file is created
    assert not os.path.exists(f"{path_main}/GENERATE_data.dat")
    outfile = open(f"{path_generate}/GENERATE_data.dat", "r")
    outlines = outfile.readlines()
    outfile.close()
    assert "ROBERT v" in outlines[0]
    assert "- 37 datapoints" in outlines[9]
    if test_job != 'reduced_clas':
        assert "- 12 accepted descriptors" in outlines[10]
    else:
        assert "- 9 accepted descriptors" in outlines[10]
    assert "- 1 ignored descriptors" in outlines[11]
    assert "- 0 discarded descriptors" in outlines[12]
    finding_line = False
    for line in outlines:
        if f"- 1/{len(model_list) * len(train_list)}" in line:
            finding_line = True
    assert finding_line

    # check that the right amount of CSV files were created
    expected_amount = len(model_list) * len(train_list) * 2
    if test_job != "reduced_noPFI":
        folders = ['No_PFI','PFI']
    else:
        folders = ['No_PFI']
        assert not os.path.exists(f'{path_generate}/Raw_data/PFI')

    for folder in folders:
        csv_amount = glob.glob(f'{path_generate}/Raw_data/{folder}/*.csv')
        if test_job != 'reduced_others':
            if test_job == 'standard':
                assert expected_amount == len(csv_amount)+6 # accounts for the failing GB jobs during hyperopt
            else:
                assert expected_amount == len(csv_amount)
        else:
            assert expected_amount == len(csv_amount)+2 # accounts for the failing GP jobs during hyperopt
        best_amount = glob.glob(f'{path_generate}/Best_model/{folder}/*.csv')
        assert len(best_amount) == 2
        params_best = pd.read_csv(best_amount[0])
        db_best = pd.read_csv(best_amount[1])
        if test_job in ['reduced','reduced_PFImax','reduced_rnd']:
            if folder == 'No_PFI':
                if test_job != 'reduced_clas':
                    desc_list = ['x2', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10', 'x11', 'Csub-Csub', 'Csub-H', 'Csub-O', 'H-O']
                else:
                    desc_list = ['x1', 'x2', 'x3', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10']
            elif folder == 'PFI':
                if test_job in ['reduced','reduced_rnd']:
                    desc_list = ['x6', 'x7', 'x10']
                elif test_job =='reduced_PFImax':
                    desc_list = ['x6', 'x7']

            if test_job in ['reduced','reduced_rnd']:    
                sum_split = 0
                if db_best['Set'][0] == 'Training':
                    sum_split += 1
                if db_best['Set'][1] == 'Training':
                    sum_split += 1
                if db_best['Set'][2] == 'Training':
                    sum_split += 1
                if db_best['Set'][3] == 'Validation':
                    sum_split += 1
                if test_job == 'reduced':
                    assert sum_split == 4
                elif test_job == 'reduced_rnd':
                    assert sum_split < 4
            for var in desc_list:
                assert var in params_best['X_descriptors'][0]
            assert len(desc_list) == len(params_best['X_descriptors'][0].split(','))
    
    # check that the heatmap plots were generated
    assert os.path.exists(f'{path_generate}/Raw_data/Heatmap ML models no PFI filter.png')
    if test_job != "reduced_noPFI":
        assert os.path.exists(f'{path_generate}/Raw_data/Heatmap ML models with PFI filter.png')
    else:
        assert not os.path.exists(f'{path_generate}/Raw_data/Heatmap ML models with PFI filter.png')

    # Check that the default metric for classification models is MCC
    if test_job == 'reduced_clas':
        csv_clas = glob.glob(f'{path_generate}/Best_model/PFI/RF_80_PFI.csv')
        df = pd.read_csv(csv_clas[0])
        if 'error_type' in df.columns:
            error_types = df['error_type'].tolist()
        assert 'mcc' in error_types

    if test_job == 'reduced_clas':
        filepath = Path(f"{path_generate}")
        filepath.rename(f"{path_main}/GENERATE_clas")
