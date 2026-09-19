"""
CompliScan LM — Rule Snapshot & Definitions.
"""

from typing import Dict, Any, NamedTuple
from shared.domain.enums import ApplicabilityStatus


RULE_SET_ID = "LMPC-2011-MVP-RULES"
RULE_SET_VERSION = "v1.0"
EVALUATION_VERSION = "v1.0"


class RuleMetadata(NamedTuple):
    domain: str
    citation: str
    title: str
    description: str
    is_conditional: bool = False


CORE_RULES: Dict[str, RuleMetadata] = {
    "manufacturer_identity": RuleMetadata(
        domain="manufacturer_identity",
        citation="Rule 6(1)(a)",
        title="Manufacturer / Packer / Importer Identity",
        description="Name and complete address of the manufacturer, packer, or importer.",
        is_conditional=False,
    ),
    "commodity_name": RuleMetadata(
        domain="commodity_name",
        citation="Rule 6(1)(b)",
        title="Common or Generic Commodity Name",
        description="Common or generic name of the commodity contained in the package.",
        is_conditional=False,
    ),
    "net_quantity": RuleMetadata(
        domain="net_quantity",
        citation="Rule 6(1)(c)",
        title="Net Quantity & Standard Unit",
        description="Net quantity in terms of standard unit of weight, measure, or number.",
        is_conditional=False,
    ),
    "manufacture_packing_date": RuleMetadata(
        domain="manufacture_packing_date",
        citation="Rule 6(1)(d)",
        title="Month & Year of Manufacture / Packing / Import",
        description="Month and year in which the commodity is manufactured, pre-packed, or imported.",
        is_conditional=False,
    ),
    "mrp": RuleMetadata(
        domain="mrp",
        citation="Rule 6(1)(e)",
        title="Maximum Retail Price (MRP)",
        description="Maximum retail price inclusive of all taxes clearly displayed.",
        is_conditional=False,
    ),
    "consumer_care": RuleMetadata(
        domain="consumer_care",
        citation="Rule 6(1)(f)",
        title="Consumer Care Details",
        description="Name, address, telephone number, or email of the person or office to be contacted for consumer grievances.",
        is_conditional=False,
    ),
    "country_of_origin": RuleMetadata(
        domain="country_of_origin",
        citation="Rule 6(1)(da)",
        title="Country of Origin (Imported Commodities)",
        description="Name of the country of origin or manufacture or assembly in case of imported packages (G.S.R. 629(E)).",
        is_conditional=True,
    ),
}

# Standard metric units permitted under Legal Metrology (Packaged Commodities) Rules, 2011 (Rule 11-13)
VALID_STANDARD_UNITS = {
    # Weight
    "g", "gm", "gms", "gram", "grams",
    "kg", "kgs", "kilogram", "kilograms",
    "mg", "mgs", "milligram", "milligrams",
    # Volume
    "ml", "mls", "millilitre", "millilitres", "milliliter", "milliliters",
    "l", "ltr", "ltrs", "litre", "litres", "liter", "liters",
    "cl", "centilitre", "centilitres",
    # Length
    "m", "meter", "meters", "metre", "metres",
    "cm", "centimeter", "centimeters", "centimetre", "centimetres",
    "mm", "millimeter", "millimeters", "millimetre", "millimetres",
    # Area
    "sq m", "sq cm", "sq mm", "sqm", "sqcm", "sqmm",
    # Number / Count
    "n", "no", "nos", "number", "numbers", "u", "unit", "units", "pc", "pcs", "piece", "pieces", "count", "items",
}
