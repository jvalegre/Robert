#!/usr/bin/env python

######################################################.
# 	         Testing PREDICT with pytest 	         #
######################################################.

import os
import glob
import pytest
import shutil
import subprocess
from pathlib import Path

# saves the working directory
path_main = os.getcwd()
path_predict = path_main + "/PREDICT"

# PREDICT tests
@pytest.mark.parametrize(
    "test_job",
    [
        (
            "t_value"
        ),  # test for the t-value used
        (
            "names"
        ),  # test the names option
        (
            "clas"
        ),  # test for clasification        
        (
            "csv_test"
        ),  # test for external test set
        (
            "standard"
        ),  # standard test
    ],
)
def test_PREDICT(test_job):

    # leave the folders as they were initially to run a different batch of tests
    if os.path.exists(f"{path_predict}"):
        shutil.rmtree(f"{path_predict}")
        # remove DAT and CSV files generated by PREDICT
        dat_files = glob.glob("*.dat")
        for dat_file in dat_files:
            if "PREDICT" in dat_file:
                os.remove(dat_file)

    if test_job == 'clas': # rename folders to use in classification
        # rename the regression GENERATE folder
        filepath_reg = Path(f"{path_main}/GENERATE")
        filepath_reg.rename(f"{path_main}/GENERATE_reg")
        # rename the classification GENERATE folder
        filepath = Path(f"{path_main}/GENERATE_clas")
        filepath.rename(f"{path_main}/GENERATE")

    else: # in case the clas test fails and the ending rename doesn't happen
        if os.path.exists(f"{path_main}/GENERATE_reg"):
            # rename the classification GENERATE folder
            filepath = Path(f"{path_main}/GENERATE")
            filepath.rename(f"{path_main}/GENERATE_clas")
            # rename the regression GENERATE folder
            filepath_reg = Path(f"{path_main}/GENERATE_reg")
            filepath_reg.rename(f"{path_main}/GENERATE")

    # runs the program with the different tests
    cmd_robert = [
        "python",
        "-m",
        "robert",
        "--predict",
    ]

    if test_job == "t_value":
        cmd_robert = cmd_robert + ["--t_value", "4"]
    if test_job == "names":
        cmd_robert = cmd_robert + ["--names", "Name"]
    if test_job == "csv_test":
        cmd_robert = cmd_robert + ["--csv_test", "tests/Robert_example_test.csv"]

    subprocess.run(cmd_robert)

    # check that the DAT file is created
    assert not os.path.exists(f"{path_main}/PREDICT_data.dat")
    outfile = open(f"{path_predict}/PREDICT_data.dat", "r")
    outlines = outfile.readlines()
    outfile.close()
    assert "ROBERT v" in outlines[0]
    categor_test = False
    for i,line in enumerate(outlines):
        if 'Results saved in' in line and 'No_PFI.dat' in line:
            if test_job not in ["csv_test"]:
                assert 'Points Train:Validation = ' in outlines[i+1]
            else:
                assert 'Points Train:Validation:Test = ' in outlines[i+1]
        elif 'x  There are missing descriptors' in line:
            categor_test = True
        if 'Outlier values saved in' in line and 'No_PFI' in line:
            if test_job == "names":
                assert '-  21 (' in outlines[i+2]
                break
            elif test_job != "clas":
                assert 'x  No names option' in outlines[i+1]             
                if test_job == "t_value":
                    assert 'Train: 0 outliers' in outlines[i+2]
                else:
                    assert 'Train: 1 outliers' in outlines[i+2]
                if test_job == "t_value":
                    assert 'Validation: 0 outliers' in outlines[i+3]
                else:
                    assert 'Validation: 0 outliers' in outlines[i+3]
                if test_job == "csv_test":
                    assert 'Test: 0 outliers' in outlines[i+4]
                break
    if test_job == "csv_test":
        assert categor_test

    # check that all the plots, CSV and DAT files are created
    assert len(glob.glob(f'{path_predict}/*.png')) == 8
    if test_job == "clas":
        assert len(glob.glob(f'{path_predict}/*.dat')) == 7
    else:
        assert len(glob.glob(f'{path_predict}/*.dat')) == 9
    if test_job == "csv_test":
        assert len(glob.glob(f'{path_predict}/*.csv')) == 6
    else:
        assert len(glob.glob(f'{path_predict}/*.csv')) == 4

    if test_job == 'clas': # rename folders back to their original names
        # rename the classification GENERATE folder
        filepath = Path(f"{path_main}/GENERATE")
        filepath.rename(f"{path_main}/GENERATE_clas")
        # rename the regression GENERATE folder
        filepath_reg = Path(f"{path_main}/GENERATE_reg")
        filepath_reg.rename(f"{path_main}/GENERATE")
