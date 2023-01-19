"""Tests whether MDSA algorithm specification detects invalid
specifications."""
# pylint: disable=R0801
import copy
import unittest

from snncompare.exp_config.default_setts.create_default_settings import (
    default_exp_config,
)
from snncompare.exp_config.Supported_experiment_settings import (
    Supported_experiment_settings,
)
from snncompare.exp_config.verify_experiment_settings import verify_exp_config
from typeguard import typechecked

from snnalgorithms.get_alg_configs import get_algo_configs, verify_algo_configs
from snnalgorithms.sparse.MDSA.alg_params import MDSA


class Test_mdsa(unittest.TestCase):
    """Tests whether MDSA algorithm specification detects invalid
    specifications."""

    # Initialize test object
    @typechecked
    def __init__(self, *args, **kwargs) -> None:  # type:ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.mdsa = MDSA(list(range(0, 4, 1)))
        self.mdsa_configs = get_algo_configs(self.mdsa.__dict__)
        verify_algo_configs("MDSA", self.mdsa_configs)

        # Create experiment settings.
        self.supp_exp_config = (
            Supported_experiment_settings()
        )  # Needed for verification.
        self.default_exp_config = default_exp_config()
        self.default_exp_config.algorithms["MDSA"] = self.mdsa_configs
        verify_algo_configs("MDSA", self.default_exp_config.algorithms["MDSA"])

    @typechecked
    def test_error_is_thrown_if_m_val_key_is_missing(self) -> None:
        """Verifies an exception is thrown if the m_val key is missing from
        (one of the) the mdsa_configs."""
        # Create deepcopy of configuration settings.
        exp_config = copy.deepcopy(self.default_exp_config)

        # First verify the mdsa_configs are valid.
        verify_exp_config(
            self.supp_exp_config,
            exp_config,
            has_unique_id=False,
            allow_optional=False,
        )

        # Then remove one m_val parameter from a config and assert KeyError is
        # thrown.
        exp_config.algorithms["MDSA"][0].pop("m_val")
        with self.assertRaises(KeyError) as context:
            verify_exp_config(
                self.supp_exp_config,
                exp_config,
                has_unique_id=False,
                allow_optional=False,
            )

        self.assertEqual(
            "'m_val'",
            str(context.exception),
        )

    @typechecked
    def test_error_is_thrown_if_m_val_has_invalid_type(self) -> None:
        """Verifies an exception is thrown if the m_vals key is missing from
        the mdsa configs."""

        # Create deepcopy of configuration settings.
        exp_config = copy.deepcopy(self.default_exp_config)

        # First verify the mdsa_configs are valid.
        verify_exp_config(
            self.supp_exp_config,
            exp_config,
            has_unique_id=False,
            allow_optional=False,
        )

        # Then remove one m_val parameter from a config and assert KeyError is
        # thrown.
        exp_config.algorithms["MDSA"][0]["m_val"] = "somestring"
        with self.assertRaises(TypeError) as context:
            verify_exp_config(
                self.supp_exp_config,
                exp_config,
                has_unique_id=False,
                allow_optional=False,
            )

        self.assertEqual(
            # "m_val is not of type:int. Instead it is of " + f"type:{str}",
            'type of argument "m_vals"[0] must be int; got str instead',
            str(context.exception),
        )

    @typechecked
    def test_error_is_thrown_if_m_val_is_too_large(self) -> None:
        """Verifies an exception is thrown if the m_vals key is too large in
        the mdsa configs."""
        # Create deepcopy of configuration settings.
        exp_config = copy.deepcopy(self.default_exp_config)

        # First verify the mdsa_configs are valid.
        verify_exp_config(
            self.supp_exp_config,
            exp_config,
            has_unique_id=False,
            allow_optional=False,
        )

        # Then remove one m_val parameter from a config and assert KeyError is
        # thrown.
        # self.mdsa_configs[2]["m_val"] = self.mdsa.max_m_vals + 1
        exp_config.algorithms["MDSA"][0]["m_val"] = self.mdsa.max_m_vals + 1
        with self.assertRaises(ValueError) as context:
            verify_exp_config(
                self.supp_exp_config,
                exp_config,
                has_unique_id=False,
                allow_optional=False,
            )

        self.assertEqual(
            (
                "Error, the maximum supported value for m_vals is:"
                + f"{self.mdsa.min_m_vals}, yet we found:"
                + f'{[exp_config.algorithms["MDSA"][0]["m_val"]]}'
            ),
            str(context.exception),
        )

    @typechecked
    def test_error_is_thrown_if_m_val_is_too_low(self) -> None:
        """Verifies an exception is thrown if the m_vals key is too low in the
        mdsa configs."""
        # Create deepcopy of configuration settings.
        exp_config = copy.deepcopy(self.default_exp_config)

        # First verify the mdsa_configs are valid.
        verify_exp_config(
            self.supp_exp_config,
            exp_config,
            has_unique_id=False,
            allow_optional=False,
        )

        # Then remove one m_val parameter from a config and assert KeyError is
        # thrown.
        # self.mdsa_configs[2]["m_val"] = self.mdsa.min_m_vals - 1
        exp_config.algorithms["MDSA"][2]["m_val"] = self.mdsa.min_m_vals - 1
        with self.assertRaises(ValueError) as context:
            verify_exp_config(
                self.supp_exp_config,
                exp_config,
                has_unique_id=False,
                allow_optional=False,
            )

        self.assertEqual(
            (
                "Error, the minimum supported value for m_vals is:"
                + f"{self.mdsa.min_m_vals}, yet we found:"
                + f'{[exp_config.algorithms["MDSA"][2]["m_val"]]}'
            ),
            str(context.exception),
        )
