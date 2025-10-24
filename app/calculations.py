from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Parameters(BaseModel):
    total_area_m2: float = Field(98.5, ge=0)
    pellet_consumption_tonnes: float = Field(1.5, ge=0)
    pellet_price_per_kg: float = Field(0.30, ge=0)
    pellet_price_growth_rate_percent: float = Field(3.0)
    wood_consumption_stere: float = Field(5.0, ge=0)
    wood_price_per_stere: float = Field(90.0, ge=0)
    wood_price_growth_rate_percent: float = Field(2.0)
    pellet_energy_density_kwh_per_kg: float = Field(4.8, gt=0)
    wood_energy_per_stere_kwh: float = Field(1700.0, gt=0)
    old_boiler_efficiency_percent: float = Field(85.0, gt=0, le=100)
    new_boiler_efficiency_percent: float = Field(95.0, gt=0, le=100)
    wood_stove_efficiency_percent: float = Field(79.0, gt=0, le=100)
    maintenance_cost_per_year: float = Field(250.0, ge=0)
    maintenance_growth_rate_percent: float = Field(2.0)
    electric_price_per_kwh: float = Field(0.15, ge=0)
    electric_price_growth_rate_percent: float = Field(3.0)
    electric_subscription_increase_per_month: float = Field(10.0, ge=0)
    electric_subscription_growth_rate_percent: float = Field(3.0)
    analysis_years: int = Field(30, ge=1, le=50)
    new_boiler_cost: float = Field(18000.0, ge=0)
    radiator_cost_per_kw: float = Field(150.0, ge=0)
    design_power_density_w_per_m2: float = Field(120.0, ge=0)
    radiator_install_extra_cost: float = Field(0.0, ge=0)


@dataclass
class ScenarioSummary:
    """Snapshot of a scenario for presentation."""

    name: str
    capex: float
    annual_costs: List[float]
    cumulative_costs: List[float]

    @property
    def first_year_cost(self) -> float:
        return self.annual_costs[0]

    @property
    def horizon_cost(self) -> float:
        return self.cumulative_costs[-1]

    @property
    def total_horizon_cost(self) -> float:
        return self.capex + self.horizon_cost


def percent_to_rate(percent: float) -> float:
    return percent / 100.0


def project_costs(base_cost: float, growth_rate: float, years: int) -> List[float]:
    """Return yearly costs applying compound growth."""
    return [base_cost * ((1.0 + growth_rate) ** year) for year in range(years)]


def cumulative(values: List[float]) -> List[float]:
    result: List[float] = []
    running_total = 0.0
    for value in values:
        running_total += value
        result.append(running_total)
    return result


def find_break_even(
    capex_a: float,
    annual_a: List[float],
    capex_b: float,
    annual_b: List[float],
) -> Dict[str, object]:
    """Return break-even information describing when option A catches up with option B."""

    diff = capex_a - capex_b
    if diff <= 0:
        # Option A starts ahead on CAPEX.
        return {"status": "ahead", "year": 0}

    for index, (cost_a, cost_b) in enumerate(zip(annual_a, annual_b), start=1):
        diff += cost_a - cost_b
        if diff <= 0:
            return {"status": "payback", "year": index}

    return {"status": "never", "year": None}


