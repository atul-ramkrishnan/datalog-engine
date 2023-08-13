from ..model.model import Predicate
from collections import defaultdict
import copy

def convert_to_datalog_format(data):
    result = []
    for predicate, facts in data.items():
        for fact in facts:
            terms = ", ".join(fact)
            result.append(f"{predicate}({terms}).")
    return "\n".join(result)


def get_facts_matching_predicate(predicate, database):
    predicate_name = predicate.predicate
    
    if predicate_name in database:
        return database[predicate_name]
    else:
        return set()
    

def is_variable(term):
    return term[0].isupper()


def join_match_with_fact(match, fact, predicate):
    new_match = match.copy()

    for variable, term in zip(predicate.terms, fact):
        if is_variable(variable):
            if variable in new_match and new_match[variable] != term:
                return None
            new_match[variable] = term
        else:
            if variable != term:
                return None

    return new_match


def match_and_join(rule_body, database):
    matches = [{}]
    for predicate in rule_body:
        facts_matching_predicate = get_facts_matching_predicate(predicate, database)
        new_matches = []

        for match in matches:
            for fact in facts_matching_predicate:
                # Join the current match with the current fact
                joined_match = join_match_with_fact(match, fact, predicate)
                if joined_match is not None:
                    new_matches.append(joined_match)

        # Update the matches with the new matches for the current predicate
        matches = new_matches

    return matches


def project_head(rule_head, match, derived_facts):
    projected_terms = tuple(match[var] if var in match else var for var in rule_head.terms)
    predicate = rule_head.predicate
    derived_facts[predicate].add(projected_terms)


def apply_rule(rule, database, derived_facts):
    # print(rule)
    for match in match_and_join(rule.body, database):
        project_head(rule.head, match, derived_facts)
        

def semi_naive_evaluation(base_facts, rules, verbose=False):
    edb_predicates = defaultdict(set)               # q1, q2, ... , qm
    for fact in base_facts:
        edb_predicates[fact.fact.predicate].add(tuple(fact.fact.terms))


    idb_predicates = defaultdict(set)               # p1, p2, ..., pn
    for rule in rules:
        idb_predicates[rule.head.predicate] = set()
        for predicate in rule.body:
            if predicate.predicate not in edb_predicates:
                idb_predicates[predicate.predicate] = set()

    
    delta_small = copy.deepcopy(idb_predicates)     # delta_small(p1), delta_small(p2), ..., delta_small(pn)

    # Initialize delta_small with tuples produced by rules using only EDBs
    for rule in rules:
        apply_rule(rule, edb_predicates, delta_small)

    i = 1
    while any(delta_small.values()):
        for predicate, tuple_set in delta_small.items():
            idb_predicates[predicate].update(tuple_set)
        
        # print(idb_predicates)
        delta_big = calculate_delta_big(rules, copy.deepcopy(idb_predicates), copy.deepcopy(delta_small), copy.deepcopy(edb_predicates))
        
        for predicate, tuple_set in idb_predicates.items():
            if predicate in delta_small:
                delta_small[predicate] = delta_big[predicate] - tuple_set
        if verbose:
            print(f"<---------- Iteration {i} ---------->")
            print(f"p[{i}]:")
            print(convert_to_datalog_format(idb_predicates))
            print(f"delta(p[{i}]):")
            print(convert_to_datalog_format(delta_small))
                    
        i += 1
    return convert_to_datalog_format(idb_predicates)


def merge_dicts(dict1, dict2):
    '''Merge two defaultdicts and return the result.'''
    result = defaultdict(set)
    for key, value_set in dict1.items():
        result[key].update(value_set)
    for key, value_set in dict2.items():
        result[key].update(value_set)
    return result


def combine_databases(idb_predicates, predicate, delta_small, edb_predicates):
    # Remove the key-value pair associated with 'predicate'
    idb_predicates.pop(predicate, None)
    
    # Merge the dictionaries
    temp_result = merge_dicts(idb_predicates, delta_small)
    final_database = merge_dicts(temp_result, edb_predicates)
    
    return final_database


def apply_rule_with_delta(rule, idb_predicates, delta_small, edb_predicates, delta_big):
    idb_rule_predicates = []
    edb_rule_predicates = []
    for predicate in rule.body:
        if predicate.predicate in edb_predicates:
            edb_rule_predicates.append(predicate.predicate)
        else:
            idb_rule_predicates.append(predicate.predicate)
    
    for predicate in idb_rule_predicates:
        database = combine_databases(idb_predicates, predicate, delta_small, edb_predicates)
        for match in match_and_join(rule.body, database):
            project_head(rule.head, match, delta_big)


def calculate_delta_big(rules, idb_predicates, delta_small, edb_predicates):
    delta_big = defaultdict(set, {key: set() for key in idb_predicates.keys()})
    for rule in rules:
        apply_rule_with_delta(rule, idb_predicates, delta_small, edb_predicates, delta_big)
    
    return delta_big
