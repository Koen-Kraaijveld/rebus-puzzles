import json
import random

from tqdm import tqdm

from graphs.BeliefGraphGenerator import BeliefGraphGenerator
from graphs.BeliefGraphReasoner import BeliefGraphReasoner
from puzzles.Benchmark import Benchmark

seed = 43
random.seed(seed)

n_puzzles = 50
benchmark = Benchmark()
puzzles = random.sample(benchmark.get_puzzles(), n_puzzles)
model = "gpt-4o"
max_depth = 1
verbose = False

hyperparameters = {
    "k": 9,
    "k_entailer": 36,
    "k_xor": 30,
    "k_mc": 9,
    "t_entailer": 1.02,
    "t_xor": 1.1,
    "t_mc": 0.98,
    "m_xor": 0.3,
    "c_xor": 1.,
    "c_mc": 1.
}

for puzzle in tqdm(puzzles, desc="Running belief graphs"):
    image = puzzle["image"]
    options = list(puzzle["options"].values())
    generator = BeliefGraphGenerator(image, options, hyperparameters, max_depth=max_depth, model=model)
    graph = generator.generate_graph()

    reasoner = BeliefGraphReasoner(hyperparameters)
    graph, _ = reasoner.fix_graph(graph, verbose=verbose)
    answer_csp = graph.get_answer()

    puzzle["output"] = answer_csp

    if verbose:
        print(f"\nOptions:", options)
        print("Correct:", puzzle["correct"])
        print("Answer:", answer_csp)


with open(f"../results/analysis/results_v3/belief_graphs_{model}_v8.json", "w") as file:
    metadata = {
        "experiment": "Belief Graphs",
        "model": model,
        "seed": seed,
        "max_depth": max_depth,
        "n_puzzles": n_puzzles,
        "hyperparameters": hyperparameters
    }

    json.dump({
        "metadata": metadata,
        "results": puzzles
    }, file, indent=3)
