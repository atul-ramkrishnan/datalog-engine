from ..model.model import Predicate


def convert_to_datalog_format(database):
    # Combine all the inner sets into one set
    combined_set = set()
    for value_set in database.values():
        combined_set.update(value_set)

    # Sort the combined set based on the predicate
    sorted_data = sorted(combined_set, key=lambda x: x.predicate)

    result = ""
    for item in sorted_data:
        predicate = item.predicate
        terms = ", ".join(item.terms)
        result += f"{predicate}({terms}).\n"
    return result


def semi_naive_evaluation(base_facts, rules, verbose=False):
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

    i = 1
    while any(delta.values()):  # Continue as long as there are new facts in any of the delta sets        
        # Update database with the union of its current facts and the delta from the previous iteration
        if verbose:
            print(f"<---------- Iteration {i} ---------->")
            print(f"p[{i-1}]:")
            print(convert_to_datalog_format(database))
            print(f"delta(p[{i-1}]):")
            print(convert_to_datalog_format(delta))
        for predicate in unique_predicates:
            database[predicate].update(delta[predicate])
        
        next_big_delta = {predicate: set() for predicate in unique_predicates}

        for rule in rules:
            head_predicate = rule.head.predicate
            rule_big_delta = compute_big_delta(rule, delta, database)

            # Update the next_big_delta
            next_big_delta[head_predicate].update(rule_big_delta)

        # Update delta for the next iteration
        for predicate in unique_predicates:
            delta[predicate] = next_big_delta[predicate] - database[predicate]

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
            derived_fact = project_head(rule, match)
            big_delta.add(derived_fact)

             # Tracing information
            # print("Rule:", rule)
            # print("Matched with:", match)
            # print("Derived Fact:", derived_fact)
            # print("Current Delta:", delta)
            # print("Current Database:", database)
            # print("------------------------------")

    return big_delta


def match_and_join_with_delta(current_predicate, delta, other_predicates, database):
    matches = []

    # Start with the facts from the delta for the current predicate
    delta_facts = delta.get(current_predicate.predicate, set())
    database_facts = database.get(current_predicate.predicate, set())
    
    # Merge the facts from delta and database
    all_facts = delta_facts.union(database_facts)

    for current_fact in all_facts:
        initial_match = join(current_predicate, current_fact, None, None)
        if initial_match:
            matches.extend(recursive_join(initial_match, other_predicates, database))

    return matches


def recursive_join(current_match, remaining_predicates, database):
    if not remaining_predicates:
        return [current_match]

    current_predicate = remaining_predicates[0]
    next_predicates = remaining_predicates[1:]

    current_facts = database.get(current_predicate.predicate, set())
    matches = []

    for current_fact in current_facts:
        # Consider the current match when joining
        new_match = join_with_existing_match(current_predicate, current_fact, current_match)
        if new_match:
            # Merge the current match with the new match
            merged_match = {**current_match, **new_match}
            matches.extend(recursive_join(merged_match, next_predicates, database))

    return matches


def join_with_existing_match(predicate, fact, existing_match):
    unifier = {}

    # First, ensure that the existing match is consistent
    for term in predicate.terms:
        if term[0].isupper() and term in existing_match:
            unifier[term] = existing_match[term]

    # Now, try to unify the predicate with the fact
    for term1, term2 in zip(predicate.terms, fact.terms):
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


def join(predicate1, fact1, predicate2, fact2):
    unifier = {}

    # Unify predicate1 and fact1
    if not unify_terms(predicate1.terms, fact1.terms, unifier):
        return None

    # If predicate2 and fact2 are provided, unify them as well
    if predicate2 and fact2:
        if not unify_terms(predicate2.terms, fact2.terms, unifier):
            return None

    return unifier


def unify_terms(terms1, terms2, unifier):
    for term1, term2 in zip(terms1, terms2):
        if term1[0].isupper():  # If term1 is a variable
            if term1 in unifier:
                if unifier[term1] != term2:
                    return False  # Mismatch, so no unification possible
            else:
                unifier[term1] = term2
        else:
            if term1 != term2:
                return False  # Mismatch, so no unification possible
    return True


def project_head(rule, match):
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
