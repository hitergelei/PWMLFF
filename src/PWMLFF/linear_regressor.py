"""
    module for linear regressor 
"""
import os,sys
import pathlib

codepath = str(pathlib.Path(__file__).parent.resolve())

#for model.mlff 
sys.path.append(codepath+'/../model')

#for default_para, data_loader_2type dfeat_sparse
sys.path.append(codepath+'/../pre_data')

#for optimizer
sys.path.append(codepath+'/..')
sys.path.append(codepath+'/../aux')
sys.path.append(codepath+'/../lib')
sys.path.append(codepath+'/../..')

import default_para as pm
import fortran_fitting as ff 


class linear_regressor:
    
    def __init__(   
                    self,
                    atom_type = None, 
                    feature_type = None,
                    max_neigh_num = 100, 
                    
                    etot_weight = 0.5, 
                    force_weight = 0.5,
                    ei_weight = 0.5, 
                ):
        
        if atom_type == None:
            raise Exception("atom types not specifed")
        
        if feature_type is None:
            raise Exception("feature type not specified")

        pm.atomType = atom_type 

        pm.use_Ftype = feature_type 
        pm.nfeat_type = len(pm.use_Ftype)

        pm.atomTypeNum = len(pm.atomType)       
        pm.ntypes = len(pm.atomType)

        pm.maxNeighborNum = max_neigh_num 
        
        # weights for regression 
        pm.fortranFitWeightOfEtot = etot_weight
        pm.fortranFitWeightOfForce = force_weight
        pm.fortranFitWeightOfEnergy = ei_weight

    def generate_data(self):

        import subprocess
        # clean old .dat files otherwise will be appended 
        if os.path.exists("PWdata/MOVEMENTall"):
            print ("cleaning old data")
            subprocess.run([
                "rm -rf fread_dfeat output input train_data plot_data PWdata/*.txt PWdata/trainData.* PWdata/location PWdata/Egroup_weight PWdata/MOVEMENTall"
                ],shell=True)
            subprocess.run(["find PWdata/ -name 'dfeat*' | xargs rm -rf"],shell=True)
            subprocess.run(["find PWdata/ -name 'info*' | xargs rm -rf"],shell=True)
            
        print("data generation starts")
        # calculate features
        pm.isCalcFeat = True 
        import mlff 
        pm.isCalcFeat = False

    def train(self):
        print ("training starts")
        
        pm.isFitLinModel = True     

        #pp.prepare_dir_info()   

        #os.system('cp '+pm.fbinListPath+' ./input/')
        #pp.writeGenFeatInput()
        #pp.collectAllSourceFiles()

        #pp.prepare_novdw()

        ff.fit() 

        pm.isFitLinModel = False 
        """
        pm.isFitLinModel = True    
        import mlff
        pm.isFitLinModel = False 
        """
    
    def set_etot_weight(self,val):
        pm.fortranFitWeightOfEtot = val 
    
    def set_ei_weight(self,val):
        pm.fortranFitWeightOfEnergy = val
    
    def set_force_weight(self,val):
        pm.fortranFitWeightOfForce = val
    
    
    
    def evaluate(self, num_thread = 1):
        """
            evaluate a model w.r.t AIMD
            put a MOVEMENT in /MD and run MD100 
        """
        
        if not os.path.exists("MD/MOVEMENT"):
            raise Exception("MD/MOVEMENT not found. It should be an Ab Initio MD result")
        if os.path.exists("MOVEMENT"):
            os.remove("MOVEMENT")        
        import md100    
        md100.run_md100(imodel = 1, atom_type = pm.atomType, num_process = num_thread)


    def plot_evaluation(self, plot_elem, save_data):
        
        if not os.path.exists("MOVEMENT"):
            raise Exception("MOVEMENT not found. It should be force field MD result")

        import plot_evaluation

        if pm.fortranFitWeightOfEnergy == 0:
            plot_ei = False
        else:
            plot_ei = True
            
        plot_evaluation.plot_new(atom_type = pm.atomType, plot_elem = plot_elem, save_data = save_data, plot_ei = plot_ei)

    def extract_force_field(self, name= "myforcefield.ff"):

        from extract_ff import extract_ff
        extract_ff(name = name, model_type = 1, atom_type = pm.atomType)
        
    def run_md(self, init_config = "atom.config", md_details = None, num_thread = 1, follow = False):

        import subprocess 
        from poscar2lammps import idx2mass
        
        # remove existing MOVEMENT file for not 
        if follow == False:
            os.system('rm -f MOVEMENT')     
        
        if md_details is None:
            raise Exception("md detail is missing")
        
        md_detail_line = str(md_details)[1:-1]+"\n"
        
        if os.path.exists(init_config) is not True: 
            raise Exception("initial config for MD is not found")
        
        # preparing md.input 
        idx_tabel = idx2mass()
        mass_type = []
        for idx in pm.atomType:
            if idx in idx_tabel:
                mass_type.append(idx_tabel[idx])
                
        f = open('md.input', 'w')
        f.write(init_config+"\n")

        f.write(md_detail_line) 
        f.write('F\n')
        f.write("1\n")     # imodel=1,2,3.    {1:linear;  2:VV;   3:NN;}
        f.write('1\n')               # interval for MOVEMENT output
        f.write('%d\n' % len(pm.atomType)) 
        
        for i in range(len(pm.atomType)):
            f.write('%d %.3f\n' % (pm.atomType[i], mass_type[i]))
        f.close()    
        
        # creating md.input for main_MD.x 
        command = r'mpirun -n ' + str(num_thread) + r' main_MD.x'
        print (command)
        subprocess.run(command, shell=True) 

    """
        ============================================================
        ===================auxiliary functions======================
        ============================================================ 
    """

    def set_max_neigh_num(self,val):
        pm.maxNeighborNum = val
    
    def set_etot_weight(self,val):
        pm.fortranFitWeightOfEtot = val 
    
    def set_force_weight(self,val):
        pm.fortranFitWeightOfForce = val
    
    def set_ei_weight(self,val):
        pm.fortranFitWeightOfEnergy = val 


        
"""
if __name__ == "__main__":

    atom_type = [29,8]
    feature_type = [1,2] 

    linReg = linear_regressor(atom_type = atom_type, feature_type = feature_type)
    
    #linReg.generate_data() 
    
    #linReg.train() 

    md_detail = [1,1000,1,500,500]
    
    kfnn_trainer.run_md(md_details = md_detail, num_thread = 12, follow = False) 
"""

