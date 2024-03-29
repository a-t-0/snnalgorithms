"""Creates the MDSA snn neurons.

TODO: replace len(input_graph) with nr_of_nodes arg, or vice versa.
"""
from typing import Dict, List, Union

import networkx as nx
from snnbackends.networkx.LIF_neuron import Identifier, LIF_neuron
from snncompare.export_plots.Plot_config import (
    Plot_config,
    get_default_plot_config,
)
from snncompare.run_config.Run_config import Run_config
from typeguard import typechecked

from snnalgorithms.sparse.MDSA.create_MDSA_snn_recurrent_synapses import (
    create_MDSA_recurrent_synapses,
)
from snnalgorithms.sparse.MDSA.create_MDSA_snn_synapses import (
    create_MDSA_synapses,
)
from snnalgorithms.sparse.MDSA.retry_layout import get_node_position


@typechecked
def get_new_mdsa_graph(
    *,
    run_config: Run_config,
    input_graph: nx.Graph,
) -> nx.DiGraph:
    """Creates the networkx snn for a run configuration for the MDSA
    algorithm."""
    if not isinstance(input_graph.graph["alg_props"], Dict):
        raise KeyError("Error, algorithm properties not set.")
    # exit()
    # TODO get recurrent weight form algo specification.
    recurrent_weight: Union[float, int] = -100

    plot_config: Plot_config = get_default_plot_config()

    snn_graph = create_MDSA_neurons(
        input_graph=input_graph, run_config=run_config, plot_config=plot_config
    )

    for node_name in snn_graph.nodes:
        snn_graph.nodes[node_name]["recur"] = recurrent_weight

    create_MDSA_recurrent_synapses(
        input_graph=input_graph,
        mdsa_snn=snn_graph,
        recurrent_weight=recurrent_weight,
        run_config=run_config,
    )

    create_MDSA_synapses(
        input_graph=input_graph,
        mdsa_snn=snn_graph,
        run_config=run_config,
    )

    return snn_graph


# pylint: disable=R0912
# pylint: disable=R0914
@typechecked
def create_MDSA_neurons(
    *,
    input_graph: nx.Graph,
    plot_config: Plot_config,
    run_config: Run_config,
) -> nx.DiGraph:
    """Creates the neurons for the MDSA algorithm."""
    mdsa_snn = nx.DiGraph()
    degree_indices = get_max_degree_index_per_node_index(
        input_graph=input_graph
    )
    # Create connecting node.
    create_connector_node(
        mdsa_snn=mdsa_snn,
        plot_config=plot_config,
        run_config=run_config,
    )

    # Create spike_once nodes.
    create_spike_once_node(
        degree_indices=degree_indices,
        input_graph=input_graph,
        mdsa_snn=mdsa_snn,
        plot_config=plot_config,
        run_config=run_config,
    )

    create_degree_receiver_node(
        degree_indices=degree_indices,
        input_graph=input_graph,
        mdsa_snn=mdsa_snn,
        plot_config=plot_config,
        run_config=run_config,
    )

    # Create random spike nodes.
    create_rand_node(
        degree_indices=degree_indices,
        input_graph=input_graph,
        mdsa_snn=mdsa_snn,
        plot_config=plot_config,
        run_config=run_config,
    )

    # Create selector nodes.
    create_selector_node(
        degree_indices=degree_indices,
        input_graph=input_graph,
        mdsa_snn=mdsa_snn,
        plot_config=plot_config,
        run_config=run_config,
    )

    # Create selector nodes.
    create_counter_node(
        degree_indices=degree_indices,
        input_graph=input_graph,
        mdsa_snn=mdsa_snn,
        plot_config=plot_config,
        run_config=run_config,
    )

    create_next_round_node(
        mdsa_snn=mdsa_snn,
        nr_of_nodes=len(input_graph.nodes),
        plot_config=plot_config,
        run_config=run_config,
    )

    create_terminator_node(
        mdsa_snn=mdsa_snn,
        nr_of_nodes=len(input_graph.nodes),
        plot_config=plot_config,
        run_config=run_config,
    )

    return mdsa_snn


@typechecked
def create_connector_node(
    *,
    mdsa_snn: nx.DiGraph,
    plot_config: Plot_config,
    run_config: Run_config,
) -> None:
    """Creates the neuron settings for the connecting node in the MDSA
    algorithm."""
    connecting_xy = tuple(
        get_node_position(
            node_name="connecting",
            identifiers=[],
            plot_config=plot_config,
            run_config=run_config,
        )
    )
    lif_neuron = LIF_neuron(
        name="connector_node",
        bias=0.0,
        du=0.0,
        dv=0.0,
        vth=1.0,
        pos=connecting_xy,
    )
    mdsa_snn.add_node(lif_neuron.full_name)
    mdsa_snn.nodes[lif_neuron.full_name]["nx_lif"] = [lif_neuron]


