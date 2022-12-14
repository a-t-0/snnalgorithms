"""Returns the results for the MDSA algorithm. The results are composed of a
list of nodes that is generated by the Alipour algorithm on the original input
graph, a list of nodes that are selected for the following graphs:
snn_algo_graph adapted_snn_graph rad_snn_algo_graph rad_adapted_snn_graph.

, and a boolean per graph to indicate whether the graphs as computed by Alipour
and the SNN match.

These results are returned in the form of a dict.
"""
import copy
from typing import Dict

import networkx as nx
from snncompare.helper import get_actual_duration
from typeguard import typechecked

from snnalgorithms.sparse.MDSA.get_results import get_results


@typechecked
def set_mdsa_snn_results(
    m_val: int, run_config: dict, stage_2_graphs: dict
) -> None:
    """Returns the nodes and counts per node that were computed by the SNN
    algorithm.

    TODO: rewrite to store results in graphs directly.
    """

    # TODO: Verify stage 2 graphs.

    # Get Alipour count.
    # Compute the count for each node according to Alipour et al.'s algorithm.
    alipour_counter_marks = get_results(
        input_graph=stage_2_graphs["input_graph"],
        iteration=run_config["iteration"],
        m_val=m_val,
        rand_props=stage_2_graphs["input_graph"].graph["alg_props"],
        seed=run_config["seed"],
        size=run_config["graph_size"],
    )

    # Compute SNN results
    for graph_name, snn_graph in stage_2_graphs.items():
        # Verify the SNN graphs have completed simulation stage 2.
        if 2 not in stage_2_graphs[graph_name].graph["completed_stages"]:
            raise Exception(
                "Error, the stage 2 simulation is not yet"
                + f" completed for: {graph_name}"
            )

        if graph_name != "input_graph":
            if graph_name == "snn_algo_graph":
                snn_graph.graph["results"] = get_snn_results(
                    alipour_counter_marks,
                    stage_2_graphs["input_graph"],
                    m_val,
                    redundant=False,
                    snn_graph=snn_graph,
                )
                assert_valid_results(
                    snn_graph.graph["results"],
                    alipour_counter_marks,
                    graph_name,
                )

            elif graph_name == "adapted_snn_graph":
                snn_graph.graph["results"] = get_snn_results(
                    alipour_counter_marks,
                    stage_2_graphs["input_graph"],
                    m_val,
                    redundant=True,
                    snn_graph=snn_graph,
                )
                assert_valid_results(
                    snn_graph.graph["results"],
                    alipour_counter_marks,
                    graph_name,
                )

            elif graph_name == "rad_snn_algo_graph":
                snn_graph.graph["results"] = get_snn_results(
                    alipour_counter_marks,
                    stage_2_graphs["input_graph"],
                    m_val,
                    redundant=False,
                    snn_graph=snn_graph,
                )
            elif graph_name == "rad_adapted_snn_graph":
                snn_graph.graph["results"] = get_snn_results(
                    alipour_counter_marks,
                    stage_2_graphs["input_graph"],
                    m_val,
                    redundant=True,
                    snn_graph=snn_graph,
                )
            else:
                raise Exception(f"Invalid graph name:{graph_name}")
            # TODO: verify the results are set correctly.


@typechecked
def assert_valid_results(
    actual_nodenames: Dict[str, int],
    expected_nodenames: Dict[str, int],
    graph_name: str,
) -> None:
    """Assert results are equal to the Alipour default algorithm."""

    # Remove the passed boolean, and redo results verification.
    copy_actual_nodenames = copy.deepcopy(actual_nodenames)
    copy_actual_nodenames.pop("passed")

    # Verify node names are identical.
    if copy_actual_nodenames.keys() != expected_nodenames.keys():
        raise KeyError(
            f"Selected SNN nodenames for: {graph_name}, are "
            "not equal to the default/Neumann selected nodes:\n"
            f"SNN nodes:    {copy_actual_nodenames.keys()}\n"
            "!=\n"
            f"Neumann nodes:{expected_nodenames.keys()}\n"
        )

    # Verify the expected nodes are the same as the actual nodes.
    for key in expected_nodenames.keys():
        if expected_nodenames[key] != copy_actual_nodenames[key]:
            raise ValueError(
                f"SNN count per node for: {graph_name}, are not equal to "
                " the default/Neumann node counts:\n"
                f"SNN nodes:    {actual_nodenames}\n"
                "!=\n"
                f"Neumann nodes:{expected_nodenames}\n"
                f"Node:{key} has different counts."
            )
    if not actual_nodenames["passed"]:
        raise Exception(
            "Error, did not detect a difference between SNN "
            "and Neumann mark count in the nodes. Yet "
            "the results computation says there should be a difference."
        )

    print("")
    for node_index, expected_count in expected_nodenames.items():
        print(
            f"node_index:{node_index}, ali-mark:"
            + f"{expected_count}, snn:{copy_actual_nodenames[node_index]}"
        )


