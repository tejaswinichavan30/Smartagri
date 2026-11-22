"""
Unit Tests for Dharwad Agronomy Fixes (Bugs 1-7)
Testing Date: 17 Nov 2026
Target District: Dharwad, Karnataka
"""

import json
import os
import sys
from datetime import date
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.agri_calendar_service import (
    get_sowing_status,
    compute_harvest_range,
    load_msp_config,
    get_msp_for_crop,
    load_sowing_config
)
import translations
from app import compute_price_forecast, KARNATAKA_DISTRICT_SEASON_CROPS


FIXED_TEST_DATE = date(2026, 11, 17)
CURRENT_MARKETING_SEASON = "2026-27"


class TestMspLookupAndConfig:
    """Bug 1: Unit tests for Government MSP configuration and validation."""

    def test_msp_config_file_exists_and_valid(self):
        config_path = os.path.join("data", "msp_config.json")
        assert os.path.exists(config_path), f"Missing config file at {config_path}"
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "commodities" in data
        assert data.get("current_marketing_year") == CURRENT_MARKETING_SEASON

    def test_jowar_msp_2026_27_ccea_approved_rates(self):
        """Verify Jowar MSP is updated to Kharif 2026-27 rates (₹4023 / ₹4073)."""
        msp_entry = get_msp_for_crop("jowar")
        assert msp_entry is not None, "MSP entry for Jowar not found"
        
        # Verify marketing season is 2026-27
        season = msp_entry.get("marketing_season", "")
        assert CURRENT_MARKETING_SEASON in season, f"Expected {CURRENT_MARKETING_SEASON}, found {season}"

        # Verify variety pricing
        varieties = msp_entry.get("varieties", {})
        hybrid_info = varieties.get("Hybrid", {})
        maldandi_info = varieties.get("Maldandi (White)", {})
        
        assert hybrid_info.get("msp_per_quintal") == 4023.00, f"Expected Hybrid ₹4023, got {hybrid_info.get('msp_per_quintal')}"
        assert maldandi_info.get("msp_per_quintal") == 4073.00, f"Expected Maldandi ₹4073, got {maldandi_info.get('msp_per_quintal')}"
        
        # Verify previous year rates (2025-26: ₹3699 / ₹3749)
        assert hybrid_info.get("previous_year_msp") == 3699.00
        assert maldandi_info.get("previous_year_msp") == 3749.00

        # Verify default price matches Hybrid
        assert msp_entry.get("msp_per_quintal") == 4023.00

        # Verify provenance flags: static reference, last verified date
        assert msp_entry.get("is_live_fetched") is False
        assert "last_verified" in msp_entry
        assert "source_url" in msp_entry

    def test_rabi_crops_msp_2026_27(self):
        """Verify Rabi 2026-27 MSP: Wheat ₹2,585, Gram (Chickpea) ₹5,875."""
        wheat = get_msp_for_crop("wheat")
        assert wheat is not None
        assert wheat.get("msp_per_quintal") == 2585.00
        assert CURRENT_MARKETING_SEASON in wheat.get("marketing_season", "")

        chickpea = get_msp_for_crop("chickpea")
        assert chickpea is not None
        assert chickpea.get("msp_per_quintal") == 5875.00
        assert CURRENT_MARKETING_SEASON in chickpea.get("marketing_season", "")

    def test_msp_fails_if_older_than_current_marketing_season(self):
        """Ensure test fails if any configured MSP is older than 2026-27."""
        config = load_msp_config()
        commodities = config.get("commodities", {})
        for crop_key, info in commodities.items():
            season = info.get("marketing_season", "")
            assert CURRENT_MARKETING_SEASON in season, (
                f"Crop '{crop_key}' has outdated MSP season '{season}'. Must be {CURRENT_MARKETING_SEASON}."
            )
            assert info.get("msp_per_quintal", 0) > 0, (
                f"Crop '{crop_key}' has zero or missing MSP."
            )