@typechecked
def create_spike_once_node(
    *,
    degree_indices: Dict[int, int],
    input_graph: nx.Graph,
    mdsa_snn: nx.DiGraph,
    plot_config: Plot_config,
    run_config: Run_config,
) -> None:
    """Creates the neuron settings for the spike_once node in the MDSA
    algorithm."""
    for node_index in input_graph.nodes:
        identifiers: List = [
            Identifier(
                description="node_index",
                position=0,
                value=node_index,
            )
        ]
        spike_once_xy = tuple(
            get_node_position(
                node_name="spike_once",
                plot_config=plot_config,
                identifiers=identifiers,
                run_config=run_config,
                degree_indices=degree_indices,
            )
        )
        lif_neuron = LIF_neuron(
            name="spike_once",
            bias=2.0,
            du=0.0,
            dv=0.0,
            vth=1.0,
            pos=spike_once_xy,
            identifiers=identifiers,
        )

        mdsa_snn.add_node(lif_neuron.full_name)
        mdsa_snn.nodes[lif_neuron.full_name]["nx_lif"] = [lif_neuron]


# pylint: disable=R0913
@typechecked
def create_degree_receiver_node(
    *,
    degree_indices: Dict[int, int],
    input_graph: nx.Graph,
    mdsa_snn: nx.DiGraph,
    plot_config: Plot_config,
    run_config: Run_config,
) -> None:
    """Creates the neuron settings for the spike_once node in the MDSA
    algorithm."""
    # pylint: disable=R0801
    # Create degree_receiver nodes.
    for m_val in range(0, run_config.algorithm["MDSA"]["m_val"] + 1):
        for node_index in input_graph.nodes:
            degree_index: int = 0
            for node_neighbour in nx.all_neighbors(input_graph, node_index):
                if node_index != node_neighbour:
                    identifiers = [
                        Identifier(
                            description="node_index",
                            position=0,
                            value=node_index,
                        ),
                        Identifier(
                            description="neighbour_index",
                            position=1,
                            value=node_neighbour,
                        ),
                        Identifier(
                            description="m_val",
                            position=2,
                            value=m_val,
                        ),
                    ]
                    degree_receiver_xy = tuple(
                        get_node_position(
                            node_name="degree_receiver",
                            plot_config=plot_config,
                            identifiers=identifiers,
                            run_config=run_config,
                            m_val_max=run_config.algorithm["MDSA"]["m_val"],
                            degree_index=degree_index,
                            degree_indices=degree_indices,
                        )
                    )

                    lif_neuron = LIF_neuron(
                        name="degree_receiver",
                        bias=0.0,
                        du=0.0,
                        dv=1.0,
                        vth=1.0,
                        pos=degree_receiver_xy,
                        identifiers=identifiers,
                        custom_props={"degree_index": degree_index},
                    )
                    degree_index = degree_index + 1
                    mdsa_snn.add_node(lif_neuron.full_name)
                    mdsa_snn.nodes[lif_neuron.full_name]["nx_lif"] = [
                        lif_neuron
                    ]


@typechecked
def get_max_degree_index_per_node_index(
    *,
    input_graph: nx.Graph,
) -> Dict[int, int]:
    """Returns how many degree_receiver nodes exist within a single node
    circuit."""
    degree_indices: Dict[int, int] = {}
    for node_index in input_graph.nodes:
        degree_indices[node_index] = 0
        for node_neighbour in nx.all_neighbors(input_graph, node_index):
            if node_index != node_neighbour:
                degree_indices[node_index] = degree_indices[node_index] + 1
    return degree_indices


@typechecked
def create_rand_node(
    *,
    degree_indices: Dict[int, int],
    input_graph: nx.Graph,
    mdsa_snn: nx.DiGraph,
    plot_config: Plot_config,
    run_config: Run_config,
) -> None:
    """Creates the neuron settings for the rand node in the MDSA algorithm."""
    for node_index in input_graph.nodes:
        identifiers = [
            Identifier(
                description="node_index",
                position=0,
                value=node_index,
            ),
        ]
        rand_xy = tuple(
            get_node_position(
                node_name="rand",
                plot_config=plot_config,
                identifiers=identifiers,
                run_config=run_config,
                degree_indices=degree_indices,
            )
        )
        lif_neuron = LIF_neuron(
            name="rand",
            bias=2.0,
            du=0.0,
            dv=0.0,
            vth=1.0,
            pos=rand_xy,
            identifiers=identifiers,
        )
        mdsa_snn.add_node(lif_neuron.full_name)
        mdsa_snn.nodes[lif_neuron.full_name]["nx_lif"] = [lif_neuron]


