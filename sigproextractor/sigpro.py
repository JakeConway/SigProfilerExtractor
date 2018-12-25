#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 11:04:39 2018

@author: mishugeb
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 13:39:29 2018

@author: mishugeb
"""
import os
os.environ["MKL_NUM_THREADS"] = "1" 
os.environ["NUMEXPR_NUM_THREADS"] = "1" 
os.environ["OMP_NUM_THREADS"] = "1" 
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import scipy.io
import numpy as np
import pandas as pd
import time
from sigproextractor import subroutines as sub
from SigProfilerMatrixGenerator.scripts import SigProfilerMatrixGeneratorFunc as datadump   
import shutil
import multiprocessing as mp





def sigProfilerExtractor(input_type, out_put, project, refgen="GRCh37", startProcess=1, endProcess=10, totalIterations=8, cpu=-1, hierarchy = False, mtype = ["default"],exome = False, indel_extended = False): 
    
    ################################ take the inputs from the mandatory arguments ####################################
    input_type = input_type;
    out_put = out_put;  
    project = project
        
    
    ################################ take the inputs from the general optional arguments ####################################
    startProcess=startProcess ; 
    endProcess=endProcess;
    totalIterations=totalIterations
    cpu = cpu
    hierarchi = hierarchy
    
       
    if input_type=="text":
        
        ################################### For text input files ######################################################
        
        text_file = project
        title = "" # set the title for plotting 
            
    
            
        data = pd.read_csv(text_file, sep="\t").iloc[:,:]
        data=data.dropna(axis=1, inplace=False)
        genomes = data.iloc[:,1:]
        genomes = np.array(genomes)
        allgenomes = genomes.copy()  # save the allgenomes for the final results 
        
        #Contruct the indeces of the matrix
        #setting index and columns names of processAvg and exposureAvg
        index = data.iloc[:,0]
        colnames  = data.columns[1:]
        allcolnames = colnames.copy() # save the allcolnames for the final results
        
        #creating list of mutational type to sync with the vcf type input
        mtypes = [str(genomes.shape[0])]
        
    ###############################################################################################################
    
    ###########################################################################################################################################################################################
    elif input_type=="matobj":
        ################################# For matlab input files #######################################################
        
        mat_file = project
        title = "" # set the title for plotting 
        
            
        
        mat = scipy.io.loadmat(mat_file)
        mat = sub.extract_input(mat)
        genomes = mat[1]
        allgenomes = genomes.copy()  # save the allgenomes for the final results 
        
        
      
        
        #Contruct the indeces of the matrix
        #setting index and columns names of processAvg and exposureAvg
        index1 = mat[3]
        index2 = mat[4]
        index = []
        for i, j in zip(index1, index2):
            index.append(i[0]+"["+j+"]"+i[2])
        colnames = np.array(pd.Series(mat[2]))
        allcolnames = colnames.copy() # save the allcolnames for the final results
        index = np.array(pd.Series(index))
        
        #creating list of mutational type to sync with the vcf type input
        mtypes = [str(genomes.shape[0])]
        
        
        #################################################################################################################
        
        
        
    elif input_type=="vcf":
        ################################# For vcf input files #######################################################
        
        project = project
        title = project # set the title for plotting 
        
        refgen = refgen
        
        
        exome = exome
    
        
        indel_extended = indel_extended
    
        mtype = mtype     
        
        data = datadump.SigProfilerMatrixGeneratorFunc(project, refgen, project, exome=exome, indel_extended=indel_extended, bed_file=None, chrom_based=False, plot=False, gs=False)
        
        
        
    
        # Selecting the mutation types    
        mtype = mtype 
        if mtype != ["default"]:
            mkeys = data.keys()
            mtypes = mtypes
            if any(x not in mkeys for x in mtypes):
                 raise Exception("Please pass valid mutation types seperated by comma with no space. Carefully check (using SigProfilerMatrixGenerator)"\
                                 "what mutation contexts should be generated by your VCF files. Also please use the uppercase characters")
                
                 
        else:
            if set(["96", "DINUC", "INDEL"]).issubset(data):            
                mtypes = ["96", "DINUC", "INDEL"] 
            elif set(["96", "DINUC"]).issubset(data): 
                mtypes = ["96", "DINUC"]
            elif set(["INDEL"]).issubset(data):            
                mtypes = ["INDEL"] 
        #print (mtypes)
        #change working directory 
        
        
        
          
    ###########################################################################################################################################################################################                  
    for m in mtypes:
        
        # Determine the types of mutation which will be needed for exporting and copying the files
        if not (m=="DINUC"or m=="INDEL"):
            mutation_type = "SNV"
            
        else:
            mutation_type = m
        
        if input_type=="vcf":
            genomes = data[m]
            allgenomes = genomes.copy()  # save the allgenomes for the final results 
            index = genomes.index.values
            colnames  = genomes.columns
            allcolnames = colnames.copy() # save the allcolnames for the final results 
            
           
            
        #create output directories to store all the results 
        output = out_put+"/"+m
        
        
        
        
        est_genomes = np.zeros([1,1])
        listofsignatures=[]
        H_iteration = 1 
        flag = True # We need to enter into the first while loop regardless any condition
        # While loop starts here
        while flag:
            genomes = np.array(genomes)
            information =[] 
            if hierarchi is True:
                layer_directory = output+"/Analysis/L"+str(H_iteration)
            elif hierarchi is False:
                layer_directory = output
                
            try:
                if not os.path.exists(layer_directory):
                    os.makedirs(layer_directory)
                    #os.makedirs(output+"/pickle_objects")
                    #os.makedirs(output+"/All solutions")
                
             
            
        
                
            except: 
                print ("The {} folder could not be created".format("output"))
            
            
            fh = open(layer_directory+"/results_stat.csv", "w")   
            fh.write("Number of signature, Reconstruction Error, Process stability\n") 
            fh.close()
            # The following for loop operates to extract data from each number of signature
             
            for i in range(startProcess,endProcess+1):
                    
                processAvg, \
                exposureAvg, \
                processStd, \
                exposureStd, \
                avgSilhouetteCoefficients, \
                clusterSilhouetteCoefficients, \
                finalgenomeErrors, \
                finalgenomesReconstructed, \
                finalWall, \
                finalHall, \
                processes = sub.decipher_signatures(genomes= genomes, \
                                                    i = i, \
                                                    totalIterations=totalIterations, \
                                                    cpu=cpu, \
                                                    mut_context=m) 
                
                
                ####################################################################### add sparsity in the exposureAvg #################################################################
                
    
                # remove signatures only if the process stability is above a thresh-hold of 0.85
                if  avgSilhouetteCoefficients>0.85:   
                    stic = time.time() 
                    pool = mp.Pool()
                    results = [pool.apply_async(sub.remove_all_single_signatures_pool, args=(x,processAvg,exposureAvg,genomes,)) for x in range(genomes.shape[1])]
                    pooloutput = [p.get() for p in results]
                    #print(results)
                    pool.close()
                    
                    for i in range(len(pooloutput)):
                        #print(results[i])
                        exposureAvg[:,i]=pooloutput[i]
                    stoc = time.time()
                    print ("Optimization time is {} seconds".format(stoc-stic))    
                
                
                ##########################################################################################################################################################################
                # store the resutls of the loop            
                loopResults = [genomes, processAvg, exposureAvg, processStd, exposureStd, avgSilhouetteCoefficients, clusterSilhouetteCoefficients, finalgenomeErrors, finalgenomesReconstructed, finalWall, finalHall, processes]    
                information.append([processAvg, exposureAvg]) #Will be used during hierarchical approach
                
                ################################# Export the results ###########################################################    
                sub.export_information(loopResults, m, layer_directory, index, colnames)
                
                
                
            ################################################################################################################
            ########################################## Plot Stabiltity vs Reconstruction Error #############################        
            ################################################################################################################    
            # Print the Stabiltity vs Reconstruction Error as get the solution as well
            solution = sub.stabVsRError(layer_directory+"/results_stat.csv", layer_directory, title)
            #print ("The mutution type is %s"%(m)
            
            
            
        
            ################################### Hierarchical Extraction  #########################
            if hierarchi is True:
                
                if os.path.exists(layer_directory+"/Selected solution"):
                    shutil.rmtree(layer_directory+"/Selected solution") 
                # Copy the best solution the "selected solution" folder
                solutionFolderFrom= layer_directory+"/All solutions/"+str(solution)+" "+ mutation_type+ " Signature"
                solutionFolderTo = layer_directory+"/Selected solution/"+str(solution)+" "+ mutation_type+ " Signature"
                shutil.copytree(solutionFolderFrom, solutionFolderTo)
                
                # load the best processAvg and exposureAvg based on the solution
                processAvg = information[solution-startProcess][0]
                exposureAvg = information[solution-startProcess][1]
                #del information
                
                # Compute the estimated genome from the processAvg and exposureAvg
                est_genomes = np.dot(processAvg, exposureAvg) 
                
                # make the list of the samples which have similarity lower than the thresh-hold with the estimated ones
                low_similarity_idx = []
                for i in range(genomes.shape[1]):
                    similarity = sub.cos_sim(genomes[:,i], est_genomes[:,i])
                    #print (similarity)
                    # The tresh-hold for hierarchy is 0.95 for now
                    if similarity < 0.95:    
                        low_similarity_idx.append(i)
                
                
                if len(low_similarity_idx)==0:   
                    low_similarity_idx = []
                #print(low_similarity_idx)
                
                # Accumulated the signatures for the final results
                listofsignatures.append(processAvg) 
                
                genomes = genomes[:,low_similarity_idx]
                colnames=colnames[low_similarity_idx]
                H_iteration = H_iteration + 1
                
                #########################################################################################################
                # do the necessary operations and put the outputs in the "Final Solution" folder when the while loop ends
                if genomes.shape[1]<10 or est_genomes.shape[1]==genomes.shape[1]:
                    flag = False #update the flag for the whileloop
                    
                    # create the folder for the final solution/ De Novo Solution
                    layer_directory1 = output+"/Final Solution/De Novo Solution"
                    try:
                        if not os.path.exists(layer_directory1):
                            os.makedirs(layer_directory1)
                    except: 
                        print ("The {} folder could not be created".format("output"))
            
            
                    count = 0
                    for p in listofsignatures:
                        if count==0:
                            processAvg=p
                        else:
                            processAvg = np.hstack([processAvg, p]) 
                        count+=1
                        
                        
                    # make de novo solution(processAvg, allgenomes, layer_directory1)
                    listOfSignatures = sub.make_letter_ids(idlenth = processAvg.shape[1])
                    sub.make_final_solution(processAvg, allgenomes, listOfSignatures, layer_directory1, m, index, allcolnames)    
                    
                    
                    # create the folder for the final solution/ Decomposed Solution
                    layer_directory2 = output+"/Final Solution/Decomposed Solution"
                    try:
                        if not os.path.exists(layer_directory2):
                            os.makedirs(layer_directory2)
                    except: 
                        print ("The {} folder could not be created".format("output"))
            
                    
                    final_signatures = sub.signature_decomposition(processAvg, m, layer_directory2)                
                    # extract the global signatures and new signatures from the final_signatures dictionary
                    globalsigs = final_signatures["globalsigs"]
                    globalsigs = np.array(globalsigs)
                    newsigs = final_signatures["newsigs"]
                    processAvg = np.hstack([globalsigs, newsigs])  
                    allsigids = final_signatures["globalsigids"]+final_signatures["newsigids"]
                    
                    sub.make_final_solution(processAvg, allgenomes, allsigids, layer_directory2, m, index, allcolnames)
                    
                #######################################################################################################
            elif hierarchi is False:
                
                ################################### Decompose the new signatures into global signatures   #########################
                processAvg = information[solution-startProcess][0]
               
                # create the folder for the final solution/ De Novo Solution
                layer_directory1 = output+"/Final Solution/De Novo Solution"
                try:
                    if not os.path.exists(layer_directory1):
                        os.makedirs(layer_directory1)
                except: 
                    print ("The {} folder could not be created".format("output"))
                
                # make de novo solution(processAvg, allgenomes, layer_directory1)
                listOfSignatures = sub.make_letter_ids(idlenth = processAvg.shape[1])
                sub.make_final_solution(processAvg, allgenomes, listOfSignatures, layer_directory1, m, index, allcolnames)    
                
               # create the folder for the final solution/ Decomposed Solution
                layer_directory2 = output+"/Final Solution/Decomposed Solution"
                try:
                    if not os.path.exists(layer_directory2):
                        os.makedirs(layer_directory2)
                except: 
                    print ("The {} folder could not be created".format("output"))
            
                
                final_signatures = sub.signature_decomposition(processAvg, m, layer_directory2)
                # extract the global signatures and new signatures from the final_signatures dictionary
                globalsigs = final_signatures["globalsigs"]
                globalsigs = np.array(globalsigs)
                newsigs = final_signatures["newsigs"]
                processAvg = np.hstack([globalsigs, newsigs])  
                allsigids = final_signatures["globalsigids"]+final_signatures["newsigids"]
                
                sub.make_final_solution(processAvg, genomes, allsigids, layer_directory2, m, index, colnames)
               
                break
            
        


if __name__=="__main__":
    
    sigProfilerExtractor("text", "textfunc", "all_mice_silvio.txt", refgen="GRCh37", startProcess=1, endProcess=2, totalIterations=3, \
                         cpu=-1, hierarchy = False, mtype = ["default"],exome = False, indel_extended = False)
    

print (__name__)