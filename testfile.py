from nlp_parser import save_constraints

sample_text = """
No lecturer should teach two courses at the same time
Classes above 150 students must use Hall A
Prefer practical courses in the morning
"""

print(save_constraints(sample_text))