# pylint: disable=R0913
@typechecked
def get_snn_results(
    alipour_counter_marks: Dict[str, int],
    input_graph: nx.Graph,
    m_val: int,
    redundant: bool,
    snn_graph: nx.DiGraph,
) -> dict:
    """Returns the marks per node that are selected by the snn simulation.

    If the simulation is ran with adaptation in the form of redundancy,
    the code automatically selects the working node, and returns its
    count in the list.
    TODO: make it more biologically plausible by using majority voting.
    TODO: determine what to do in a draw: random pick. Allow specifying
    picking heuristic.
    """
    # Determine why the duration is used here to get a time step.
    sim_duration = get_actual_duration(snn_graph)
    # get runtime

    snn_counter_marks = {}
    if not redundant:
        snn_counter_marks = get_nx_LIF_count_without_redundancy(
            input_graph, snn_graph, m_val, sim_duration
        )
    else:
        snn_counter_marks = get_nx_LIF_count_with_redundancy(
            input_graph, snn_graph, m_val, sim_duration
        )

    # Compare the two performances.
    if alipour_counter_marks == snn_counter_marks:
        snn_counter_marks["passed"] = True
    else:
        snn_counter_marks["passed"] = False
    return snn_counter_marks


@typechecked
def get_nx_LIF_count_without_redundancy(
    input_graph: nx.Graph, nx_SNN_G: nx.DiGraph, m_val: int, t: int
) -> dict:
    """Creates a dictionary with the node name and the the current as node
    count.

    # TODO: build support for Lava NX neuron.

    :param G: The original graph on which the MDSA algorithm is ran.
    :param nx_SNN_G:
    :param m: The amount of approximation iterations used in the MDSA
    approximation.
    """
    # Initialise the node counts
    node_counts = {}

    # TODO: verify nx simulator is used, throw error otherwise.
    for node_index in range(0, len(input_graph)):
        node_counts[f"counter_{node_index}_{m_val}"] = int(
            nx_SNN_G.nodes[f"counter_{node_index}_{m_val}"]["nx_lif"][
                t
            ].u.get()
        )
    return node_counts


@typechecked
def get_nx_LIF_count_with_redundancy(
    input_graph: nx.Graph,
    adapted_nx_snn_graph: nx.DiGraph,
    m_val: int,
    t: int,
) -> dict:
    """Creates a dictionary with the node name and the the current as node
    count.

    # TODO: build support for Lava NX neuron.

    :param G: The original graph on which the MDSA algorithm is ran.
    :param nx_SNN_G:
    :param m: The amount of approximation iterations used in the MDSA
    approximation.
    """
    # Initialise the node counts
    node_counts = {}

    # TODO: verify nx simulator is used, throw error otherwise.
    for node_index in range(0, len(input_graph)):
        # Check if counterneuron died, if yes, read out redundant neuron.
        if counter_neuron_died(
            adapted_nx_snn_graph, f"counter_{node_index}_{m_val}"
        ):
            prefix = "red_"
        else:
            prefix = ""

        node_counts[
            f"counter_{node_index}_{m_val}"
        ] = adapted_nx_snn_graph.nodes[
            f"{prefix}counter_{node_index}_{m_val}"
        ][
            "nx_lif"
        ][
            t
        ].u.get()
    return node_counts


@typechecked
def counter_neuron_died(
    snn_graph: nx.DiGraph, counter_neuron_name: str
) -> bool:
    """Returns True if the counter neuron died, and False otherwise. This
    method assumes the chip is able to probe a particular neuron to determine
    if it is affected by radiation or not, after the algorithm is completed.

    Alternatively, a majority voting amongst 3 or more redundant neurons
    may be used to read out the algorithm results.
    """

    # Determine whether the graph has rad_death property:
    if graph_has_dead_neurons(snn_graph):
        return snn_graph.nodes[counter_neuron_name]["rad_death"]
    return False


@typechecked
def graph_has_dead_neurons(snn_graph: nx.DiGraph) -> bool:
    """Checks whether the "rad_death" key is in any of the nodes of the graph,
    and if it is, verifies it is in all of the nodes."""
    rad_death_found = False
    for nodename in snn_graph.nodes:
        if "rad_death" in snn_graph.nodes[nodename].keys():
            rad_death_found = True

    if rad_death_found:
        for nodename in snn_graph.nodes:
            if "rad_death" not in snn_graph.nodes[nodename].keys():
                raise Exception(
                    "Error, rad_death key not set in all nodes of"
                    + "graph, yet it was set for at least one node in graph:"
                    + f"{snn_graph}"
                )

        return True
    return False
