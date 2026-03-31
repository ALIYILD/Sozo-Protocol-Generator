from pydantic import BaseModel, Field
from typing import Optional


class ColorPalette(BaseModel):
    primary_brown: str = "#996600"
    primary_blue: str = "#2E75B6"
    dark_blue: str = "#1B3A5C"
    accent_red: str = "#CC0000"
    light_gray: str = "#F2F2F2"
    medium_gray: str = "#999999"
    dark_gray: str = "#666666"
    white: str = "#FFFFFF"
    black: str = "#000000"
    warning_orange: str = "#FF8C00"
    highlight_yellow: str = "#FFFF99"


class FontConfig(BaseModel):
    heading: str = "Calibri"
    body: str = "Calibri"
    monospace: str = "Courier New"
    h1_size: int = 16
    h2_size: int = 14
    h3_size: int = 12
    body_size: int = 11
    small_size: int = 9
    caption_size: int = 8


class BrandingConfig(BaseModel):
    organization: str = "SOZO Brain Center"
    tagline: str = "Evidence-Based Neuromodulation"
    copyright_year: int = 2026
    confidentiality_statement: str = (
        "CONFIDENTIAL \u2014 For authorized SOZO personnel only. Not for distribution."
    )
    colors: ColorPalette = Field(default_factory=ColorPalette)
    fonts: FontConfig = Field(default_factory=FontConfig)
    fellow_tier_label: str = "FELLOW TIER"
    fellow_tier_description: str = "For use by SOZO Fellow clinicians under Doctor supervision"
    partners_tier_label: str = "PARTNERS TIER"
    partners_tier_description: str = "For use by SOZO Partner clinicians \u2014 includes full FNON framework"
