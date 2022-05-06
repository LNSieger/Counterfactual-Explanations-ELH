from ontolearn.knowledge_base import KnowledgeBase
from owlapy.model import OWLObjectProperty, OWLObjectPropertyAssertionAxiom, OWLClassAssertionAxiom, \
IRI, OWLNamedIndividual, OWLObjectSomeValuesFrom, OWLObjectIntersectionOf, OWLClass
from owlapy.owlready2._base import OWLReasoner_Owlready2
from owlapy.fast_instance_checker import OWLReasoner_FastInstanceChecker
from collections import OrderedDict
import os
    

def Counterfactual_Generator(concept, data_file, individual, NS, variant: str = "edit", saving: bool = False):
        
    def Individual_Changer(concept_part, kb, manager, reasoner, individual, NS):            
        
        global change_count
        change_count = 0
        
        if isinstance(concept_part,OWLClass):

            classes_list = list(reasoner.sub_classes(concept_part))
            classes_list.append(concept_part)
            classes_list_names = []
            for h in classes_list:
                if h in list(reasoner.types(individual, direct=False)):
                    manager.remove_axiom(kb.ontology(), OWLClassAssertionAxiom(individual, h))
                    if variant == "with_subclasses":
                        change_count = change_count+1
            if variant == "edit":
                change_count = 1
          
        elif isinstance(concept_part,OWLObjectSomeValuesFrom):
            role_name = concept_part.get_property().get_iri()._remainder
            role = OWLObjectProperty(IRI(NS, f'{role_name}'))
            
            props_list = list(reasoner.sub_object_properties(role))
            props_list.append(role)
            props_list_names = []
            
            for g in props_list:
                props_list_names.append(g.get_iri()._remainder)
            role_object_list = []
            for h in props_list_names:
                for y in list(reasoner.object_property_values(individual, OWLObjectProperty(IRI(NS, f'{h}')))):
                    role_object_list.append(y)   
            role_object_list = list(OrderedDict.fromkeys(role_object_list))
            #Removing           
            if concept_part.get_filler().is_owl_thing() == True:
                #Counting
                if variant == "edit":
                    for k in role_object_list:
                        if k in list(reasoner.object_property_values(individual, role)):
                            change_count = change_count+1
                if variant == "with_subclasses":
                    for h in props_list_names:
                        for k in role_object_list:
                            if k in list(reasoner.object_property_values(individual, OWLObjectProperty(IRI(NS, f'{h}')))):
                                change_count = change_count+1
                for z in props_list_names:
                    for j in role_object_list:
                        manager.remove_axiom(kb.ontology(), OWLObjectPropertyAssertionAxiom(individual, OWLObjectProperty(IRI(NS, f'{z}')), j))

            else:
                role_objects_in_ER_concept = []
                for k in role_object_list:
                    if k in list(reasoner_sub.instances(concept_part.get_filler())):
                        role_objects_in_ER_concept.append(k)
                #Counting
                if variant == "edit":
                    for k in role_objects_in_ER_concept:
                        if k in list(reasoner.object_property_values(individual, role)):
                            change_count = change_count+1
                if variant == "with_subclasses":
                    for h in props_list_names:
                        for k in role_objects_in_ER_concept:
                            if k in list(reasoner.object_property_values(individual, OWLObjectProperty(IRI(NS, f'{h}')))):
                                change_count = change_count+1
                for h in props_list_names:
                    for m in role_objects_in_ER_concept:   
                        manager.remove_axiom(kb.ontology(), OWLObjectPropertyAssertionAxiom(individual, OWLObjectProperty(IRI(NS, f'{h}')), m))
                    
    KB_List = []
    concept_list = []
    
    if isinstance(concept,OWLObjectIntersectionOf):
        for n in concept.operands():
            concept_list.append(n)    
            KB_List.append(KnowledgeBase(path = data_file))
    else:
        KB_List.append(KnowledgeBase(path = data_file))
        concept_list.append(concept)
    
    global KB_count
    KB_count = 0
    counterfactual_dict = {}
    for o in KB_List:
        manager_reasoning = KnowledgeBase(path = data_file).ontology().get_owl_ontology_manager()
        manager_editing = o.ontology().get_owl_ontology_manager()
        kb = manager_reasoning.load_ontology(IRI.create(data_file))
        base_reasoner = OWLReasoner_Owlready2(kb)
        reasoner = OWLReasoner_FastInstanceChecker(kb, base_reasoner, negation_default=True, sub_properties=True)
        reasoner_sub = OWLReasoner_FastInstanceChecker(kb, base_reasoner, negation_default=True, )
        concept_part = concept_list[KB_count]
        Individual_Changer(concept_part, o, manager_editing, reasoner, individual, NS)
        if saving:
            if (os.path.exists(f"/{os.getcwd()}/Counterfactual{KB_count}.owl")):
                os.remove(f"/{os.getcwd()}/Counterfactual{KB_count}.owl")
            manager_editing.save_ontology(o.ontology(), IRI.create(f'file:/Counterfactual{KB_count}.owl'))
        print(f"Counterfactual {KB_count} was created with {change_count} axiom changes.")
        counterfactual_dict[f'subconcept{KB_count}']=f'{concept_part}'
        counterfactual_dict[f'{KB_count}']=f'{change_count}'
        KB_count = KB_count+1
    return counterfactual_dict


    

