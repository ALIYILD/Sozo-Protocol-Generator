"""Tests for EEG / QEEG data models."""
from __future__ import annotations

import pytest

from sozo_generator.schemas.eeg import (
    AsymmetryIndex,
    BandPower,
    ChannelDeviation,
    EEGBand,
    EEGChannel,
    EEGFeatures,
    EEG_BAND_RANGES,
    QEEGNormativeComparison,
    STANDARD_10_20_CHANNELS,
)


# ── EEGBand enum ──────────────────────────────────────────────────────────


class TestEEGBandEnum:
    def test_all_band_values(self):
        assert EEGBand.DELTA.value == "delta"
        assert EEGBand.THETA.value == "theta"
        assert EEGBand.ALPHA.value == "alpha"
        assert EEGBand.BETA.value == "beta"
        assert EEGBand.HIGH_BETA.value == "high_beta"
        assert EEGBand.GAMMA.value == "gamma"

    def test_band_count(self):
        assert len(EEGBand) == 6


# ── EEG_BAND_RANGES constant ─────────────────────────────────────────────


class TestEEGBandRanges:
    def test_all_bands_have_ranges(self):
        for band in EEGBand:
            assert band in EEG_BAND_RANGES

    def test_delta_range(self):
        low, high = EEG_BAND_RANGES[EEGBand.DELTA]
        assert low == 0.5
        assert high == 4.0

    def test_alpha_range(self):
        low, high = EEG_BAND_RANGES[EEGBand.ALPHA]
        assert low == 8.0
        assert high == 13.0

    def test_ranges_are_ascending(self):
        """Each band's low boundary should be less than its high boundary."""
        for band, (low, high) in EEG_BAND_RANGES.items():
            assert low < high, f"{band.value}: low={low} >= high={high}"

    def test_bands_are_contiguous(self):
        """Each band's high should match the next band's low."""
        ordered = [
            EEGBand.DELTA, EEGBand.THETA, EEGBand.ALPHA,
            EEGBand.BETA, EEGBand.HIGH_BETA, EEGBand.GAMMA,
        ]
        for i in range(len(ordered) - 1):
            _, current_high = EEG_BAND_RANGES[ordered[i]]
            next_low, _ = EEG_BAND_RANGES[ordered[i + 1]]
            assert current_high == next_low


# ── STANDARD_10_20_CHANNELS ──────────────────────────────────────────────


class TestStandard1020Channels:
    def test_has_19_entries(self):
        assert len(STANDARD_10_20_CHANNELS) == 19

    def test_each_channel_has_required_keys(self):
        for ch in STANDARD_10_20_CHANNELS:
            assert "name" in ch
            assert "position_10_20" in ch
            assert "hemisphere" in ch

    def test_hemispheres_are_valid(self):
        valid = {"left", "right", "midline"}
        for ch in STANDARD_10_20_CHANNELS:
            assert ch["hemisphere"] in valid

    def test_known_channels_present(self):
        names = {ch["name"] for ch in STANDARD_10_20_CHANNELS}
        for expected in ["Fp1", "Fp2", "F3", "F4", "Cz", "O1", "O2"]:
            assert expected in names


# ── BandPower validation ─────────────────────────────────────────────────


class TestBandPower:
    def test_valid_band_power(self):
        bp = BandPower(
            band=EEGBand.ALPHA,
            absolute_power=12.5,
            relative_power=0.35,
        )
        assert bp.absolute_power == 12.5

    def test_negative_absolute_power_rejected(self):
        with pytest.raises(Exception, match="[Nn]egative"):
            BandPower(
                band=EEGBand.ALPHA,
                absolute_power=-1.0,
                relative_power=0.3,
            )

    def test_zero_absolute_power_allowed(self):
        bp = BandPower(
            band=EEGBand.DELTA,
            absolute_power=0.0,
            relative_power=0.0,
        )
        assert bp.absolute_power == 0.0

    def test_relative_power_bounds(self):
        with pytest.raises(Exception):
            BandPower(
                band=EEGBand.ALPHA,
                absolute_power=10.0,
                relative_power=1.5,
            )

    def test_relative_power_negative_rejected(self):
        with pytest.raises(Exception):
            BandPower(
                band=EEGBand.ALPHA,
                absolute_power=10.0,
                relative_power=-0.1,
            )

    def test_z_score_optional(self):
        bp = BandPower(
            band=EEGBand.BETA,
            absolute_power=8.0,
            relative_power=0.2,
        )
        assert bp.z_score is None


# ── AsymmetryIndex range ─────────────────────────────────────────────────


