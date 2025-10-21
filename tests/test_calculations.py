import pytest

from app.calculations import Parameters, compute_results


def find_scenario(results, name):
    for scenario in results["scenarios"]:
        if scenario["name"] == name:
            return scenario
    raise AssertionError(f"Scenario {name!r} not found in results.")


def find_break_even(results, row_name, col_name):
    labels = results["break_even"]["labels"]
    matrix = results["break_even"]["matrix"]
    try:
        row_index = labels.index(row_name)
        col_index = labels.index(col_name)
    except ValueError as exc:
        raise AssertionError(f"Missing scenario in break-even labels: {exc}") from exc
    return matrix[row_index][col_index]


def test_energy_calculation_without_wood():
    params = Parameters(
        total_area_m2=0,
        pellet_consumption_tonnes=1.0,
        pellet_price_per_kg=1.0,
        pellet_price_growth_rate_percent=0.0,
        pellet_energy_density_kwh_per_kg=4.0,
        old_boiler_efficiency_percent=100.0,
        new_boiler_efficiency_percent=100.0,
        wood_consumption_stere=0.0,
        wood_price_per_stere=0.0,
        wood_price_growth_rate_percent=0.0,
        wood_stove_efficiency_percent=100.0,
        maintenance_cost_per_year=0.0,
        maintenance_growth_rate_percent=0.0,
        electric_price_per_kwh=0.2,
        electric_price_growth_rate_percent=0.0,
        electric_subscription_increase_per_month=0.0,
        electric_subscription_growth_rate_percent=0.0,
        analysis_years=3,
        new_boiler_cost=0.0,
        radiator_cost_per_kw=0.0,
        design_power_density_w_per_m2=0.0,
        radiator_install_extra_cost=0.0,
    )

    results = compute_results(params)
    energy = results["energy"]

    assert energy["pellet_energy_input_kwh"] == pytest.approx(4000.0)
    assert energy["pellet_heat_delivered_kwh"] == pytest.approx(4000.0)
    assert energy["wood_heat_delivered_kwh"] == pytest.approx(0.0)
    assert energy["total_heat_demand_kwh"] == pytest.approx(4000.0)
    assert energy["pellet_mass_new_without_wood_kg"] == pytest.approx(1000.0)
    assert energy["electric_needed_total_kwh"] == pytest.approx(4000.0)

    radiator_elec = find_scenario(results, "Radiateurs électriques seuls")
    assert radiator_elec["capex"] == 0.0
    assert radiator_elec["first_year_cost"] == pytest.approx(800.0)
    assert radiator_elec["horizon_cost"] == pytest.approx(800.0 * 3)
    assert radiator_elec["total_horizon_cost"] == pytest.approx(800.0 * 3)


def test_subscription_increase_is_applied():
    params = Parameters(
        total_area_m2=0,
        pellet_consumption_tonnes=0.0,
        pellet_price_per_kg=1.0,
        pellet_price_growth_rate_percent=0.0,
        pellet_energy_density_kwh_per_kg=4.0,
        old_boiler_efficiency_percent=100.0,
        new_boiler_efficiency_percent=100.0,
        wood_consumption_stere=0.0,
        wood_price_per_stere=0.0,
        wood_price_growth_rate_percent=0.0,
        wood_stove_efficiency_percent=100.0,
        maintenance_cost_per_year=0.0,
        maintenance_growth_rate_percent=0.0,
        electric_price_per_kwh=0.0,
        electric_price_growth_rate_percent=0.0,
        electric_subscription_increase_per_month=10.0,
        electric_subscription_growth_rate_percent=0.0,
        analysis_years=2,
        new_boiler_cost=0.0,
        radiator_cost_per_kw=0.0,
        design_power_density_w_per_m2=0.0,
        radiator_install_extra_cost=0.0,
    )

    results = compute_results(params)
    radiator_elec = find_scenario(results, "Radiateurs électriques seuls")

    assert radiator_elec["first_year_cost"] == pytest.approx(120.0)
    assert radiator_elec["horizon_cost"] == pytest.approx(120.0 * 2)


def test_break_even_indicates_radiators_are_cheaper():
    params = Parameters(
        total_area_m2=100,
        pellet_consumption_tonnes=2.0,
        pellet_price_per_kg=0.5,
        pellet_price_growth_rate_percent=0.0,
        pellet_energy_density_kwh_per_kg=4.5,
        old_boiler_efficiency_percent=90.0,
        new_boiler_efficiency_percent=90.0,
        wood_consumption_stere=0.0,
        wood_price_per_stere=0.0,
        wood_price_growth_rate_percent=0.0,
        wood_stove_efficiency_percent=100.0,
        maintenance_cost_per_year=0.0,
        maintenance_growth_rate_percent=0.0,
        electric_price_per_kwh=0.05,
        electric_price_growth_rate_percent=0.0,
        electric_subscription_increase_per_month=0.0,
        electric_subscription_growth_rate_percent=0.0,
        analysis_years=5,
        new_boiler_cost=5000.0,
        radiator_cost_per_kw=100.0,
        design_power_density_w_per_m2=50.0,
        radiator_install_extra_cost=0.0,
    )

    results = compute_results(params)

    # Radiateurs électriques seuls should be immediately cheaper than a new boiler without the stove.
    cell = find_break_even(
        results,
        "Radiateurs électriques seuls",
        "Chaudière neuve sans poêle",
    )

    assert cell["status"] == "ahead"
    assert cell["year"] == 0

    radiator = find_scenario(results, "Radiateurs électriques seuls")
    boiler = find_scenario(results, "Chaudière neuve sans poêle")

    assert radiator["total_horizon_cost"] < boiler["total_horizon_cost"]
