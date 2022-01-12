from ortools.sat.python import cp_model
from ortools import IntVar
from string import ascii_lowercase
from typing import List

letter_to_index_map = {letter: index for index, letter in enumerate(ascii_lowercase)}
index_to_letter_map = {index: letter for letter, index in letter_to_index_map.items()}


def add_doesnt_contain_letter_constraint(
    model: cp_model.CpModel, letter_vars: List[cp_model.IntVar], letter: str
):
    for letter_var in letter_vars:
        model.Add(letter_var != letter_to_index_map[letter])


def add_contains_letter_constraint(
    model: cp_model.CpModel, letter_vars: List[cp_model.IntVar], letter: str
):
    model.AddAllowedAssignments(
        letter_vars,
        [letter_to_index_map[letter] for _ in letter_vars],
    )


def add_exact_letter_position_constraint(
    model: cp_model.CpModel,
    letter_vars: List[cp_model.IntVar],
    letter: str,
    position: int,
):
    model.Add(letter_vars[position] == letter_to_index_map[letter])


# def add_letter_appears_once_constraint(
#     model: cp_model.CpModel, letter_vars: List[cp_model.IntVar], letter: str
# ):
#     unique_letter_disjunction = []

#     for letter_var in letter_vars:
#         this_letter_conjunction = [letter_var == letter_to_index_map[letter]]
#         for other_letter_var in letter_vars:
#             if letter_var == other_letter_var:
#                 continue
#             this_letter_conjunction.append(
#                 other_letter_var != letter_to_index_map[letter]
#             )
#         unique_letter_disjunction.append(z3.And(this_letter_conjunction))

#     model.Add(z3.Or(unique_letter_disjunction))


def add_invalid_position_constraint(
    model: cp_model.CpModel, letter_vars, letter, position
):
    model.Add(letter_vars[position] != letter_to_index_map[letter])


def remove_plurals(words):
    five_letter_words = list(filter(lambda word: len(word) == 5, words))
    four_letter_words = set(filter(lambda word: len(word) == 4, words))
    all_five_letter_words_ending_in_s = set(
        filter(lambda word: word[4] == "s", five_letter_words)
    )
    singular_five_letter_words = list(
        filter(
            lambda word: not (
                word in all_five_letter_words_ending_in_s
                and word[:4] in four_letter_words
            ),
            five_letter_words,
        )
    )
    return singular_five_letter_words


def remove_words_with_invalid_chars(words):
    valid_chars_set = set(letter_to_index_map.keys())

    def contains_only_valid_chars(word):
        return set(word).issubset(valid_chars_set)

    return filter(contains_only_valid_chars, words)


def load_dictionary(dictionary_path=None):
    with open(dictionary_path, "r") as f:
        all_legal_words = set(word.strip() for word in f.readlines())

    words = remove_words_with_invalid_chars(all_legal_words)
    words = list(words)
    words = remove_plurals(words)
    return words


if __name__ == "__main__":
    model = cp_model.CpModel()
    letter_vars = [
        model.NewIntVar(0, 25, "position_1"),
        model.NewIntVar(0, 25, "position_2"),
        model.NewIntVar(0, 25, "position_3"),
        model.NewIntVar(0, 25, "position_4"),
        model.NewIntVar(0, 25, "position_5"),
    ]

    words = load_dictionary(dictionary_path="/usr/share/dict/words")
    possible_assignments: List[List[int]] = []
    for word in words:
        possible_assignments.append([letter_to_index_map[n] for n in word])

    model.AddAllowedAssignments(letter_vars, possible_assignments)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for lv in letter_vars:
            print(f"{lv} = {solver.Value(lv)}")
    else:
        print("No solution found.")
