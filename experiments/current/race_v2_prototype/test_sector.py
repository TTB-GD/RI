import unittest

from .sector import RacePhysiologyTable, resolve_sector, sustainability_balance


TABLE = RacePhysiologyTable(
    speeds=(5, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16),
    ef_energy=1,
    threshold_energy=6,
    vma_energy=12,
)


class SustainabilityBalanceTests(unittest.TestCase):
    def test_initial_credit_is_available_from_start(self):
        self.assertEqual(
            sustainability_balance(
                initial_credit=3, cumulative_form=0, cumulative_consumption=0
            ),
            (0, 3),
        )

    def test_consumption_uses_credit_before_degradation(self):
        self.assertEqual(
            sustainability_balance(
                initial_credit=2, cumulative_form=1, cumulative_consumption=5
            ),
            (2, 0),
        )

    def test_positive_form_restores_existing_degradation(self):
        self.assertEqual(
            sustainability_balance(
                initial_credit=1, cumulative_form=3, cumulative_consumption=5
            ),
            (1, 0),
        )

    def test_negative_form_reduces_available_credit(self):
        self.assertEqual(
            sustainability_balance(
                initial_credit=2, cumulative_form=-2, cumulative_consumption=1
            ),
            (1, 0),
        )


class SectorResolutionTests(unittest.TestCase):
    def test_flat_sector_reads_integer_table_and_consumes_by_as(self):
        result = resolve_sector(
            table=TABLE, energy_result=7, group_bonus=0, terrain_difficulty=0,
            specific_pace=7, initial_credit=2, cumulative_form=0,
            cumulative_consumption=0,
        )
        self.assertEqual(result.energy_spent, 7)
        self.assertEqual(result.conversion_energy, 7)
        self.assertEqual(result.speed, 11)
        self.assertEqual(result.sustainability_consumption, 1)
        self.assertEqual(result.degradation_used, 0)
        self.assertEqual(result.degradation_next, 0)
        self.assertEqual(result.reserve_next, 1)

    def test_group_and_downhill_change_conversion_not_spend(self):
        result = resolve_sector(
            table=TABLE, energy_result=7, group_bonus=1, terrain_difficulty=-2,
            specific_pace=7, initial_credit=0, cumulative_form=0,
            cumulative_consumption=0,
        )
        self.assertEqual(result.energy_spent, 7)
        self.assertEqual(result.conversion_energy, 10)
        self.assertEqual(result.speed, 14)
        self.assertEqual(result.sustainability_consumption, 1)

    def test_uphill_reduces_conversion_without_changing_consumption(self):
        result = resolve_sector(
            table=TABLE, energy_result=8, group_bonus=0, terrain_difficulty=2,
            specific_pace=7, initial_credit=0, cumulative_form=0,
            cumulative_consumption=0,
        )
        self.assertEqual(result.conversion_energy, 6)
        self.assertEqual(result.speed, 10)
        self.assertEqual(result.sustainability_consumption, 1)

    def test_degradation_shifts_curve_right_by_integer_cells(self):
        result = resolve_sector(
            table=TABLE, energy_result=8, group_bonus=0, terrain_difficulty=0,
            specific_pace=7, initial_credit=0, cumulative_form=0,
            cumulative_consumption=2,
        )
        self.assertEqual(result.degradation_used, 2)
        self.assertEqual(result.effective_curve_energy, 6)
        self.assertEqual(result.speed, 10)

    def test_degradation_cannot_push_speed_below_ef(self):
        result = resolve_sector(
            table=TABLE, energy_result=2, group_bonus=0, terrain_difficulty=0,
            specific_pace=7, initial_credit=0, cumulative_form=0,
            cumulative_consumption=20,
        )
        self.assertEqual(result.effective_curve_energy, TABLE.ef_energy)
        self.assertEqual(result.speed, TABLE.ef_speed)

    def test_positive_form_applies_before_current_sector(self):
        result = resolve_sector(
            table=TABLE, energy_result=8, group_bonus=0, terrain_difficulty=0,
            specific_pace=7, initial_credit=0, cumulative_form=3,
            cumulative_consumption=2,
        )
        self.assertEqual(result.degradation_used, 0)
        self.assertEqual(result.speed, 12)

    def test_zero_expenditure_ignores_group_and_terrain(self):
        result = resolve_sector(
            table=TABLE, energy_result=0, group_bonus=1, terrain_difficulty=-5,
            specific_pace=7, initial_credit=3, cumulative_form=0,
            cumulative_consumption=0,
        )
        self.assertEqual(result.speed, 0)
        self.assertEqual(result.energy_spent, 0)
        self.assertEqual(result.sustainability_consumption, 0)

    def test_expenditure_is_capped_at_vma_before_consumption(self):
        result = resolve_sector(
            table=TABLE, energy_result=20, group_bonus=1, terrain_difficulty=0,
            specific_pace=7, initial_credit=0, cumulative_form=0,
            cumulative_consumption=0,
        )
        self.assertEqual(result.energy_spent, 12)
        self.assertEqual(result.conversion_energy, 12)
        self.assertEqual(result.speed, 16)
        self.assertEqual(result.sustainability_consumption, 2)

    def test_consumption_is_deferred_until_next_sector(self):
        result = resolve_sector(
            table=TABLE, energy_result=10, group_bonus=0, terrain_difficulty=0,
            specific_pace=7, initial_credit=0, cumulative_form=0,
            cumulative_consumption=0,
        )
        self.assertEqual(result.degradation_used, 0)
        self.assertEqual(result.speed, 14)
        self.assertEqual(result.degradation_next, 2)


if __name__ == "__main__":
    unittest.main()
