import os
from ontolearn.binders import DLLearnerBinder
from owlapy.parser import ManchesterOWLSyntaxParser
from ontolearn.knowledge_base import KnowledgeBase
from owlapy.model import OWLClassAssertionAxiom
from owlapy.owlready2._base import OWLReasoner_Owlready2
from owlapy.fast_instance_checker import OWLReasoner_FastInstanceChecker
from owlapy.model import IRI, OWLObjectIntersectionOf, OWLDeclarationAxiom, OWLThing, OWLClass
import copy
import csv
import random
os.chdir("//home/leo/sciebo")
from scoring import ScoringCounterfactuals
from Counterfactual_Generator_ELH import Counterfactual_Generator
os.chdir("//home/leo")

#Choose dataset

data_file = "/home/leo/Working/Ontolearn/KGs/Family/family-benchmark_rich_background_mod.owl"
NS = "http://www.benchmark.org/family#"
kb = KnowledgeBase(path = data_file)
manager_editing = kb.ontology().get_owl_ontology_manager()
manager_reasoning = KnowledgeBase(path = data_file).ontology().get_owl_ontology_manager()
onto = manager_reasoning.load_ontology(IRI.create(data_file))
base_reasoner = OWLReasoner_Owlready2(onto)
reasoner = OWLReasoner_FastInstanceChecker(onto, base_reasoner, negation_default=True, sub_properties=True)
all_classes = list(reasoner.sub_classes(OWLThing))
all_individuals = list(onto.individuals_in_signature())
filecontents = []
random.seed(4141)

def RemoveClass(anyclass, reasoner, manager_editing):
    
    #Delete Class axioms for class that shall be newly classified 
    for j in onto.individuals_in_signature():
        if anyclass in reasoner.types(j, direct=False):
            manager_editing.remove_axiom(kb.ontology(), OWLClassAssertionAxiom(j, anyclass))
    manager_editing.remove_axiom(kb.ontology(), OWLDeclarationAxiom(anyclass))
    manager_editing.save_ontology(kb.ontology(), IRI.create(f'file:/Family_without_{anyclass.get_iri().get_remainder()}.owl'))
    output_path = f'/home/leo/Family_without_{anyclass.get_iri().get_remainder()}.owl'
    return output_path
    
def CreatePositives(reasoner):
    #Get positive examples
    positive_list = list(reasoner.instances(anyclass))
    count=0
    positive_list = list(random.sample(positive_list, k=10))
    for i in positive_list:
        positive_list[count] = i.get_iri().as_str()
        count = count+1
    positive = tuple(positive_list)
    return positive
    
def CreateNegatives(onto, positive):
    #Get as many negative examples
    negative = []
    for i in onto.individuals_in_signature():
        if i not in positive:
            negative.append(i)
    negative = list(random.sample(negative, k=10))
    count=0
    for i in negative:
        negative[count] = i.get_iri().as_str()
        count = count+1
    negative = tuple(negative)
    return negative

#Go through classes
for anyclass in all_classes:
    
    kb = KnowledgeBase(path = data_file)
    manager_editing = kb.ontology().get_owl_ontology_manager()
    manager_reasoning = KnowledgeBase(path = data_file).ontology().get_owl_ontology_manager()
    onto = manager_reasoning.load_ontology(IRI.create(data_file))
    base_reasoner = OWLReasoner_Owlready2(onto)
    reasoner = OWLReasoner_FastInstanceChecker(onto, base_reasoner, negation_default=True, sub_properties=True)
    
    output_path = RemoveClass(anyclass, reasoner, manager_editing)    
    positive = CreatePositives(reasoner)
    negative = CreateNegatives(onto, positive)
    
    #Create reasoners
    kb_edit = KnowledgeBase(path = output_path)
    manager_reasoning_edit = kb_edit.ontology().get_owl_ontology_manager()
    onto_edit = manager_reasoning.load_ontology(IRI.create(output_path))
    base_reasoner_edit = OWLReasoner_Owlready2(onto)
    reasoner_edit = OWLReasoner_FastInstanceChecker(onto, base_reasoner, negation_default=True, sub_properties=True)
    
    #Learn concept using ELTL
    
    # (1) Enter the absolute path of the input knowledge base
    kb_path = output_path
    # (2) To download DL-learner,  https://github.com/SmartDataAnalytics/DL-Learner/releases.
    dl_learner_binary_path = '/home/leo/Working/dllearner-1.5.0/'
    # (3) Initialize CELOE, OCEL, and ELTL
    
    eltl = DLLearnerBinder(binary_path=dl_learner_binary_path, kb_path=kb_path, model='eltl')
    # (4) Fit (4) on the learning problems and show the best concept.
    
    best_pred_eltl = eltl.fit(pos=positive, neg=negative, max_runtime=1).best_hypothesis()
    
    parser = ManchesterOWLSyntaxParser(NS)
    prediction = best_pred_eltl['Prediction']
    concept = parser.parse_expression(prediction)
    
    individual = random.choice(list(reasoner_edit.instances(concept)))
    
    print(f"The concept is {prediction}")
    if not isinstance(concept, OWLObjectIntersectionOf):
        print("Only one counterfactual")
        o23_edit = Counterfactual_Generator(concept, data_file, individual, NS, variant = "edit", saving = True)
        o23_edit_w_sub = Counterfactual_Generator(concept, data_file, individual, NS, variant = "with_subclasses", saving = True)
        results = {'prediction': prediction, 'class' : anyclass.get_iri().get_remainder(), 'individual': individual.get_iri().get_remainder(),\
                'comparison_instances': 'None', 'simple_edit' : 'None','edit_sub' : 'None',\
                    'Distances_edit': 'None', 'Distances_edit_sub': 'None',\
                'Likeliness_scores_edit': 'None', 'Likeliness_scores_edit_sub': 'None'}
        
    else:
        results = ScoringCounterfactuals(reasoner, concept, anyclass, data_file, NS, onto, prediction, all_individuals, individual)
    results['positive examples'] = positive
    results['negative examples'] = negative
    filecontents.append(results)


    
keys = filecontents[0].keys()

with open('Results_family.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(filecontents)