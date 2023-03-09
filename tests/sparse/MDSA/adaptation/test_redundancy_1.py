"""Tests whether the `nth` redundant neuron (with n=1) in the MDSA algorithm
takes over from the died neurons (0 to n-1)."""
# pylint: disable=R0801

import unittest
from pprint import pprint

from snncompare.simulation.stage2_sim import sim_graphs
from typeguard import typechecked

from tests.sparse.MDSA.adaptation.redundancy_helper import (
    assert_redundant_neuron_takes_over,
    get_dead_neuron_names,
    get_run_config_and_results_dicts_for_large_test_scope,
    overwrite_radiation_with_custom,
)


# pylint: disable=R0903
class Test_mdsa(unittest.TestCase):
    """Tests whether MDSA algorithm specification detects invalid
    specifications."""

    # Initialize test object
    def __init__(self, *args, **kwargs) -> None:  # type:ignore[no-untyped-def]
        super().__init__(*args, **kwargs)

    @typechecked
    def test_something(self) -> None:
        """Tests whether the MDSA algorithm with adaptation yields the same
        results as without adaptation."""
        (
            run_config_results,
            output_config,
        ) = get_run_config_and_results_dicts_for_large_test_scope(
            with_adaptation_only=True
        )

        if not run_config_results:
            raise SystemError("Error, no run_configs are tested.")

        for i, (
            run_config,
            original_results_nx_graphs,
        ) in enumerate(run_config_results.items()):
            print(f"run_config ({i}/{len(run_config_results.keys())})=")
            pprint(run_config.__dict__)

            # Generate lists with dead neurons that are to be considered
            # dead during a run. One list contains all the neurons that
            # will be dead due to radiation in a single run_config.
            for dead_neuron_names in get_dead_neuron_names(
                snn_algo_graph=original_results_nx_graphs["graphs_dict"][
                    "snn_algo_graph"
                ],
                redundancy_levels=[0],
            ):
                # Do not test redundancy for counter neuron, because they
                # don't spike.
                # Do not test redundancy for terminator node because it
                # is ok if any of them fire simultaneously, so they are
                # "dumb" copies, not intelligent redundancy.
                if not any(
                    x in dead_neuron_name
                    for dead_neuron_name in dead_neuron_names
                    for x in ["connector", "counter", "terminator"]
                ):
                    results_nx_graphs = overwrite_radiation_with_custom(
                        original_results_nx_graphs=original_results_nx_graphs,
                        dead_neuron_names=dead_neuron_names,
                    )

                    # Now that the graphs have been created, simulate them.
                    sim_graphs(
                        run_config=run_config,
                        stage_1_graphs=results_nx_graphs["graphs_dict"],
                    )

                    # Perform actual test.
                    assert_redundant_neuron_takes_over(
                        dead_neuron_names=dead_neuron_names,
                        graphs_dict=results_nx_graphs["graphs_dict"],
                        output_config=output_config,
                        max_redundancy=list(run_config.adaptation.values())[0],
                        run_config=run_config,
                        test_object=self,
                    )

                    # TODO: also assert the radiation graph passes.
                    # This is to verify unexpected artifacts, like a redundant
                    # degree receiver node that keeps on spiking, do not still
                    # render erroneous results after adaptation has taken over.