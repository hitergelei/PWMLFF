import os
import shutil
from src.user.model_param import DpParam
import torch
import numpy as np
import src.aux.extract_ff as extract_ff
from src.user.model_param import DpParam
def extract_force_field():
    pass

'''
description: 
    extracting network parameters and scaler values for fortran MD routine
param {DpParam} dp_params
param {*} model_name
return {*}
author: wuxingxing
'''
def extract_model_para(dp_params:DpParam):
    from src.aux.extract_nn import read_wij, read_scaler 

    load_model_path = dp_params.file_paths.model_save_path
    # extracting Wij values from model.ckpt
    read_wij(load_model_path, ntype=len(dp_params.atom_type))

    # extracting scaler values from model.ckpt
    read_scaler(load_model_path, ntype=len(dp_params.atom_type))

def extract_force_field(dp_params:DpParam):
    forcefield_dir = dp_params.file_paths.forcefield_dir
    if os.path.exists(forcefield_dir):
        shutil.rmtree(forcefield_dir)
    os.makedirs(forcefield_dir)
    cwd = os.getcwd()
    os.chdir(forcefield_dir)

    extract_dreat_input(dp_params.file_paths.model_save_path, forcefield_dir)

    from src.aux.extract_ff import extract_ff
    extract_model_para(dp_params)
    extract_ff(ff_name = dp_params.file_paths.forcefield_name, model_type = 3)
    os.chdir(cwd)

def load_scaler_from_checkpoint(model_path):
    model_checkpoint = torch.load(model_path,map_location=torch.device("cpu"))
    scaler = model_checkpoint['scaler']
    return scaler

# scaler_path = self.dp_params.file_paths.model_store_dir + 'scaler.pkl'
#             print("loading scaler from file",scaler_path)
#             self.scaler = load(scaler_path)
#             print("transforming feat with loaded scaler")

'''
description: 
load dfread_dfeat files and input files, they will be saved in model.ckpt file, and used for extracting forcefiled file.
param {*} dfread_dfeat_path
param {*} input_path
return {*}
author: wuxingxing
'''
def load_dfeat_input(dfread_dfeat_path, input_path):
    dicts = {}
    dicts["dfread_dfeat"] = {}
    dicts["input"] = {}

    dfread_paths = os.listdir(dfread_dfeat_path)
    for feat in dfread_paths:
        with open(os.path.join(dfread_dfeat_path, feat), 'rb') as file:
            file_content = file.read()
            dicts["dfread_dfeat"][feat] = file_content

    input_paths = os.listdir(input_path)
    for input in input_paths:
        with open(os.path.join(input_path, input), 'rb') as file:
            file_content = file.read()
            dicts["input"][input] = file_content

    return dicts

'''
description: 
extract dfread_dfeat files and input files from model.ckpt file and save the to forcefield dir
param {*} ckpt_file
param {*} forcefield_dir
return {*}
author: wuxingxing
'''
def extract_dreat_input(ckpt_file, forcefield_dir):
    model_ckpt = torch.load(ckpt_file,map_location=torch.device("cpu"))

    dfread_dfeat = model_ckpt["dfread_dfeat_input"]["dfread_dfeat"]
    fread_dfeat_dir = os.path.join(forcefield_dir, "fread_dfeat")
    if os.path.exists(fread_dfeat_dir) is False:
        os.makedirs(fread_dfeat_dir)
    for key in dfread_dfeat.keys():
        file_content = dfread_dfeat[key]
        with open(os.path.join(fread_dfeat_dir, key), 'wb') as wf:
            wf.write(file_content)

    input = model_ckpt["dfread_dfeat_input"]["input"]
    input_dir = os.path.join(forcefield_dir, "input")
    if os.path.exists(input_dir) is False:
        os.makedirs(input_dir)
    for key in input.keys():
        file_content = input[key]
        with open(os.path.join(input_dir, key), 'wb') as wf:
            wf.write(file_content)
