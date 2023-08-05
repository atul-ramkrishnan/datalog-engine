from ..model.model import Predicate


def convert_to_datalog_format(database):
    sorted_data = sorted(database, key=lambda x: x.predicate)
    result = ""
    for item in sorted_data:
        predicate = item.predicate
        terms = ", ".join(item.terms)
        result += f"{predicate}({terms}).\n"
    return result


def naive_evaluation(base_facts, rules):
    database = set(fact.fact for fact in base_facts)
    new_facts = database.copy()  # Initialize new_facts with base facts

    while new_facts:  # Continue as long as there are new facts
        next_new_facts = set()  # To keep track of the facts derived in the next iteration

        for rule in rules:
            for match in match_and_join(rule, database):  # Use the entire database to derive new facts
                derived_fact = project_head(rule, match)
                if derived_fact not in database:
                    next_new_facts.add(derived_fact)

        database.update(next_new_facts)
        new_facts = next_new_facts  # Update new_facts for the next iteration

    return convert_to_datalog_format(database)


def semi_naive_evaluation(base_facts, rules):
    database = set(fact.fact for fact in base_facts)
    new_facts = database.copy()  # Initialize new_facts with base facts

    while new_facts:
        next_new_facts = set()  # To keep track of the facts derived in the next iteration

        for rule in rules:
            for match in match_and_join(rule, new_facts):
                derived_fact = project_head(rule, match)
                if derived_fact not in database:
                    next_new_facts.add(derived_fact)

        database.update(next_new_facts)
        new_facts = next_new_facts  # Update new_facts for the next iteration

    return convert_to_datalog_format(database)


def match_and_join(rule, database):
    # Initialize the list of matches with a single empty match
    matches = [{}]

    # Iterate over the predicates in the rule's body
    for predicate in rule.body:
        # Find the facts in the database that match the current predicate
        matching_facts = [fact for fact in database if fact_matches_predicate(fact, predicate)]

        # Initialize a new list of matches for the current predicate
        new_matches = []

        # Iterate over the current matches and the matching facts
        for match in matches:
            for fact in matching_facts:
                # Join the current match with the current fact
                joined_match = join_match_with_fact(match, fact, predicate)
                if joined_match is not None:
                    new_matches.append(joined_match)

        # Update the matches with the new matches for the current predicate
        matches = new_matches

    return matches


def fact_matches_predicate(fact, predicate):
    # Check if the predicate names match
    # print(fact)
    if fact.predicate != predicate.predicate:
        return False

    # Check if the terms match, allowing for variables in the predicate
    for fact_term, predicate_term in zip(fact.terms, predicate.terms):
        # If the predicate term is a variable (uppercase), it can match any fact term
        if predicate_term[0].isupper():
            continue

        # If the predicate term is a constant (lowercase), it must match the corresponding fact term
        if fact_term != predicate_term:
            return False

    return True


def join_match_with_fact(match, fact, predicate):
    # Create a copy of the current match to avoid modifying the original
    joined_match = match.copy()

    # Iterate over the terms of the fact and the corresponding terms of the predicate
    for fact_term, predicate_term in zip(fact.terms, predicate.terms):
        # If the predicate term is a variable (uppercase)
        if predicate_term[0].isupper():
            # If the variable is already bound in the match, check if the binding is consistent with the fact term
            if predicate_term in joined_match and joined_match[predicate_term] != fact_term:
                return None  # Inconsistent binding, so the join is not possible

            # Bind the variable to the fact term in the joined match
            joined_match[predicate_term] = fact_term

        # If the predicate term is a constant (lowercase), check if it matches the fact term
        elif fact_term != predicate_term:
            return None  # Mismatched constant, so the join is not possible

    return joined_match


def project_head(rule, match):
    # Extract the head of the rule
    head = rule.head

    # Construct the derived fact's terms by replacing variables with their bindings in the match
    derived_terms = [match[term] if term[0].isupper() else term for term in head.terms]

    # Construct the derived fact as a Predicate object
    derived_fact_predicate = Predicate(
        name=head.predicate,
        terms=derived_terms,
        isNegated=head.isNegated,
        type='predicate'
    )

    return derived_fact_predicate


# def test(facts, rules):
#     database = set(fact.fact for fact in facts)

#     for rule in rules:
#         for match in match_and_join(rule, database):
#             print("<----------->")
#             print(rule)
#             print(match)