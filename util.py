import copy
import glob
import json
import os

import networkx as nx
import pandas as pd

from puzzles.patterns.Rule import Rule


def get_node_attributes(graph):
    attrs = {attr: nx.get_node_attributes(graph, attr) for attr in ["text", "is_plural"] + Rule.ALL_RULES}
    node_attrs = {}
    for attr, nodes in attrs.items():
        for node, attr_val in nodes.items():
            if node not in node_attrs:
                node_attrs[node] = {attr: attr_val}
            node_attrs[node][attr] = attr_val
    return node_attrs


def get_edges_from_node(graph, node_id):
    in_edges, out_edges = {}, {}
    for edge in graph.in_edges(node_id, keys=True):
        in_edges[edge] = nx.get_edge_attributes(graph, "rule")[edge]
    for edge in graph.out_edges(node_id, keys=True):
        out_edges[edge] = nx.get_edge_attributes(graph, "rule")[edge]
    return [in_edges, out_edges]


def get_edge_information(graph):
    node_attrs = get_node_attributes(graph)
    edge_attrs = nx.get_edge_attributes(graph, "rule")
    edge_info = {}
    for edge in graph.edges:
        rule = edge_attrs[edge]
        source = node_attrs[edge[0]]
        target = node_attrs[edge[1]]
        edge_info[edge] = (source, rule, target)
    return edge_info


def get_graph_as_sequence(graph):
    node_attrs = get_node_attributes(graph)
    edge_attrs = nx.get_edge_attributes(graph, "rule")
    sequence = []
    for node, attrs in node_attrs.items():
        if (node-1, node) in edge_attrs and edge_attrs[(node-1, node)] != "NEXT-TO":
            sequence.append(edge_attrs[(node-1, node)])
        sequence.append(attrs)
    return sequence


def remove_duplicate_graphs(graphs):
    unique_graphs = []
    for graph in graphs:
        is_duplicate = False
        for unique_graph in unique_graphs:
            if nx.utils.graphs_equal(graph, unique_graph):
                is_duplicate = True
                break
        if not is_duplicate:
            unique_graphs.append(graph)
    return unique_graphs


def count_relational_rules(phrase):
    relational_keywords = [x for xs in Rule.get_all_rules()["relational"].values() for x in xs]
    return sum([1 for word in phrase.split() if word in relational_keywords])


def get_answer_graph_pairs(version, combine=False):
    from puzzles.parsers.CompoundRebusGraphParser import CompoundRebusGraphParser
    from puzzles.parsers.PhraseRebusGraphParser import PhraseRebusGraphParser

    phrases = [os.path.basename(file).split(".")[0]
               for file in glob.glob(f"{os.path.dirname(__file__)}/results/benchmark/final_{version}/*")]
    ladec = pd.read_csv(f"{os.path.dirname(__file__)}/saved/ladec_raw_small.csv")
    custom_compounds = pd.read_csv(f"{os.path.dirname(__file__)}/saved/custom_compounds.csv")

    compound_parser = CompoundRebusGraphParser()
    phrase_parser = PhraseRebusGraphParser()
    phrase_to_graph = {}
    compound_to_graph = {}
    for phrase in phrases:
        orig_phrase = phrase
        if phrase.endswith("_icon") or phrase.endswith("_non-icon"):
            phrase = "_".join(phrase.split("_")[:-1])
        parts = phrase.split("_")
        index = 0
        if (parts[0] in ladec["stim"].tolist() and len(parts) == 2) or len(parts) == 1:
            if parts[-1].isnumeric():
                index = int(parts[-1]) - 1
                parts = parts[:-1]
            phrase_ = " ".join(parts)
            row = ladec.loc[ladec["stim"] == phrase_].values.flatten().tolist()
            if len(row) == 0:
                row = custom_compounds.loc[custom_compounds["stim"] == phrase_].values.flatten().tolist()
            c1, c2, is_plural = row[0], row[1], bool(row[3])
            graphs = compound_parser.parse(c1, c2, is_plural)
            phrase = "_".join(orig_phrase.split())
            if orig_phrase.endswith("non-icon"):
                compound_to_graph[phrase] = remove_icons_from_graph(graphs[index])
            else:
                compound_to_graph[phrase] = graphs[index]

        else:
            if parts[-1].isnumeric():
                index = int(parts[-1]) - 1
                parts = parts[:-1]
            phrase_ = " ".join(parts)
            graphs = phrase_parser.parse(phrase_)
            phrase = "_".join(orig_phrase.split())
            if orig_phrase.endswith("non-icon"):
                phrase_to_graph[phrase] = remove_icons_from_graph(graphs[index])
            else:
                phrase_to_graph[phrase] = graphs[index]
    if combine:
        graphs = {}
        graphs.update(phrase_to_graph)
        graphs.update(compound_to_graph)
        return graphs

    return phrase_to_graph, compound_to_graph


def remove_icons_from_graph(graph):
    graph_no_icon = copy.deepcopy(graph)
    graph_no_icon_node_attrs = get_node_attributes(graph_no_icon)
    for attr in graph_no_icon_node_attrs.values():
        if "icon" in attr:
            attr["text"] = list(attr["icon"].keys())[0].upper()
            del attr["icon"]

    for node in graph_no_icon.nodes:
        graph_no_icon.nodes[node].clear()
    nx.set_node_attributes(graph_no_icon, graph_no_icon_node_attrs)
    return graph_no_icon


