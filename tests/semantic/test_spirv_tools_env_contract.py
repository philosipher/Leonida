"""Regression coverage for LEONIDA_REQUIRE_SPIRV_TOOLS handling in semantic helpers.

The Windows semantic leg sets LEONIDA_REQUIRE_SPIRV_TOOLS to the string "0".
Python treats a non-empty string as true, so a bare truthy check would demand
spirv-as / spirv-val on a leg where they are optional.  Only the exact string
"1" means the tools are mandatory.

Covers four paths:
- tools missing with unset / "0" / "1";
- tools present with "0": both spirv-as and spirv-val are invoked, the
  translated SOPC module is returned, and validation failures propagate.

All inputs here are synthetic; no game files are read.
"""
import os
import subprocess
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import test_active_cache  # noqa: E402
import test_reg_ptr_hoist  # noqa: E402
import test_sopc_validation  # noqa: E402
import test_unary_f16_validation  # noqa: E402

FAKE_AS = "/fake/spirv-as"
FAKE_VAL = "/fake/spirv-val"


def _fake_which(name):
    return FAKE_AS if name == "spirv-as" else FAKE_VAL


class SpirvToolsEnvContractTests(unittest.TestCase):
    def _helpers(self):
        return (
            ("test_active_cache", test_active_cache._validate_spirv, ("synthetic",)),
            ("test_reg_ptr_hoist", test_reg_ptr_hoist._validate_spirv, ("synthetic",)),
            ("test_unary_f16_validation", test_unary_f16_validation.validate_spirv, ("synthetic",)),
            ("test_sopc_validation", test_sopc_validation._translate_and_validate_cs,
             ("cs_env_contract", ["s_nop 0"], 64)),
        )

    def _env(self, value):
        env = dict(os.environ)
        env.pop("LEONIDA_REQUIRE_SPIRV_TOOLS", None)
        if value is not None:
            env["LEONIDA_REQUIRE_SPIRV_TOOLS"] = value
        return env

    def _check(self, value):
        with mock.patch.dict(os.environ, self._env(value), clear=True), \
                mock.patch("shutil.which", return_value=None), \
                mock.patch.object(test_sopc_validation.rdna2spirv, "translate",
                                  return_value="synthetic"):
            for name, helper, args in self._helpers():
                if value == "1":
                    with self.assertRaises(AssertionError, msg=name):
                        helper(*args)
                else:
                    # Missing tools are optional: the interpreter checks still run and
                    # no AssertionError is raised. The SOPC helper returns the
                    # translated module on this path.
                    result = helper(*args)
                    if name == "test_sopc_validation":
                        self.assertEqual(result, "synthetic")

    def test_unset(self):
        self._check(None)

    def test_zero_string(self):
        self._check("0")

    def test_one_string(self):
        self._check("1")

    def test_tools_present_with_zero_still_validates(self):
        """With tools on PATH, "0" means optional-to-require, not skip-validation."""
        calls = []
        with mock.patch.dict(os.environ, self._env("0"), clear=True), \
                mock.patch("shutil.which", side_effect=_fake_which), \
                mock.patch.object(test_sopc_validation.rdna2spirv, "translate",
                                  return_value="synthetic"), \
                mock.patch("subprocess.run") as run:
            run.return_value = mock.Mock(returncode=0, stderr="")
            for name, helper, args in self._helpers():
                result = helper(*args)
                if name == "test_sopc_validation":
                    self.assertEqual(result, "synthetic")
                calls.extend(c.args[0] for c in run.call_args_list)
                run.reset_mock()

        self.assertEqual(len(calls), 8)
        for i in range(0, len(calls), 2):
            self.assertEqual(calls[i][0], FAKE_AS)
            self.assertEqual(calls[i + 1][0], FAKE_VAL)
            self.assertIn("--target-env", calls[i])
            self.assertIn("--target-env", calls[i + 1])

    def test_tools_present_with_zero_propagates_validation_failure(self):
        """A validator failure is never swallowed just because tools are optional."""
        with mock.patch.dict(os.environ, self._env("0"), clear=True), \
                mock.patch("shutil.which", side_effect=_fake_which), \
                mock.patch.object(test_sopc_validation.rdna2spirv, "translate",
                                  return_value="synthetic"):
            for name, helper, args in self._helpers():
                calls = []

                def run(cmd, **kwargs):
                    calls.append(cmd)
                    if cmd[0] != FAKE_VAL:
                        return mock.Mock(returncode=0, stderr="")
                    if name in ("test_active_cache", "test_reg_ptr_hoist"):
                        raise subprocess.CalledProcessError(1, cmd)
                    return mock.Mock(returncode=1, stderr="bad module")

                with mock.patch("subprocess.run", side_effect=run):
                    if name in ("test_active_cache", "test_reg_ptr_hoist"):
                        with self.assertRaises(subprocess.CalledProcessError, msg=name):
                            helper(*args)
                    else:
                        with self.assertRaises(AssertionError, msg=name):
                            helper(*args)
                self.assertEqual(len(calls), 2, name)
                self.assertEqual(calls[0][0], FAKE_AS)
                self.assertEqual(calls[1][0], FAKE_VAL)


if __name__ == "__main__":
    unittest.main()