@typechecked
def create_selector_node(
    *,
    degree_indices: Dict[int, int],
    input_graph: nx.Graph,
    mdsa_snn: nx.DiGraph,
    plot_config: Plot_config,
    run_config: Run_config,
) -> None:
    """Creates the neuron settings for the selector node in the MDSA
    algorithm."""
    for node_index in input_graph.nodes:
        for m_val in range(0, run_config.algorithm["MDSA"]["m_val"] + 1):
            # This is probably for the delay in activation for m>0.
            vth: float = 4.0
            bias: float
            if m_val == 0:
                # The selector should fire at the timestep if m=0.
                bias = vth + 1
            else:
                # for m>0, the selector should not fire until it has an input
                # spike from the next_round neuron, hence the lower bias, equal
                # to the threshold.
                bias = vth

            identifiers = [
                Identifier(
                    description="node_index",
                    position=0,
                    value=node_index,
                ),
                Identifier(description="m_val", position=1, value=m_val),
            ]

            selector_xy = tuple(
                get_node_position(
                    node_name="selector",
                    identifiers=identifiers,
                    plot_config=plot_config,
                    run_config=run_config,
                    m_val_max=run_config.algorithm["MDSA"]["m_val"],
                    degree_indices=degree_indices,
                )
            )

            lif_neuron = LIF_neuron(
                name="selector",
                bias=bias,
                du=0.0,
                dv=1.0,
                vth=vth,
                pos=selector_xy,
                identifiers=identifiers,
            )
            mdsa_snn.add_node(lif_neuron.full_name)
            mdsa_snn.nodes[lif_neuron.full_name]["nx_lif"] = [lif_neuron]


@typechecked
def create_counter_node(
    *,
    degree_indices: Dict[int, int],
    input_graph: nx.Graph,
    mdsa_snn: nx.DiGraph,
    plot_config: Plot_config,
    run_config: Run_config,
) -> None:
    """Creates the neuron settings for the counter node in the MDSA
    algorithm."""
    for node_index in input_graph.nodes:
        identifiers = [
            Identifier(
                description="node_index",
                position=0,
                value=node_index,
            ),
        ]

        counter_xy = tuple(
            get_node_position(
                node_name="counter",
                plot_config=plot_config,
                identifiers=identifiers,
                run_config=run_config,
                m_val_max=run_config.algorithm["MDSA"]["m_val"],
                degree_indices=degree_indices,
            )
        )

        lif_neuron = LIF_neuron(
            name="counter",
            bias=0.0,
            du=0.0,
            dv=1.0,
            vth=0.0,
            pos=counter_xy,
            identifiers=identifiers,
        )
        mdsa_snn.add_node(lif_neuron.full_name)
        mdsa_snn.nodes[lif_neuron.full_name]["nx_lif"] = [lif_neuron]


@typechecked
def create_next_round_node(
    *,
    mdsa_snn: nx.DiGraph,
    nr_of_nodes: int,
    plot_config: Plot_config,
    run_config: Run_config,
) -> None:
    """Creates the neuron settings for the counter node in the MDSA algorithm.

    TODO: Change properties to accept a_in of size n, to make it spike,
    and then still allow it to spike at t+1 for redundancy.
    """
    # NOTE, for loop starts at index 1, instead of 0!
    for m_val in range(1, run_config.algorithm["MDSA"]["m_val"] + 1):
        identifiers = [
            Identifier(description="m_val", position=0, value=m_val),
        ]
        next_round_xy = tuple(
            get_node_position(
                node_name="next_round",
                plot_config=plot_config,
                identifiers=identifiers,
                run_config=run_config,
                # m_val=m_val - 1,
                m_val_max=run_config.algorithm["MDSA"]["m_val"] + 1,
            )
        )
        lif_neuron = LIF_neuron(
            name="next_round",
            bias=0.0,
            du=0.0,
            dv=1.0,
            vth=float(nr_of_nodes) - 1,
            pos=next_round_xy,
            identifiers=identifiers,
        )
        mdsa_snn.add_node(lif_neuron.full_name)
        mdsa_snn.nodes[lif_neuron.full_name]["nx_lif"] = [lif_neuron]


@typechecked
def create_terminator_node(
    *,
    mdsa_snn: nx.DiGraph,
    nr_of_nodes: int,
    plot_config: Plot_config,
    run_config: Run_config,
) -> None:
    """T800 node that stops the spiking neural network from proceeding, once
    the algorithm is completed.

    Ensures it will not start learning at the geometric rate.
    """
    terminator_xy = tuple(
        get_node_position(
            node_name="terminator",
            plot_config=plot_config,
            identifiers=[],
            run_config=run_config,
            m_val_max=run_config.algorithm["MDSA"]["m_val"],
        )
    )

    lif_neuron = LIF_neuron(
        name="terminator_node",
        bias=0.0,
        du=0.0,
        dv=1.0,
        vth=float(nr_of_nodes) - 1,
        pos=terminator_xy,
    )
    mdsa_snn.add_node(lif_neuron.full_name)
    mdsa_snn.nodes[lif_neuron.full_name]["nx_lif"] = [lif_neuron]