class TestSowingStatusAndCalendar:
    """Bug 3: Shared getSowingStatus function with fixed date 17 Nov 2026."""

    def test_rabi_jowar_dharwad_status_is_passed(self):
        """On 17 Nov 2026, Dharwad Rabi Jowar (Sep - Oct 31) window must be PASSED."""
        status = get_sowing_status("jowar", season="Rabi", today=FIXED_TEST_DATE, district="Dharwad")
        assert status["status"] == "passed", f"Expected 'passed', got {status['status']}"
        assert status["days_difference"] > 0
        assert "passed" in status["warning_en"].lower()
        assert status["warning_kn"] is not None
        assert status["warning_hi"] is not None

    def test_chickpea_dharwad_status_is_passed(self):
        """On 17 Nov 2026, Dharwad Chickpea (Oct 1 - Nov 15) window must be PASSED."""
        status = get_sowing_status("chickpea", season="Rabi", today=FIXED_TEST_DATE, district="Dharwad")
        assert status["status"] == "passed", f"Expected 'passed', got {status['status']}"
        assert status["days_difference"] > 0
        assert "passed" in status["warning_en"].lower()

    def test_wheat_dharwad_status_is_closing_soon(self):
        """On 17 Nov 2026, Dharwad Wheat (Oct 15 - Nov 20) is within 3 days of closing (CLOSING_SOON)."""
        status = get_sowing_status("wheat", season="Rabi", today=FIXED_TEST_DATE, district="Dharwad")
        assert status["status"] == "closing_soon", f"Expected 'closing_soon', got {status['status']}"
        assert 0 <= status["days_difference"] <= 14
        assert "closing soon" in status["warning_en"].lower()

    def test_all_crops_receive_warning_when_passed_or_closing(self):
        """Verify that warnings are provided for every passed or closing crop, not just chickpea."""
        for crop in ["jowar", "chickpea", "wheat"]:
            res = get_sowing_status(crop, season="Rabi", today=FIXED_TEST_DATE, district="Dharwad")
            if res["status"] in ["passed", "closing_soon"]:
                assert res.get("warning_en") or res.get("warning"), f"Warning missing for {crop}"


class TestHarvestDateCalculation:
    """Bug 2 & 4: Harvest dates computed as max(planned_sowing_date, today) + crop duration."""

    def test_rabi_jowar_harvest_range_in_dharwad(self):
        """Rabi jowar on today=2026-11-17: effective sow 17 Nov + 110-130 days -> March-April."""
        harvest = compute_harvest_range("jowar", season="Rabi", district="Dharwad", today=FIXED_TEST_DATE)
        assert ("February" in harvest["harvest_en"] or "March" in harvest["harvest_en"])
        assert "110-130 days" in harvest["harvest_en"]

    def test_wheat_harvest_range_on_test_date(self):
        """
        Requirement 7: Test harvest range for wheat with today = 2026-11-17.
        Effective sow date = max(planned_sow 15 Oct, today 17 Nov) = 17 Nov 2026.
        Duration: 105 - 120 days.
        17 Nov + 105 days = 2 March 2027.
        17 Nov + 120 days = 17 March 2027.
        Harvest range MUST be March (or March-April).
        """
        harvest = compute_harvest_range("wheat", season="Rabi", district="Dharwad", today=FIXED_TEST_DATE)
        assert harvest["effective_sowing_date"] == "2026-11-17"
        assert "March" in harvest["harvest_en"]
        assert "105-120 days" in harvest["harvest_en"]

    def test_tomato_nursery_transplanting_dates(self):
        """Requirement 4: Tomato uses Nursery/transplanting and computes harvest from transplanting duration."""
        harvest = compute_harvest_range("tomato", season="Rabi", district="Dharwad", today=FIXED_TEST_DATE)
        assert "after transplanting" in harvest["harvest_en"]
        assert ("February" in harvest["harvest_en"] or "March" in harvest["harvest_en"])