def compute_results(params: Parameters) -> Dict[str, object]:
    years = params.analysis_years
    pellet_growth = percent_to_rate(params.pellet_price_growth_rate_percent)
    wood_growth = percent_to_rate(params.wood_price_growth_rate_percent)
    maintenance_growth = percent_to_rate(params.maintenance_growth_rate_percent)
    electric_growth = percent_to_rate(params.electric_price_growth_rate_percent)
    subscription_growth = percent_to_rate(params.electric_subscription_growth_rate_percent)

    old_boiler_eff = percent_to_rate(params.old_boiler_efficiency_percent)
    new_boiler_eff = percent_to_rate(params.new_boiler_efficiency_percent)
    wood_eff = percent_to_rate(params.wood_stove_efficiency_percent)

    pellet_mass_kg = params.pellet_consumption_tonnes * 1000.0
    pellet_energy_input_kwh = pellet_mass_kg * params.pellet_energy_density_kwh_per_kg
    wood_energy_input_kwh = params.wood_consumption_stere * params.wood_energy_per_stere_kwh

    pellet_heat_delivered_kwh = pellet_energy_input_kwh * old_boiler_eff
    wood_heat_delivered_kwh = wood_energy_input_kwh * wood_eff
    total_heat_demand_kwh = pellet_heat_delivered_kwh + wood_heat_delivered_kwh

    pellet_heat_required_with_wood_kwh = max(total_heat_demand_kwh - wood_heat_delivered_kwh, 0.0)
    pellet_energy_input_new_with_wood_kwh = pellet_heat_required_with_wood_kwh / new_boiler_eff
    pellet_mass_new_with_wood_kg = pellet_energy_input_new_with_wood_kwh / params.pellet_energy_density_kwh_per_kg

    pellet_energy_input_new_without_wood_kwh = total_heat_demand_kwh / new_boiler_eff
    pellet_mass_new_without_wood_kg = (
        pellet_energy_input_new_without_wood_kwh / params.pellet_energy_density_kwh_per_kg
    )

    electric_needed_with_wood_kwh = max(total_heat_demand_kwh - wood_heat_delivered_kwh, 0.0)
    electric_needed_total_kwh = total_heat_demand_kwh

    pellet_base_cost_current = pellet_mass_kg * params.pellet_price_per_kg
    pellet_base_cost_new_with_wood = pellet_mass_new_with_wood_kg * params.pellet_price_per_kg
    pellet_base_cost_new_without_wood = pellet_mass_new_without_wood_kg * params.pellet_price_per_kg
    wood_base_cost = params.wood_consumption_stere * params.wood_price_per_stere
    maintenance_base_cost = params.maintenance_cost_per_year
    electric_base_cost_with_wood = electric_needed_with_wood_kwh * params.electric_price_per_kwh
    electric_base_cost_total = electric_needed_total_kwh * params.electric_price_per_kwh
    subscription_base_cost = params.electric_subscription_increase_per_month * 12.0

    pellet_costs_current = project_costs(pellet_base_cost_current, pellet_growth, years)
    pellet_costs_new_with_wood = project_costs(pellet_base_cost_new_with_wood, pellet_growth, years)
    pellet_costs_new_without_wood = project_costs(pellet_base_cost_new_without_wood, pellet_growth, years)
    wood_costs = project_costs(wood_base_cost, wood_growth, years)
    maintenance_costs = project_costs(maintenance_base_cost, maintenance_growth, years)
    electric_costs_with_wood = project_costs(electric_base_cost_with_wood, electric_growth, years)
    electric_costs_total = project_costs(electric_base_cost_total, electric_growth, years)
    subscription_costs = project_costs(subscription_base_cost, subscription_growth, years)

    current_annual_costs = [
        pellet_costs_current[year] + wood_costs[year] + maintenance_costs[year]
        for year in range(years)
    ]
    current_cumulative = cumulative(current_annual_costs)

    annual_new_with_wood = [
        pellet_costs_new_with_wood[year] + wood_costs[year] + maintenance_costs[year]
        for year in range(years)
    ]
    cumulative_new_with_wood = cumulative(annual_new_with_wood)

    annual_new_without_wood = [
        pellet_costs_new_without_wood[year] + maintenance_costs[year] for year in range(years)
    ]
    cumulative_new_without_wood = cumulative(annual_new_without_wood)

    annual_electric_with_wood = [
        wood_costs[year] + electric_costs_with_wood[year] + subscription_costs[year]
        for year in range(years)
    ]
    cumulative_electric_with_wood = cumulative(annual_electric_with_wood)

    annual_electric_total = [
        electric_costs_total[year] + subscription_costs[year] for year in range(years)
    ]
    cumulative_electric_total = cumulative(annual_electric_total)

    radiator_power_kw = (params.total_area_m2 * params.design_power_density_w_per_m2) / 1000.0
    radiator_capex = radiator_power_kw * params.radiator_cost_per_kw + params.radiator_install_extra_cost

    scenarios = [
        ScenarioSummary(
            name="Chaudière neuve + poêle",
            capex=params.new_boiler_cost,
            annual_costs=annual_new_with_wood,
            cumulative_costs=cumulative_new_with_wood,
        ),
        ScenarioSummary(
            name="Chaudière neuve sans poêle",
            capex=params.new_boiler_cost,
            annual_costs=annual_new_without_wood,
            cumulative_costs=cumulative_new_without_wood,
        ),
        ScenarioSummary(
            name="Radiateurs électriques + poêle",
            capex=radiator_capex,
            annual_costs=annual_electric_with_wood,
            cumulative_costs=cumulative_electric_with_wood,
        ),
        ScenarioSummary(
            name="Radiateurs électriques seuls",
            capex=radiator_capex,
            annual_costs=annual_electric_total,
            cumulative_costs=cumulative_electric_total,
        ),
    ]

    break_even_matrix: List[List[Dict[str, object]]] = []
    for idx_a, scenario_a in enumerate(scenarios):
        row: List[Dict[str, object]] = []
        for idx_b, scenario_b in enumerate(scenarios):
            if idx_a == idx_b:
                row.append({"status": "self", "year": 0})
                continue
            row.append(
                find_break_even(
                    scenario_a.capex,
                    scenario_a.annual_costs,
                    scenario_b.capex,
                    scenario_b.annual_costs,
                )
            )
        break_even_matrix.append(row)

    return {
        "energy": {
            "pellet_energy_input_kwh": pellet_energy_input_kwh,
            "pellet_heat_delivered_kwh": pellet_heat_delivered_kwh,
            "wood_heat_delivered_kwh": wood_heat_delivered_kwh,
            "total_heat_demand_kwh": total_heat_demand_kwh,
            "pellet_mass_current_kg": pellet_mass_kg,
            "pellet_mass_new_with_wood_kg": pellet_mass_new_with_wood_kg,
            "pellet_mass_new_without_wood_kg": pellet_mass_new_without_wood_kg,
            "electric_needed_with_wood_kwh": electric_needed_with_wood_kwh,
            "electric_needed_total_kwh": electric_needed_total_kwh,
            "old_boiler_efficiency_percent": params.old_boiler_efficiency_percent,
            "new_boiler_efficiency_percent": params.new_boiler_efficiency_percent,
            "wood_stove_efficiency_percent": params.wood_stove_efficiency_percent,
        },
        "scenarios": [
            {
                "name": summary.name,
                "capex": summary.capex,
                "annual_costs": summary.annual_costs,
                "cumulative_costs": summary.cumulative_costs,
                "first_year_cost": summary.first_year_cost,
                "horizon_cost": summary.horizon_cost,
                "total_horizon_cost": summary.total_horizon_cost,
            }
            for summary in scenarios
        ],
        "investment": {
            "radiator_power_kw": radiator_power_kw,
            "radiator_capex": radiator_capex,
            "boiler_cost": params.new_boiler_cost,
        },
        "break_even": {
            "labels": [summary.name for summary in scenarios],
            "matrix": break_even_matrix,
            "horizon_years": years,
        },
        "current_baseline": {
            "name": "Situation actuelle (chaudière existante + poêle)",
            "annual_costs": current_annual_costs,
            "first_year_cost": current_annual_costs[0],
            "horizon_cost": current_cumulative[-1],
        },
    }
