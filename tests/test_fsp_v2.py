"""FSP v2 rule switches. Defaults must equal FSP v1."""
import unittest

from strategies.failed_swing_point_v2 import RULE_DEFAULTS, FailedSwingPointV2, stop_anchor
from tests.test_fsp import bars
from tvtester.engine import LONG, SHORT


class FSPRuleSwitches(unittest.TestCase):
    def test_defaults_are_feature_1(self):
        self.assertEqual(FailedSwingPointV2().rules, RULE_DEFAULTS)
        self.assertEqual(FailedSwingPointV2().params["tp"], 50)
        self.assertEqual(FailedSwingPointV2().params["stop_search"], False)
        with self.assertRaises(TypeError):
            FailedSwingPointV2(typo=True)

    def test_stop_search_takes_next_extreme_that_passes_left_check(self):
        # HL at bar 0 is high-first, so bar 0's high is excluded; bar 1 is the window max but bar 0 is higher.
        b = bars([(110, 120, 90, 95), (95, 115, 94, 100), (100, 112, 99, 101), (101, 113, 92, 93)])
        self.assertIsNone(stop_anchor(b, 0, 3, SHORT))
        # bar 1 fails (left 120 > 115); next most extreme is bar 3 (113, left 112 <= 113).
        self.assertEqual(stop_anchor(b, 0, 3, SHORT, search=True), (3, 113))
        m = bars([(-o, -l, -h, -c) for o, h, l, c in zip(b.o, b.h, b.l, b.c)])
        self.assertEqual(stop_anchor(m, 0, 3, LONG, search=True), (3, -113))

    def test_search_keeps_default_choice_when_it_passes(self):
        b = bars([(100, 105, 95, 100), (98, 100, 90, 99), (99, 103, 97, 102), (102, 108, 89, 90)])
        self.assertEqual(stop_anchor(b, 1, 3, SHORT, search=True), stop_anchor(b, 1, 3, SHORT))


if __name__ == "__main__":
    unittest.main()
