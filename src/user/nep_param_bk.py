import os
from utils.atom_type_emb_dict import element_table
from utils.json_operation import get_parameter
'''
description: 
 this NEP params default value is the same as 
    https://gpumd.org/nep/input_files/nep_in.html#nep-in

return {*}
author: wuxingxing
'''
class NepParam(object):
    '''
    description: 
        if nep.in file provided by user, prioritize using it
        elif nep.in file not exisited, use params set in user input json file
        else use default params
    param {*} self
    param {*} nep_dict
    param {str} nep_in_file
    param {list} type_list
    param {list} type_list_weight
    param {str} nep_save_file
    return {*}
    author: wuxingxing
    '''    
    def __init__(self, json_dict, nep_in_file, type_list:list[int]=[]) -> None:
        nep_dict = get_parameter("descriptor", json_dict, {})
        nep_file_dict = {}
        self.nep_in_file = nep_in_file
        if nep_in_file is not None:
            if not os.path.exists(nep_in_file):
                raise Exception("ERROR! the nep.in file is not exist, please check the file: {}".format(nep_in_file))
            nep_file_dict = self.read_nep_param_from_nep_file(nep_in_file)
            
        self.version = self.get_parameter("version", nep_dict, 4, nep_file_dict, 0) # select between NEP2, NEP3, and NEP4
        type_str = self.set_atom_type(type_list)
        self.type = self.get_parameter("type", nep_dict, type_str, nep_file_dict, 4) # number of atom types and list of chemical species
        self.type_num = len(self.type.split()[1:])
        type_list_weight_default = [1.0 for _ in range(0, self.type_num)]
        self.type_weight = self.get_parameter("type_weight", nep_dict, type_list_weight_default, nep_file_dict, 3) # force weights for different atom types
        self.model_type = self.get_parameter("model_type", nep_dict, 0, nep_file_dict, 0) # select to train potential 0, dipole 1, or polarizability 2
        self.prediction = self.get_parameter("prediction", nep_dict, 0, nep_file_dict, 0) # select between training and prediction (inference)
        self.zbl = self.get_parameter("zbl", nep_dict, None, nep_file_dict, 1) # outer cutoff for the universal ZBL potential [Ziegler1985]
        self.cutoff = self.get_parameter("cutoff", nep_dict, [8, 6], nep_file_dict, 2) # radial () and angular () cutoffs # use dp rcut, default to 6
        self.n_max = self.get_parameter("n_max", nep_dict, [4, 4], nep_file_dict, 2) # size of radial () and angular () basis
        if len(self.n_max) != 2:
            raise Exception("the input 'n_max' should has 2 values, such as [4, 4]")
        self.basis_size = self.get_parameter("basis_size", nep_dict, [12, 12], nep_file_dict, 2) # number of radial () and angular () basis functions
        if len(self.basis_size) != 2:
            raise Exception("the input 'basis_size' should has 2 values, such as [12, 12]")
        self.l_max = self.get_parameter("l_max", nep_dict, [4, 2, 0], nep_file_dict, 2) # expansion order for angular terms
        if len(self.l_max) != 3 or (self.l_max[0] != 4) or (self.l_max[1] != 2) or (self.l_max[2] > 1) :
            error_log = "the input 'l_max' should has 3 values. The values should be [4, 2, 0] or [4, 2, 1]. The last num '1', means use 5 body features.\n"
            raise Exception(error_log)
        if self.l_max[2] != 0 and self.l_max[2] != 1:
            error_log = "the input 'l_max' should has 3 values. The values should be [4, 2, 0] or [4, 2, 1]. The last num '1', means use 5 body features, '0' means not use 5 body features\n"
            raise Exception(error_log)
        self.neuron = self.get_parameter("neuron", nep_dict, 100, nep_file_dict, 0) # number of neurons in the hidden layer
        
        lambda_1 = self.get_parameter("lambda_1", nep_dict, -1, nep_file_dict, 1) # weight of regularization term
        if lambda_1 != -1 and lambda_1 < 0:
            raise Exception("ERROR! the lambda_1 should >= 0 or lambda_1 = -1 for automatically determined in training!")
        else:
            self.lambda_1 = lambda_1

        lambda_2 = self.get_parameter("lambda_2", nep_dict, -1, nep_file_dict, 1) # weight of norm regularization term
        if lambda_2 != -1 and lambda_2 < 0:
            raise Exception("ERROR! the lambda_2 should >= 0 or lambda_2 = -1 for automatically determined in training!")
        else:
            self.lambda_2 = lambda_2

        self.lambda_ei = self.get_parameter("lambda_ei", nep_dict, 1.0, nep_file_dict, 1) # weight of energy loss term
        self.lambda_eg = self.get_parameter("lambda_eg", nep_dict, 0.1, nep_file_dict, 1) # weight of energy loss term
        self.lambda_e = self.get_parameter("lambda_e", nep_dict, 1.0, nep_file_dict, 1) # weight of energy loss term
        self.lambda_f = self.get_parameter("lambda_f", nep_dict, 1.0, nep_file_dict, 1) # weight of force loss term
        self.lambda_v = self.get_parameter("lambda_v", nep_dict, 0.1, nep_file_dict, 1) # weight of virial loss term
        self.force_delta = self.get_parameter("force_delta", nep_dict, None, nep_file_dict, 1) # bias term that can be used to make smaller forces more accurate
        self.batch = self.get_parameter("batch", nep_dict, 1000, nep_file_dict, 0) # batch size for training
        self.population = self.get_parameter("population", nep_dict, 50, nep_file_dict, 0) # population size used in the SNES algorithm [Schaul2011]
        self.generation = self.get_parameter("generation", nep_dict, 100000, nep_file_dict, 0) # number of generations used by the SNES algorithm [Schaul2011]
        
        self.set_feature_params()
    
    def set_feature_params(self):
        # features
        self.two_feat_num = self.n_max[0]+1
        self.three_feat_num = (self.n_max[1]+1)*self.l_max[0] 
        self.four_feat_num = (self.n_max[1]+1) if (len(self.l_max) >= 2) else 0
        self.five_feat_num = (self.n_max[1]+1) if len(self.l_max) == 3 else 0
        self.feature_nums = self.two_feat_num + self.three_feat_num + self.four_feat_num + self.five_feat_num
        # c params, the 4-body and 5-body use the same c param of 3-body, their N_base_a the same
        self.two_c_num = self.type_num*self.type_num*(self.n_max[0]+1)*(self.basis_size[0]+1)
        self.three_c_num = self.type_num*self.type_num*(self.n_max[1]+1)*(self.basis_size[1]+1)
        self.c_num = self.two_c_num + self.three_c_num

        self.c2_param = None
        self.c3_param = None
        self.q_scaler = None
        self.model_wb = None

    '''
    read params from nep.txt
    description: 
    param {*} self
    param {*} file_path
    return {*}
    author: wuxingxing
    '''    
    def set_params_from_neptxt(self, file_path="nep.txt"):
        # self.c2_param = None
        # self.c3_param = None
        # self.q_scaler = None
        # self.model_wb = None
        pass
    
    def read_nep_param_from_nep_file(self, nep_in_file:str):
        with open(nep_in_file, 'r') as rf:
            lines = rf.readlines()
        nep_dict = {}
        for line in lines:
            substring = line.split("#")[0].strip()
            if len(substring.split()) > 1:
                key = substring.split()[0]
                value_str = substring.replace(key, "")
                nep_dict[key.lower()] = value_str.strip()
        return nep_dict

    def to_nep_in_file(self, file_path:str):
        with open(file_path, 'w') as wf:
            self._write_to_line(wf, "version", self.version)
            self._write_to_line(wf, "type", self.type_num)
            self._write_to_line(wf, "type_weight", self.type_weight, True)
            self._write_to_line(wf, "model_type", self.model_type)
            self._write_to_line(wf, "prediction", self.prediction)
            self._write_to_line(wf, "zbl", self.zbl)
            self._write_to_line(wf, "cutoff", self.cutoff, True)
            self._write_to_line(wf, "n_max", self.n_max, True)
            self._write_to_line(wf, "basis_size", self.basis_size, True)
            self._write_to_line(wf, "l_max", self.l_max, True)
            self._write_to_line(wf, "neuron", self.neuron)
            if self.lambda_1 != -1:
                self._write_to_line(wf, "lambda_1", self.lambda_1) # it will be automatically determined if -1
            if self.lambda_2 != -1:
                self._write_to_line(wf, "lambda_2", self.lambda_2) # it will be automatically determined if -1
            self._write_to_line(wf, "lambda_e", self.lambda_e)
            self._write_to_line(wf, "lambda_f", self.lambda_f)
            self._write_to_line(wf, "lambda_v", self.lambda_v)
            self._write_to_line(wf, "force_delta", self.force_delta)
            self._write_to_line(wf, "batch", self.batch)
            self._write_to_line(wf, "population", self.population)
            self._write_to_line(wf, "generation", self.generation)
        print("Successfully generated nep.in file.")

    '''
    description: 
    return line: "key value"
        example: "l_max         4 2 0"
    param {*} self
    param {*} wf
    param {*} key
    param {*} value
    param {str} data_type: int_value 0, float_value 1, int_list 2, float_list 3, str 4
    return {*}
    author: wuxingxing
    '''
    def _write_to_line(self, wf, key, value, is_list:bool = False):
        if value is None:
            return
        if is_list:
            value = " ".join(str(item) for item in value)
        line = "{} {}".format(key, value)
        wf.write(line)
        wf.write("\n")

    def to_dict(self):
        dicts = {}
        dicts["version"] = self.version
        dicts["type"] = self.type_num
        if self.type_weight is not None:
            dicts["type_weight"] = self.type_weight
        dicts["model_type"] = self.model_type
        dicts["prediction"] = self.prediction
        if self.zbl is not None:
            dicts["zbl"] = self.zbl
        dicts["cutoff"] = self.cutoff
        dicts["n_max"] = self.n_max
        dicts["basis_size"] = self.basis_size
        dicts["l_max"] = self.l_max
        dicts["neuron"] = self.neuron
        dicts["lambda_1"] = self.lambda_1
        dicts["lambda_2"] = self.lambda_2
        dicts["lambda_e"] = self.lambda_e
        dicts["lambda_f"] = self.lambda_f
        dicts["lambda_v"] = self.lambda_v
        if self.force_delta is not None:
            dicts["force_delta"] = self.force_delta
        dicts["batch"] = self.batch
        dicts["population"] = self.population
        dicts["generation"] = self.generation
        return dicts

    def to_txt(self):
        content = ""
        content += "version {}\n".format(self.version)
        content += "type {}\n".format(self.type_num)
        if self.type_weight is not None:
            content += "type_weight {}\n".format(self.type_weight)
        content += "model_type {}\n".format(self.model_type)
        content += "prediction {}\n".format(self.prediction)
        if self.zbl is not None:
            content += "zbl {}\n".format(self.zbl)
        content += "cutoff {}\n".format(self.cutoff)
        content += "n_max {}\n".format(self.n_max)
        content += "basis_size {}\n".format(self.basis_size)
        content += "l_max {}\n".format(self.l_max)
        content += "neuron {}\n".format(self.neuron)
        content += "lambda_1 {}\n".format(self.lambda_1)
        content += "lambda_2 {}\n".format(self.lambda_2)
        content += "lambda_e {}\n".format(self.lambda_e)
        content += "lambda_f {}\n".format(self.lambda_f)
        content += "lambda_v {}\n".format(self.lambda_v)
        if self.force_delta is not None:
            content += "force_delta {}\n".format(self.force_delta)
        content += "batch {}\n".format(self.batch)
        content += "population {}\n".format(self.population)
        content += "generation {}\n".format(self.generation)
        return content

    '''
    description: 
        if the value is boath in nep.in file and user input json file, the nep.in value will be used
    param {str} param
    param {dict} json_input
    param {*} default_value
    param {dict} nep_file_dict
    param {str} data_type: int_value 0, float_value 1, int_list 2, float_list 3, string 4
    return {*}
    author: wuxingxing
    '''
    def get_parameter(self, param:str, json_input:dict, default_value, nep_file_dict:dict={}, data_type:int=4):
        if param.lower() in nep_file_dict.keys():
            if data_type == 0:
                return int(nep_file_dict[param])
            elif data_type == 1:
                return float(nep_file_dict[param])
            elif data_type == 2:
                return [int(_) for _ in nep_file_dict[param].split()]
            elif data_type == 3:
                return [float(_) for _ in nep_file_dict[param].split()]
            else:
                return nep_file_dict[param]
            
        if param not in json_input.keys():
            return default_value
        else:
            return json_input[param]
    
    '''
    description: 
        the format of type in nep.in file is as:
            "type 2 Te Pb # this is a mandatory keyword"
    param {*} self
    param {*} atom_type_list
    return {*}
    author: wuxingxing
    '''    
    def set_atom_type(self, atom_type_list):
        atom_names = []
        for atom in atom_type_list:
            atom_names.append(element_table[atom])
        return str(len(atom_type_list)) + " " + " ".join(atom_names)