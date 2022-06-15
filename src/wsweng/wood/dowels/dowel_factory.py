import pandas as pd
from typing import Any

from wsweng.data import load_csv

from .wood_dowel import WoodDowel

# TODO: Move all this somewhere useful, YAML?
_MATERIALS = {
    "DFL": {"G": 0.50},
    "A36": {"G": 7.80, "FE": 87.0e3},
    "STEEL": {"G": 7.80, "FE": 87.0e3},
}


def _load_bolts() -> pd.DataFrame:
    """ Loads a csv file into a DataFrame mapping nominal diameter
    as a string to a dictionary of parameters.

    ```text
    ID         NAME  TYPE       D     DR      FYB       FU       FY
    ------  ------- -----  ------  -----  -------  -------  -------                                               
    0.2500   1/4 MB  A307  0.2500  0.189  45000.0  58000.0  36000.0
    0.3125  5/16 MB  A307  0.3125  0.245  45000.0  58000.0  36000.0
                                    ...
    ```
    REF: NDS, 2015 - Appendix L, Table L1
    """
    data = load_csv("bolts.csv").reset_index()
    data = data[data["TYPE"] == "A307"].sort_values("D")
    data["ID"] = [f"{di:#.4f}" for di in data["D"]]
    data.set_index("ID", inplace=True)
    return data


_ALIAS = {
    "A36": {"STEEL"},
}
# TODO:
#   Catch strings of parsable as numbers as specific
#   gravities. For example, ``material = "0.43"`` --> G=0.43.


class Dowels:
    """Factory for creating dowels.
    """
    _bolts: pd.DataFrame = None

    def __new__(
        cls,
        d: float,
        *,
        material: str | tuple[str, str] = "DFL",
        dr: float = None,
        fyb: float = 45.0e3,
        tm: float = 1.50,
        ts: float = 1.50,
        w: float = None,
        pt: float = None,
        full_diameter: bool = False,
        double_shear: bool = False,
    ) -> WoodDowel:
        """ Create a generic dowel.

        Parameters
        ----------
        d : float
            _description_
        material : str | (str, str), optional
            If a single specifier is passed, it will be used for both members.
            If a tuple is passed, the specifiers will be used as (main, side).
            By default `DFL`.
        dr : float, optional
            _description_, by default None
        fyb : float, optional
            _description_, by default 45.0e3
        tm : float, optional
            _description_, by default 1.50
        ts : float, optional
            _description_, by default 1.50
        w : float, optional
            _description_, by default None
        pt : float, optional
            _description_, by default None
        full_diameter : bool, optional
            _description_, by default False
        double_shear : bool, optional
            _description_, by default False

        Returns
        -------
        WoodDowel
        """
        mat_data = Dowels._parse_materials(material)
        return WoodDowel(
            d=d,
            dr=dr,
            lm=tm,
            ls=ts,
            gm=mat_data["MAIN"]["G"],
            gs=mat_data["SIDE"]["G"],
            full_diameter=full_diameter,
            double_shear=double_shear,
            fyb=45.0e3,
            fe_main=mat_data["MAIN"]["FE"],
            fe_side=mat_data["SIDE"]["FE"],
        )

    @staticmethod
    def bolt(
        d: float,
        *,
        tm: float,
        ts: float,
        material: str | tuple[str, str] = "DFL",
        full_diameter: bool = False,
        double_shear: bool = False,
    ) -> WoodDowel:
        """ Create a wood bolt.

        Parameters
        ----------
        d : float
            Nominal bolt diameter.
        tm : float
            Thickness of main member.
        ts : float
            Thickness of side memeber.
        material : str | (str, str), optional
            If a single specifier is passed, it will be used for both members.
            If a tuple is passed, the specifiers will be used as (main, side).
            By default `DFL`.
        full_diameter : bool, optional
            By default `False`.
        double_shear : bool, optional
            By default `False`.

        Returns
        -------
        WoodDowel
        """

        if Dowels._bolts is None:
            Dowels._bolts = _load_bolts()

        # Bolt Properties
        # TODO: This should have fail-safe behavior if diameter is not found. Next lowest?
        # For now, just assert the value is in the list.
        bolt_data: pd.Series = Dowels._bolts.loc[f"{d:#.4f}"]
        mat_data = Dowels._parse_materials(material)

        # Create dowel.
        return WoodDowel(
            d=d,
            dr=bolt_data["DR"],
            lm=tm,
            ls=ts,
            gm=mat_data["MAIN"]["G"],
            gs=mat_data["SIDE"]["G"],
            full_diameter=full_diameter,
            double_shear=double_shear,
            fyb=bolt_data["FYB"],
            fe_main=mat_data["MAIN"]["FE"],
            fe_side=mat_data["SIDE"]["FE"],
        )

    # =========================
    # =   PROTECTED METHODS   =
    # =========================

    @staticmethod
    def _parse_materials(
        material: str | tuple[str, str]
    ) -> dict[str, Any]:
        ret_dict = dict()
        if isinstance(material, str):
            ret_dict.update(MAIN=Dowels._parse_one_material(material),
                            SIDE=Dowels._parse_one_material(material))
        else:
            ret_dict.update(MAIN=Dowels._parse_one_material(material[0]),
                            SIDE=Dowels._parse_one_material(material[1]))
        return ret_dict

    @staticmethod
    def _parse_one_material(
        material: str,
    ) -> dict[str, Any]:
        mat_dat = _MATERIALS[material]
        return {
            "G": mat_dat.get("G", 0.50),
            "FE": mat_dat.get("FE", None)
        }
