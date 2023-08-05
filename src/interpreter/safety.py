def check_safety_rules(facts, rules):
    # Check Rule 1: Facts should be ground
    for fact in facts:
        fact_terms = fact.fact.terms
        for term in fact_terms:
            if term[0].isupper():  # Variables start with an uppercase letter
                raise Exception(
                    f"Safety Rule Violation: Fact {fact.fact.predicate} has variable {term} as a term.")

    # Check Rule 2: Each variable in the head of a rule must occur in the body
    # of the same rule
    for rule in rules:
        head_variables = [
            term for term in rule.head.terms if term[0].isupper()]
        body_variables = [
            term for predicate in rule.body for term in predicate.terms if term[0].isupper()]

        for head_var in head_variables:
            if head_var not in body_variables:
                raise Exception(
                    f"Safety Rule Violation: Variable {head_var} in head of rule {rule.head.predicate} does not occur in the body.")
