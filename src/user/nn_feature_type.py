import numpy as np
from utils.json_operation import get_parameter, get_required_parameter

class Descriptor(object):
    def __init__(self, json_input:dict, model_type:str, cmd:str) -> None:
        self.model_type = model_type
        self.cmd = cmd

        self.supported_feature_group = [[1, 2], [3, 4], [5], [6], [7], [8]]
        self.Rmax = get_parameter("Rmax", json_input, 6.0)
        self.Rmin = get_parameter("Rmin", json_input, 0.5)
        self.M2 = get_parameter("M2", json_input, 16)
        self.E_tolerance = get_parameter("E_tolerance", json_input, 9999999.99)
        self.feature_type = [int(_) for _ in get_parameter("feature_type", json_input, [3,4])]

        self.network_size = get_parameter("network_size", json_input, [25, 25, 25])
        self.bias = get_parameter("bias", json_input, True)
        self.resnet_dt = get_parameter("resnet_dt", json_input, True) # resnet in embedding net is true.
        self.activation = get_parameter("activation", json_input, "tanh")

        if self.feature_type not in self.supported_feature_group:
            raise Exception("the input feature type group {} is not support, \
                            we currently support the following combinations:\n {}".format(self.feature_type, self.supported_feature_group))
        self.feature_dict = {}
        for ftype in self.feature_type:
            ftype = "{}".format(ftype)
            ftype_dict = get_parameter("{}".format(ftype), json_input, {})
            # self.feature_dict[ftype] = getattr(self, "set_ftype{}_para".format(ftype), ftype_dict)
            if '1' == ftype:
                self.feature_dict[ftype] = self.set_ftype1_para(ftype_dict)
            elif '2' == ftype:
                self.feature_dict[ftype] = self.set_ftype2_para(ftype_dict)
            elif '3' == ftype:
                self.feature_dict[ftype] = self.set_ftype3_para(ftype_dict)
            elif '4' == ftype:
                self.feature_dict[ftype] = self.set_ftype4_para(ftype_dict)
            elif '5' == ftype:
                self.feature_dict[ftype] = self.set_ftype5_para(ftype_dict)
            elif '6' == ftype:
                self.feature_dict[ftype] = self.set_ftype6_para(ftype_dict)
            elif '7' == ftype:
                self.feature_dict[ftype] = self.set_ftype7_para(ftype_dict)
            elif '8' == ftype:
                self.feature_dict[ftype] = self.set_ftype8_para(ftype_dict)

    def set_ftype1_para(self, ftype_dict:dict):
        numOf2bfeat = get_parameter("numOf2bfeat", ftype_dict, 24)
        iflag_grid = get_parameter("iflag_grid", ftype_dict, 3)
        fact_base = get_parameter("fact_base", ftype_dict, 0.2)
        dR1 = get_parameter("dR1", ftype_dict, 0.5)
        iflag_ftype = get_parameter("iflag_ftype", ftype_dict, 3)
        return {
            "numOf2bfeat":[numOf2bfeat for tmp in range(10)],
            "Rc": [self.Rmax for tmp in range(10)],
            "Rm": [self.Rmin for tmp in range(10)],
            "iflag_grid": [iflag_grid for tmp in range(10)],   # 1 or 2 or 3
            "fact_base": [fact_base for tmp in range(10)],
            "dR1": [dR1 for tmp in range(10)],
            "iflag_ftype": iflag_ftype  
        }

    def set_ftype2_para(self, ftype_dict:dict):
        numOf3bfeat1 = get_parameter("numOf3bfeat1", ftype_dict, 3)
        numOf3bfeat2 = get_parameter("numOf3bfeat2", ftype_dict, 3)
        iflag_grid = get_parameter("iflag_grid", ftype_dict, 3)
        fact_base = get_parameter("fact_base", ftype_dict, 0.2)
        dR1 = get_parameter("dR1", ftype_dict, 0.5)
        dR2 = get_parameter("dR2", ftype_dict, 0.5)
        iflag_ftype = get_parameter("iflag_ftype", ftype_dict, 3)

        return {
            "numOf3bfeat1":[numOf3bfeat1 for tmp in range(10)],
            "numOf3bfeat2":[numOf3bfeat2 for tmp in range(10)],
            "Rc":[self.Rmax for tmp in range(10)],
            "Rc2":[self.Rmax for tmp in range(10)],
            "Rm":[self.Rmin for tmp in range(10)],
            "iflag_grid":[iflag_grid for tmp in range(10)],    # 1 or 2 or 3
            "fact_base":[fact_base for tmp in range(10)],
            "dR1":[dR1 for tmp in range(10)],
            "dR2":[dR2 for tmp in range(10)],
            "iflag_ftype":iflag_ftype   # same value for different types, iflag_ftype:1,2,3 when 3, iflag_grid must be 3
        }

    def set_ftype3_para(self, ftype_dict:dict):
        n2b = get_parameter("n2b", ftype_dict, 6)
        w = get_parameter("w", ftype_dict, [1.0, 1.5, 2.0])

        return {
            "Rc":[self.Rmax for tmp in range(10)],     # 5.4 number of elements in Rc = num atom type
            "n2b":[n2b for tmp in range(10)],       # 6 number of elements in n2b = num atom type
            "w": w #[1.0, 1.5, 2.0],
        }
        # 1/w^2 is the \eta in formula, and w is the width of gaussian fuction

    def set_ftype4_para(self, ftype_dict:dict):
        n3b = get_parameter("n3b", ftype_dict, 20)
        zeta = get_parameter("zeta", ftype_dict, 2.0)
        w = get_parameter("w", ftype_dict, [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
        
        return {
            "Rc":[self.Rmax for tmp in range(10)],     # 5.4 number of elements in Rc = num atom type
            "n3b":[n3b for tmp in range(10)],   # 20
            # n3b must be less than n_zeta * n_w * n_lambda, by default, n3b < 7*10*2=126
            # it is better if n3b is divisible by (n_w*2)
            "zeta": [ (zeta ** np.array(range(20))).tolist() for tmp in range(10)],  #2.0 feature changed
            "w":    [ w for tmp in range(10)],  # [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0] feature changed
            # 1/w^2 is the \eta in formula, and w is the width of gaussian fuction
            # 'lambda':[ [1.0,-1.0] for tmp in range(10)], # lambda === [1.0, -1.0]
        }
        # 1/w^2 is the \eta in formula, and w is the width of gaussian fuction

    def set_ftype5_para(self, ftype_dict:dict):
        n_MTP_line = get_parameter("n_MTP_line", ftype_dict, 5)

        return {
            "Rc":[self.Rmax for tmp in range(10)],     # number of elements in Rc = num atom type
            "Rm":[self.Rmin  for tmp in range(10)],     # number of elements in Rc = num atom type
            "n_MTP_line": [n_MTP_line for tmp in range(10)], # 5~14
            
            "tensors":[
                        [
                        '1, 4, 0, ( )                              ',
                        '2, 3,3, 0,0, ( ), ( )                     ',
                        '2, 3,3, 1,1, ( 21 ), ( 11 )               ',
                        '2, 3,3, 2,2, ( 21, 22 ), ( 11, 12 )       ',
                        '3, 2,2,2, 2,1,1 ( 21, 31 ), ( 11 ), ( 12 )',
                        '3, 3,3,3, 2,1,1 ( 21, 31 ), ( 11 ), ( 12 )',
                        '3, 2,2,2, 3,2,1 ( 21, 22, 31 ), ( 11, 12 ), ( 13 )',
                        '3, 3,3,3, 3,2,1 ( 21, 22, 31 ), ( 11, 12 ), ( 13 )',
                        '3, 2,2,2, 4,2,2 ( 21, 22, 31, 32 ), ( 11, 12 ), ( 13, 14 )',
                        '3, 3,3,3, 4,2,2 ( 21, 22, 31, 32 ), ( 11, 12 ), ( 13, 14 )',
                        '4, 2,2,2,2 3,1,1,1 ( 21, 31, 41 ), ( 11 ), ( 12 ), ( 13 )',
                        '4, 3,3,3,3 3,1,1,1 ( 21, 31, 41 ), ( 11 ), ( 12 ), ( 13 )',
                        '4, 2,2,2,2 4,2,1,1 ( 21, 22, 31, 41 ), ( 11, 12 ), ( 13 ), ( 14 )',
                        '4, 3,3,3,3 4,2,1,1 ( 21, 22, 31, 41 ), ( 11, 12 ), ( 13 ), ( 14 )',
                        ] for tmp in range(10)
                    ],
            }

    def set_ftype6_para(self, ftype_dict:dict):
        J = get_parameter("J", ftype_dict, 3.0)
        n_w_line = get_parameter("n_w_line", ftype_dict, 2)
        w1 = get_parameter("w1", ftype_dict, [0.9, 0.1, 0.8, 0.2, 0.7, 0.3, 0.6, 0.4])
        w2 = get_parameter("w2", ftype_dict, [0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.3, 0.6])
        
        return {
            'Rc':[self.Rmax for tmp in range(10)],     # number of elements in Rc = num atom type
            'J' :[J for tmp in range(10)],  #3.0
            'n_w_line': [n_w_line for tmp in range(10)],#2
            'w1':[ w1 for tmp in range(10)],  # shape(w1) = (ntype, n_w_line) [0.9, 0.1, 0.8, 0.2, 0.7, 0.3, 0.6, 0.4]
            'w2':[ w2 for tmp in range(10) ], # [0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.3, 0.6] 
        }

    def set_ftype7_para(self, ftype_dict:dict):
        M = get_parameter("M", ftype_dict, 25)
        M2 = get_parameter("M2", ftype_dict, 4)
        weight_r = get_parameter("weight_r", ftype_dict, 1.0)
        
        return {
            'Rc':[self.Rmax  for tmp in range(10)],     # number of elements in Rc = num atom type
            'Rc2':[self.Rmin  for tmp in range(10)],
            'Rm':[1.0 for tmp in range(10)],    #Chebyshev param , not rmin
            'M': [M for tmp in range(10)],#25
            'M2': [M2  for tmp in range(10)],#4
            'weight_r': [weight_r  for tmp in range(10)], #1.0
        }

    def set_ftype8_para(self, ftype_dict:dict):
        M = get_parameter("M", ftype_dict, 8)
        weight_r = get_parameter("weight_r", ftype_dict, 1.0)
        w = get_parameter("w", ftype_dict, [1.0, 1.5, 2.0, 2.5 ] )
        return {
            'Rc':[self.Rmax for tmp in range(10)],     # number of elements in Rc = num atom type
            'M':[M for tmp in range(10)], # 8
            'weight_r':[weight_r for tmp in range(10)], #1.0
            'w':[1.0, 1.5, 2.0, 2.5 ]
        }
    
    def to_dict(self):
        dicts = {}
        dicts["Rmax"] = self.Rmax
        dicts["Rmin"] = self.Rmin
        dicts["M2"] = self.M2
        dicts["E_tolerance"] = self.E_tolerance

        if self.model_type == "DP".upper():
            dicts["network_size"] = self.network_size
            dicts["bias"] = self.bias
            dicts["resnet_dt"] = self. resnet_dt 
            dicts["activation"] = self.activation

        elif self.model_type == "NN".upper():
            dicts["feature_type"] = self.feature_type
            # for feature in self.feature_type:
            #     feature = "{}".format(feature)
            #     dicts[feature] = self.feature_dict[feature]
        elif self.model_type == "Linear".upper():
            dicts["feature_type"] = self.feature_type
            
        else:
            raise Exception("descriptor to dict: the model type not realized:{}".format(self.model_type))
        
        return dicts