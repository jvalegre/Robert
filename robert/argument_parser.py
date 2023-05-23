#####################################################.
#      This file contains the argument parser       #
#####################################################.

var_dict = {
    "varfile": None,
    "command_line": False,
    "curate": False,
    "generate": False,
    "predict": False,
    "verify": False,
    "aqme": False,
    "report": False,
    "cheers": False,
    "seed": 8,
    "destination": None,
    "csv_name" : '',
    "y" : '',
    "discard" : [],
    "ignore" : [],
    "categorical" : "onehot",
    "corr_filter" : True,
    "thres_y" : 0.02,
    "thres_x" : 0.85,
    "train" : [60,70,80,90],
    "split" : "KN",
    "model" : ['RF','GB','NN','MVL'],
    "custom_params" : None,
    "type" : "reg",
    "seed" : 0,
    "epochs" : 50,
    "error_type" : "rmse",
    "pfi_epochs" : 30,
    "pfi_threshold" : 0.04,
    "pfi_filter" : True,
    "pfi_max" : 0,
    "thres_test" : 0.2,
    "kfold" : 5,
    "params_dir" : '',
    "csv_test" : '',
    "t_value" : 2,
    "shap_show" : 10,
    "pfi_show" : 10,
    "names" : '',
    "qdescp_keywords" : '',
    "csearch_keywords": '--sample 100',
    "report_modules" : ['AQME','CURATE','GENERATE','VERIFY','PREDICT']
}

# part for using the options in a script or jupyter notebook
class options_add:
    pass


def set_options(kwargs):
    # set default options and options provided
    options = options_add()
    # dictionary containing default values for options

    for key in var_dict:
        vars(options)[key] = var_dict[key]
    for key in kwargs:
        if key in var_dict:
            vars(options)[key] = kwargs[key]
        elif key.lower() in var_dict:
            vars(options)[key.lower()] = kwargs[key.lower()]
        else:
            print("Warning! Option: [", key,":",kwargs[key],"] provided but no option exists, try the online documentation to see available options for each module.",)

    return options
