from owlapy.owlready2._base import OWLOntologyManager_Owlready2
from owlapy.model import OWLObjectProperty, IRI, OWLClass, OWLNamedIndividual, OWLThing
from ontolearn.knowledge_base import KnowledgeBase
from owlapy.owlready2._base import OWLReasoner_Owlready2
from owlapy.fast_instance_checker import OWLReasoner_FastInstanceChecker


def DistanceToComparisonIndividuals(comparisons, counterfactuals, NS, individual, variant: str = "edit"):
    best_distance_counterfactuals_list = []
    lowest_distance = float('inf')
    comparison_dict = {}
    count = 0
    for i in counterfactuals:
        data_file = i 
        manager_reasoning = KnowledgeBase(path = data_file).ontology().get_owl_ontology_manager()
        kb = manager_reasoning.load_ontology(IRI.create(data_file))
        base_reasoner = OWLReasoner_Owlready2(kb)
        reasoner = OWLReasoner_FastInstanceChecker(kb, base_reasoner, negation_default=True)
        reasoner_sub = OWLReasoner_FastInstanceChecker(kb, base_reasoner, negation_default=True, sub_properties=True)

        if variant == "edit":
            types_count = list(reasoner.types(individual, direct=True))
            properties_count = list(reasoner.ind_object_properties(individual, direct=True))
        if variant == "with_subclasses":
            types_count = list(reasoner.types(individual, direct=False))
            properties_count = list(reasoner_sub.ind_object_properties(individual, direct=False))
        both_count = list(types_count + properties_count)
        
        diff_number = float('inf')
        for j in comparisons:
            diff = []
            if variant == "edit":
                types_comp = list(reasoner.types(OWLNamedIndividual(IRI(NS, j)), direct=True))
                properties_comp = list(reasoner.ind_object_properties(OWLNamedIndividual(IRI(NS, j)), direct=True))
            elif variant == "with_subclasses":
                types_comp = list(reasoner.types(OWLNamedIndividual(IRI(NS, j)), direct=False))
                properties_comp = list(reasoner_sub.ind_object_properties(OWLNamedIndividual(IRI(NS, j)), direct=False))
            both_comp = list(types_comp + properties_comp)
            for k in both_comp:
                if k not in list(reasoner.types(individual, direct=False)):
                    if k not in list(reasoner_sub.ind_object_properties(individual, direct=False)):
                        diff.append(k)
            for l in both_count:
                if l not in list(reasoner.types(OWLNamedIndividual(IRI(NS, j)), direct=False)):
                    if l not in list(reasoner_sub.ind_object_properties(OWLNamedIndividual(IRI(NS, j)), direct=False)):
                        diff.append(l)
            if len(diff) < diff_number:
                diff_number = len(diff)
        print(i + " has a distance of " + str(diff_number) + " to the comparison set individual most similar to it.")
        comparison_dict[f'{count}']=f'{diff_number}'
        count = count+1
        if diff_number < lowest_distance:
            lowest_distance = diff_number
            best_distance_counterfactual = i
        elif diff_number == lowest_distance:
            if not best_distance_counterfactuals_list:
                best_distance_counterfactuals_list = []
                best_distance_counterfactuals_list.append(best_distance_counterfactual)
            best_distance_counterfactuals_list.append(i)
    if not best_distance_counterfactuals_list:
        print(best_distance_counterfactual + " is the counterfactual that performs best on o4.")
    else:
        print(best_distance_counterfactuals_list)
        print("are the counterfactuals that perform best on o4.")
    return comparison_dict
