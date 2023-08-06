from ..model.model import Predicate

def convert_to_datalog_format(database):
    sorted_data = sorted(database, key=lambda x: x.predicate)
    result = ""
    for item in sorted_data:
        predicate = item.predicate
        terms = ", ".join(item.terms)
        result += f"{predicate}({terms}).\n"
    return result

def semi_naive_evaluation(base_facts, rules):
    # Extract predicates from base_facts
    fact_predicates = {fact.fact.predicate for fact in base_facts}

    # Extract predicates from rules (both head and body)
    rule_predicates = {rule.head.predicate for rule in rules}
    for rule in rules:
        for predicate in rule.body:
            rule_predicates.add(predicate.predicate)

    # Combine the two sets to get all unique predicates
    unique_predicates = fact_predicates.union(rule_predicates)

    # Initialize database and delta using unique_predicates
    database = {predicate: set() for predicate in unique_predicates}
    delta = {predicate: {fact.fact for fact in base_facts if fact.fact.predicate == predicate} for predicate in unique_predicates}

    # print(database)
    # print(delta)

    while any(delta.values()):  # Continue as long as there are new facts in any of the delta sets
        print("--------------Iteration----------------")
        next_database = database.copy()
        next_delta = {predicate: set() for predicate in unique_predicates}

        for rule in rules:
            head_predicate = rule.head.predicate
            big_delta = compute_big_delta(rule, delta, database)
            print("rule: ", rule)
            print("delta: ", delta)
            print("database: ", database)
            print("big_delta:", big_delta)
            print()
            
            # Update the next_database and next_delta
            next_database[head_predicate].update(big_delta)
            next_delta[head_predicate] = big_delta - database[head_predicate]

        # Update database and delta for the next iteration
        database = next_database
        delta = next_delta

    # print(database)
    return convert_to_datalog_format(database)

def compute_big_delta(rule, delta, database):
    big_delta = set()

    # For each predicate in the rule's body, compute the join using the current delta and database
    for i, predicate in enumerate(rule.body):
        # Get the other predicates in the rule's body excluding the current predicate
        other_predicates = rule.body[:i] + rule.body[i+1:]
        # Use the delta for the current predicate and the database for the other predicates
        matches = match_and_join_with_delta(predicate, delta, other_predicates, database)
        for match in matches:
            # print(match)
            derived_fact = project_head(rule, match)
            big_delta.add(derived_fact)

    return big_delta

def match_and_join_with_delta(current_predicate, delta, other_predicates, database):
    matches = []

    # Start with the facts from the delta for the current predicate
    current_facts = delta[current_predicate.predicate]

    for current_fact in current_facts:
        # This will store potential matches for the current_fact
        potential_matches = []

        # If there are no other predicates, just unify the current_predicate with the current_fact
        if not other_predicates:
            match = join(current_predicate, current_fact, None, None)
            if match:
                matches.append(match)
            continue

        for predicate in other_predicates:
            for fact in database[predicate.predicate]:
                match = join(current_predicate, current_fact, predicate, fact)
                if match:
                    potential_matches.append(match)

        # Check if we found matches for all other predicates
        if len(potential_matches) == len(other_predicates):
            # Merge all these matches into one unified match
            unified_match = {}
            for match in potential_matches:
                unified_match.update(match)
            matches.append(unified_match)

    return matches

def join(predicate1, fact1, predicate2, fact2):
    unifier = {}

    # Unify predicate1 and fact1
    for term1, term2 in zip(predicate1.terms, fact1.terms):
        if term1[0].isupper():  # If term1 is a variable
            if term1 in unifier:
                if unifier[term1] != term2:
                    return None  # Mismatch, so no unification possible
            else:
                unifier[term1] = term2
        else:
            if term1 != term2:
                return None  # Mismatch, so no unification possible

    # If predicate2 and fact2 are provided, unify them as well
    if predicate2 and fact2:
        for term1, term2 in zip(predicate2.terms, fact2.terms):
            if term1[0].isupper():  # If term1 is a variable
                if term1 in unifier:
                    if unifier[term1] != term2:
                        return None  # Mismatch, so no unification possible
                else:
                    unifier[term1] = term2
            else:
                if term1 != term2:
                    return None  # Mismatch, so no unification possible

    return unifier




def project_head(rule, match):
    # print(rule)
    # print(match)
    # Extract the head of the rule
    head = rule.head

    # Construct the derived fact's terms by replacing variables with their
    # bindings in the match
    derived_terms = [match[term] if term[0].isupper() else term for term in head.terms]

    # Construct the derived fact as a Predicate object
    derived_fact_predicate = Predicate(
        name=head.predicate,
        terms=derived_terms,
        type='predicate'
    )

    return derived_fact_predicate