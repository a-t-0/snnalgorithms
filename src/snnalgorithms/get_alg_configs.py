"""Returns a list with all possible algorithm configurations."""
import itertools
from typing import Dict, List

from typeguard import typechecked

from .sparse.DUMMY.DUMMY import DUMMY, DUMMY_config
from .sparse.MDSA.alg_params import MDSA, MDSA_config


@typechecked
def get_algo_configs(*, algo_spec: Dict) -> List[Dict]:
    """Returns a list of MDSA_config objects."""
    algo_configs: List[Dict] = []

    keys = algo_spec["alg_parameters"].keys()
    values = (algo_spec["alg_parameters"][key] for key in keys)
    alg_settings = [
        dict(zip(keys, combination))
        for combination in itertools.product(*values)
    ]

    for algo_config in alg_settings:
        if algo_spec["name"] == "MDSA":
            algo_configs.append(MDSA_config(algo_config).__dict__)
        elif algo_spec["name"] == "DUMMY":
            algo_configs.append(DUMMY_config(algo_config).__dict__)
        else:
            raise NameError(
                f"Algorithm:{algo_spec['name']} not yet supported."
            )
    return algo_configs


@typechecked
def verify_algo_configs(*, algo_name: str, algo_configs: List[Dict]) -> None:
    """Verifies the MDSA algorithm configurations are valid."""
    for algo_config_dict in algo_configs:
        if algo_name == "MDSA":
            mdsa = MDSA([algo_config_dict["m_val"]])
            get_algo_configs(algo_spec=mdsa.__dict__)
        elif algo_name == "DUMMY":
            dummy = DUMMY(
                some_vals=[algo_config_dict["some_val"]],
                other_vals=[algo_config_dict["other_val"]],
            )
            get_algo_configs(algo_spec=dummy.__dict__)
        else:
            raise NameError(f"Algorithm:{algo_name} not yet supported.")
