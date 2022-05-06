import os
import random
import copy
import scipy.stats as stats
import json
import numpy as np
os.chdir("//home/leo/sciebo")
from Counterfactual_Generator_ELH import Counterfactual_Generator
from Distance_o_four import DistanceToComparisonIndividuals
from owlapy.render import ManchesterOWLSyntaxOWLObjectRenderer
os.chdir("//home/leo")


def ScoringCounterfactuals(reasoner, concept, chosenclass, data_file, NS, onto, prediction, all_individuals, individual):
    
    print(f"Generating counterfactuals to individual '{individual.get_iri().get_remainder()}'")
    o23_edit = Counterfactual_Generator(concept, data_file, individual, NS, variant = "edit", saving = True)
    o23_edit_w_s = Counterfactual_Generator(concept, data_file, individual, NS, variant = "with_subclasses", saving = True)
    
    comparison_possibilities = copy.deepcopy(all_individuals)
    comparison_possibilities.remove(individual)
    comparison_individuals = list(random.sample(comparison_possibilities, k=10))
    comparison_iris = []
    for i in comparison_individuals:
        comparison_iris.append(i.get_iri().get_remainder())  
    
    counterfactual_files = []
    for i in range (0, len(list(concept.operands()))):
        counterfactual_files.append(f"/home/leo/Counterfactual{i}.owl")
    
    o4_edit = DistanceToComparisonIndividuals(comparison_iris, counterfactual_files, NS, individual, variant = "edit")
    o4_edit_w_s = DistanceToComparisonIndividuals(comparison_iris, counterfactual_files, NS, individual, variant = "with_subclasses")
    
    scoredict_edit={}
    scoredict_edit_w_s={}
    values_o23_edit = []
    values_o23_edit_w_s = []
    values_o4_edit = []
    values_o4_edit_w_s = []
    winner_edit = []
    winner_edit_w_s = []

# Simple edit
    for i in range(0, len(o4_edit)):
        values_o23_edit.append(int(o23_edit.get(f'{i}')))
        values_o4_edit.append(int(o4_edit.get(f'{i}')))
        if np.isnan(stats.zscore(values_o23_edit)).any():
            values_o23_edit_zscores = []
            for i in range (0, len(values_o23_edit)): values_o23_edit_zscores.append(0)
        else:
            values_o4_edit_zscores = stats.zscore(values_o4_edit)
        if np.isnan(stats.zscore(values_o4_edit)).any():
            values_o4_edit_zscores = []
            for i in range (0, len(values_o4_edit)): values_o4_edit_zscores.append(0)
        else:
            values_o4_edit_zscores = stats.zscore(values_o4_edit)
    for i in range(0, len(values_o23_edit_zscores)): 
        scoredict_edit[f'{i}'] = values_o23_edit_zscores[i] + values_o4_edit_zscores[i]
    min_value_edit = min(scoredict_edit.values())
    for key in scoredict_edit.keys():
        if scoredict_edit[key] == float(min_value_edit):
            winner_edit.append({key : scoredict_edit[key]})
            
# With subclasses            
    for i in range(0, len(o4_edit_w_s)):
        values_o23_edit_w_s.append(int(o23_edit_w_s.get(f'{i}')))
        values_o4_edit_w_s.append(int(o4_edit_w_s.get(f'{i}')))
        if np.isnan(stats.zscore(values_o23_edit_w_s)).any():
            values_o23_edit_w_s_zscores = []
            for i in range (0, len(values_o23_edit_w_s)): values_o23_edit_w_s_zscores.append(0)
        else:
            values_o23_edit_w_s_zscores = stats.zscore(values_o23_edit_w_s)
        if np.isnan(stats.zscore(values_o4_edit_w_s)).any():
            values_o4_edit_w_s_zscores = []
            for i in range(0, len(values_o4_edit_w_s)): values_o4_edit_w_s_zscores.append(0)
        else:
            values_o4_edit_w_s_zscores = stats.zscore(values_o4_edit_w_s)
    for i in range(0, len(values_o23_edit_w_s_zscores)): 
        scoredict_edit_w_s[f'{i}'] = values_o23_edit_w_s_zscores[i] + values_o4_edit_w_s_zscores[i]
    min_value_edit_w_s = min(scoredict_edit_w_s.values())
    for key in scoredict_edit_w_s.keys():
        if scoredict_edit_w_s[key] == float(min_value_edit_w_s):
            winner_edit_w_s.append({key : scoredict_edit_w_s[key]})
        
    print('Providing results...')
    simple_edit_results = []
    for d in winner_edit:
        simple_edit_results.append(next(iter(d.keys())))
        simple_edit_results.append(next(iter(d.values())))
    edit_sub_results = []
    for d in winner_edit_w_s:
        edit_sub_results.append(next(iter(d.keys())))
        edit_sub_results.append(next(iter(d.values())))
    
    results = {'prediction': prediction, 'class' : chosenclass, 'individual': individual.get_iri().get_remainder(),\
            'comparison_instances': comparison_individuals, 'simple_edit' : simple_edit_results,'edit_sub' : edit_sub_results,\
                'Distances_edit': o23_edit, 'Distances_edit_sub': o23_edit_w_s,\
                    'Likeliness_scores_edit': o4_edit, 'Likeliness_scores_edit_sub': o4_edit_w_s}
    return results