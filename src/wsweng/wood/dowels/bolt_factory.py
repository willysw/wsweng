from .wood_dowel import WoodDowel

# TODO: Move all this somewhere useful, YAML?
_MATERIALS = {
    "DFL": {"G": 0.50},
    "A36": {"G": 7.80, "FE": 87.0e3},
}
# REF: NDS, 2015 - Appendix L, Table L1
_BOLTS = {
    0.25: {"DR": 0.189, "FYB": 45.0e3},
    0.3125: {"DR": 0.245, "FYB": 45.0e3},
    0.375: {"DR": 0.298, "FYB": 45.0e3},
    0.500: {"DR": 0.406, "FYB": 45.0e3},
    0.625: {"DR": 0.514, "FYB": 45.0e3},
    0.750: {"DR": 0.627, "FYB": 45.0e3},
    0.875: {"DR": 0.739, "FYB": 45.0e3},
    1.000: {"DR": 0.847, "FYB": 45.0e3},
}
_ALIAS = {
    "STEEL": {"A36", "A992", "A572"},
}
# TODO:
#   Catch strings of parsable as numbers as specific
#   gravities. For example, ``material = "0.43"`` --> G=0.43.


def wood_bolt(
    diameter: float,
    main_thickness: float,
    side_thickness: float,
    *,
    main_material: str = "DFL",
    side_material: str = "DFL",
    # helper, sets both main and side if passed.
    material=None,
    full_diameter: bool = False,
    double_shear: bool = False,
) -> WoodDowel:
    """ Create a bolt wood dowel instance.

    Parameters
    ----------
    diameter : float
        Nominal bolt diameter.
    main_thickness : float
        Thickness of main member.
    side_thickness : float
        Thickness of side memeber.
    main_material : str, optional.
        Main member material.
    side_material : str, optional.
        Side member material.
    material : str, optional
        If provided, sets both main and side members, by default `None`.
    full_diameter : bool, optional
        By default `False`.
    double_shear : bool, optional
        By default `False`.

    Returns
    -------
    WoodDowel
    """
    # Bolt Properties
    # TODO: This should have fail-safe behavior if diameter is not found. Next lowest?
    # For now, just assert the value is in the list.
    assert diameter in _BOLTS
    inner_diameter = _BOLTS[diameter]["DR"]
    bending_stress = _BOLTS[diameter]["FYB"]

    # Materials
    if material is not None:
        material_dict = _MATERIALS[material]
        main_specific_gravity = material_dict["G"]
        side_specific_gravity = main_specific_gravity
        main_bearing_stress = material_dict.get("FE", None)
        side_bearing_stress = main_bearing_stress

    else:
        material_dict = _MATERIALS[main_material]
        main_specific_gravity = material_dict["G"]
        main_bearing_stress = material_dict.get("FE", None)

        material_dict = _MATERIALS[side_material]
        side_specific_gravity = material_dict["G"]
        side_bearing_stress = material_dict.get("FE", None)

    # Create dowel.
    return WoodDowel(
        d=diameter,
        dr=inner_diameter,
        lm=main_thickness,
        ls=side_thickness,
        gm=main_specific_gravity,
        gs=side_specific_gravity,
        full_diameter=full_diameter,
        double_shear=double_shear,
        fyb=bending_stress,
        fe_main=main_bearing_stress,
        fe_side=side_bearing_stress,
    )