class TestAsymmetryIndex:
    def test_valid_asymmetry(self):
        ai = AsymmetryIndex(
            pair="F3-F4",
            band=EEGBand.ALPHA,
            index_value=-0.25,
        )
        assert ai.index_value == -0.25

    def test_boundary_values(self):
        ai_low = AsymmetryIndex(pair="F3-F4", band=EEGBand.ALPHA, index_value=-1.0)
        assert ai_low.index_value == -1.0
        ai_high = AsymmetryIndex(pair="F3-F4", band=EEGBand.ALPHA, index_value=1.0)
        assert ai_high.index_value == 1.0

    def test_below_minus_one_rejected(self):
        with pytest.raises(Exception):
            AsymmetryIndex(pair="F3-F4", band=EEGBand.ALPHA, index_value=-1.1)

    def test_above_one_rejected(self):
        with pytest.raises(Exception):
            AsymmetryIndex(pair="F3-F4", band=EEGBand.ALPHA, index_value=1.1)


# ── EEGFeatures creation ─────────────────────────────────────────────────


class TestEEGFeatures:
    def test_creation(self):
        features = EEGFeatures(
            dominant_frequency=10.0,
            peak_alpha_frequency=9.8,
            frontal_alpha_asymmetry=-0.15,
            theta_beta_ratio=3.2,
            confidence=0.85,
        )
        assert features.dominant_frequency == 10.0
        assert features.confidence == 0.85
        assert features.network_dysfunction_map == {}
        assert features.abnormal_regions == []

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            EEGFeatures(
                dominant_frequency=10.0,
                peak_alpha_frequency=9.8,
                frontal_alpha_asymmetry=0.0,
                theta_beta_ratio=3.0,
                confidence=1.5,
            )


# ── QEEGNormativeComparison.significant_deviations ──────────────────────


class TestQEEGNormativeComparison:
    @pytest.fixture
    def sample_comparison(self):
        return QEEGNormativeComparison(
            database_name="NeuroGuide",
            age_group="30-39",
            eyes_condition="closed",
            deviations=[
                ChannelDeviation(
                    channel_name="F3", band=EEGBand.ALPHA,
                    z_score=-2.5, direction="reduced",
                ),
                ChannelDeviation(
                    channel_name="F4", band=EEGBand.ALPHA,
                    z_score=1.0, direction="normal",
                ),
                ChannelDeviation(
                    channel_name="P3", band=EEGBand.THETA,
                    z_score=3.1, direction="elevated",
                ),
            ],
        )

    def test_significant_deviations_default_threshold(self, sample_comparison):
        sig = sample_comparison.significant_deviations()
        assert len(sig) == 2
        channels = {d.channel_name for d in sig}
        assert "F3" in channels
        assert "P3" in channels

    def test_significant_deviations_custom_threshold(self, sample_comparison):
        sig = sample_comparison.significant_deviations(threshold=3.0)
        assert len(sig) == 1
        assert sig[0].channel_name == "P3"

    def test_channels_by_direction(self, sample_comparison):
        reduced = sample_comparison.channels_by_direction("reduced")
        assert len(reduced) == 1
        assert reduced[0].channel_name == "F3"


# ── ChannelDeviation z-score/direction consistency ────────────────────────


class TestChannelDeviation:
    def test_elevated_with_positive_zscore(self):
        cd = ChannelDeviation(
            channel_name="F3", band=EEGBand.ALPHA,
            z_score=2.5, direction="elevated",
        )
        assert cd.direction == "elevated"

    def test_reduced_with_negative_zscore(self):
        cd = ChannelDeviation(
            channel_name="F3", band=EEGBand.ALPHA,
            z_score=-2.5, direction="reduced",
        )
        assert cd.direction == "reduced"

    def test_elevated_with_large_negative_zscore_rejected(self):
        with pytest.raises(Exception, match="[Ee]levated.*conflicts"):
            ChannelDeviation(
                channel_name="F3", band=EEGBand.ALPHA,
                z_score=-2.0, direction="elevated",
            )

    def test_reduced_with_large_positive_zscore_rejected(self):
        with pytest.raises(Exception, match="[Rr]educed.*conflicts"):
            ChannelDeviation(
                channel_name="F3", band=EEGBand.ALPHA,
                z_score=2.0, direction="reduced",
            )

    def test_normal_direction_any_zscore(self):
        """Normal direction should be accepted regardless of z-score."""
        cd = ChannelDeviation(
            channel_name="Cz", band=EEGBand.BETA,
            z_score=0.5, direction="normal",
        )
        assert cd.direction == "normal"