class TestPrecisionIrrigationOverhaul:
    """Requirement 1 & 7: ETc = ET0 x Kc(stage), stage from DAS, user inputs, stage-based schedule."""

    def test_irrigation_requirement_day0_vs_day60_wheat(self):
        """
        Requirement 7: Irrigation requirement at day 0 vs day 60 for wheat.
        - Day 0 (Initial stage): Kc = 0.30
        - Day 60 (Mid stage - Jointing/Flowering): Kc = 1.15
        - Water requirement at Day 60 must be ~3.8x of Day 0.
        """
        # Day 0: Sowing / Initial germination
        res_day0 = translations.calculate_smart_irrigation(
            crop="wheat",
            days_after_sowing=0,
            temp=24.0,
            humidity=50.0,
            rainfall_mm=0.0,
            district="Dharwad",
            irrigation_type="drip"
        )
        assert res_day0["kc"] == 0.30
        assert res_day0["growth_stage"] == "initial"

        # Day 60: Jointing / Mid-season peak water demand
        res_day60 = translations.calculate_smart_irrigation(
            crop="wheat",
            days_after_sowing=60,
            temp=24.0,
            humidity=50.0,
            rainfall_mm=0.0,
            district="Dharwad",
            irrigation_type="drip"
        )
        assert res_day60["kc"] == 1.15
        assert res_day60["growth_stage"] == "mid"
        
        # ETc must be significantly higher at Day 60 than Day 0
        assert res_day60["etc_mm"] > res_day0["etc_mm"] * 3.5
        assert res_day60["total_litres_day"] > res_day0["total_litres_day"] * 3.5

        # Must mention critical stage recommendation from UAS Dharwad
        assert "UAS Dharwad" in res_day60["critical_stage_info_en"]
        assert ("Jointing" in res_day60["stage_schedule_en"] or "Flowering" in res_day60["stage_schedule_en"])

    def test_irrigation_subtracts_effective_rainfall(self):
        """Verify effective rainfall (Peff) is subtracted from ETc."""
        res_dry = translations.calculate_smart_irrigation(
            crop="wheat",
            days_after_sowing=60,
            temp=24.0,
            humidity=50.0,
            rainfall_mm=0.0,
            district="Dharwad"
        )
        res_rain = translations.calculate_smart_irrigation(
            crop="wheat",
            days_after_sowing=60,
            temp=24.0,
            humidity=50.0,
            rainfall_mm=10.0,
            district="Dharwad"
        )
        assert res_rain["peff_mm"] > 0
        assert res_rain["net_depth_mm"] < res_dry["net_depth_mm"]

    def test_irrigation_user_inputs_custom_flow_and_efficiency(self):
        """User input pump flow (default 10000) and custom efficiency."""
        res = translations.calculate_smart_irrigation(
            crop="wheat",
            days_after_sowing=25,
            pump_flow_rate=12000,
            irrigation_efficiency=85,
            district="Dharwad"
        )
        assert res["pump_flow_rate_per_acre"] == 12000
        assert res["efficiency"] == 0.85
        assert res["efficiency_pct"] == 85


class TestSoybeanExclusion:
    """Requirement 3 & 7: Soybean marked Kharif-only in Dharwad; excluded in Rabi / after September."""

    def test_soybean_excluded_from_dharwad_rabi(self):
        """On 17 Nov 2026 (Rabi season, after September), Dharwad must NOT recommend soybean."""
        dharwad_crops = KARNATAKA_DISTRICT_SEASON_CROPS.get("Dharwad", {})
        rabi_crops = dharwad_crops.get("rabi", [])
        assert "soybean" not in [c.lower() for c in rabi_crops], "Soybean must not be in Dharwad Rabi crops"

        # Check sowing config marks soybean kharif only
        cfg = load_sowing_config().get("crops", {}).get("soybean", {})
        assert "kharif" in cfg
        assert "rabi" not in cfg or cfg.get("kharif", {}).get("is_kharif_only", False)


class TestPriceCardWheatVarietyAndMspWarning:
    """Requirement 5: Wheat variety on price line and explicit warning if trend falls below MSP."""

    def test_wheat_price_line_has_variety(self):
        p_data = compute_price_forecast("wheat", "Dharwad", month=11, year=2026)
        assert "Sharbati" in p_data["spot_clean_en"] or "Durum" in p_data["spot_clean_en"]
        assert "DWR" in p_data["spot_clean_en"] or "Lokwan" in p_data["spot_clean_en"]

    def test_below_msp_warning_generated_when_forecast_below_msp(self):
        """If projected price falls below MSP in any month, explicit warning must be present."""
        # For Jowar or when market is lower than MSP (Jowar MSP is ₹4023 while market is ~3400)
        p_data = compute_price_forecast("jowar", "Dharwad", month=11, year=2026)
        assert p_data["msp"] == 4023.00
        # Average forecast is ~₹3450 which is below MSP ₹4023
        assert "below_msp_warning_en" in p_data
        assert "BELOW Govt MSP" in p_data["forecast_clean_en"]
