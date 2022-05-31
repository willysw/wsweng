from cmath import nan
from dataclasses import dataclass, KW_ONLY
from functools import cached_property
import math


@dataclass(frozen=True)
class WoodDowel:
    """ A dowel-type wood fastener.

    Attributes
    ----------
    d : float
        Fastener outer diameter.
    dr : float
        Fastener inner diameter.
    gm : float
        Main member specific gravity.
    gs : float
        Side member specific gravity.
    fyb : float
        Fastener bending capacity.
    lm : float
        Main member thickness/penetration.
    ls : float
        Side member thickness/penetration.
    w : float | None
        Unit withdrawl capacity. If none, `zw()` will always return `None`.
    pt : float
        Threadded length of penetration of fastener into main member.
    fe_main, fe_side : float | None
        If specified, overrides the fe calculation for the member. Use this for non-wood members
        that have bearing capacities not related to their specific gravities.
    full_diameter : bool
        `False` if fastener has reduced diameter in bearing on wood (i.e. screws). `True` if fastener
        is full diameter in contact with wood. Defaults to `False`.
    double_shear : bool
        `False` if only one side member is fastened to the main member. `True` if a side member is
        connected either side by the same fastener. Defaults to `False`.
    """
    d: float
    _: KW_ONLY
    dr: float = None
    gm: float = 0.50
    gs: float = 0.50
    fyb: float = 45.0e3
    lm: float = 1.50
    ls: float = 1.50
    w: float = None
    pt: float = None
    fe_main: float | None = None
    fe_side: float | None = None
    full_diameter: bool = False
    double_shear: bool = False

    def __post_init__(self) -> None:
        """ Update any missing defaults.
        """
        if self.dr is None:
            object.__setattr__(self, "dr", self.d)
            object.__setattr__(self, "full_diameter", True)

        if self.pt is None:
            object.__setattr__(self, "pt", self.lm)

    def Zv(self, theta: float = 90.0) -> float:
        """ Reference dowel shear capacity.

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0

        Returns
        -------
        float
        """
        if self.double_shear:
            return min(
                self.zim(theta),
                2*self.zis(theta),
                2*self.ziiis(theta),
                2*self.ziv(theta),
            )
        else:
            return min(
                self.zim(theta),
                self.zis(theta),
                self.zii(theta),
                self.ziiim(theta),
                self.ziiis(theta),
                self.ziv(theta),
            )

    def Zw(self) -> float:
        """ Reference dowel withdrawl capacity.

        Returns
        -------
        float
        """
        if self.w is not None:
            return self.w*self.lm
        else:
            return None

    # =============================
    # =   Calculated Properties   =
    # =============================

    @cached_property
    def de(self) -> float:
        """ Effective dowel diameter for use in `Z` computations.
        """
        if self.full_diameter:
            return self.d
        else:
            return self.dr

    @cached_property
    def rt(self) -> float:
        """ Ratio of main member to side member penetration length
        """
        return self.lm/self.ls

    @cached_property
    def kd(self) -> float:
        """ Diameter constant.
        """
        if self.de <= 0.17:
            # KD = 2.2
            return 2.2
        else:
            # KD = 10 * D + 0.5
            return 10.0*self.de + 0.5

    def rd(self, rkt: float, theta: float = 90.0) -> float:
        """_summary_

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0

        Returns
        -------
        float
        """
        if self.de < 0.25:
            # RD = KD(D)
            return self.kd
        else:
            # RD = KTheta(Theta) * RKt
            return self.ktheta(theta)*rkt

    # ============================
    # =   Dowel Mode Equations   =
    # ============================

    def zim(self, theta: float = 90.0) -> float:
        """_summary_

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0

        Returns
        -------
        float
        """
        # ZIM = D * LM * FEM / RD(D, Theta, 4#)
        return self.de*self.lm*self.fem(theta)/self.rd(4.0, theta)

    def zis(self, theta: float = 90.0) -> float:
        """_summary_

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0

        Returns
        -------
        float
        """
        # ZIS = D * LS * FES / RD(D, Theta, 4#)
        return self.de*self.ls*self.fes(theta)/self.rd(4.0, theta)

    def zii(self, theta: float = 90.0) -> float:
        """_summary_

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0

        Returns
        -------
        float
        """
        # ZII = k1 * D * LS * FES / RD(D, Theta, 3.6)
        return self.k1(theta)*self.de*self.ls*self.fes(theta)/self.rd(3.6, theta)

    def ziiim(self, theta: float = 90.0) -> float:
        """_summary_

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0

        Returns
        -------
        float
        """
        # ZIIIM = (k2 * D * LM * FEM) / ((1 + 2 * RE) * RD(D, Theta, 3.2))
        return (
            (self.k2(theta)*self.de*self.lm*self.fem(theta)) /
            ((1 + 2*self.re(theta))*self.rd(3.2, theta))
        )

    def ziiis(self, theta: float = 90.0) -> float:
        """_summary_

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0

        Returns
        -------
        float
        """
        # ZIIIS = (k3 * D * LS * FEM) / ((2 + RE) * RD(D, Theta, 3.2))
        return (
            (self.k3(theta)*self.de*self.ls*self.fem(theta)) /
            ((2 + self.re(theta))*self.rd(3.2, theta))
        )

    def ziv(self, theta: float = 90.0) -> float:
        """_summary_

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0

        Returns
        -------
        float
        """
        #     ZIV = (2 * FEM * FYB) / (3 * (1 + RE))
        ziv = (2*self.fem(theta)*self.fyb)/(3*(1 + self.re(theta)))

        #     ZIV = (D ^ 2) / (RD(D, Theta, 3.2)) * Math.Sqr(ZIV)
        return math.sqrt(ziv)*(self.de**2)/self.rd(3.2, theta)

    # =====================
    # =   Intermediates   =
    # =====================

    @staticmethod
    def ktheta(theta: float = 90.0) -> float:
        """_summary_

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90

        Returns
        -------
        float
        """
        # KTheta = 1 + 0.25 * (Theta / 90)
        return 1.0 + 0.25*(theta/90)

    def k1(self, theta: float = 90.0) -> float:
        """ constant K1.

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90

        Returns
        -------
        float
        """
        # RE2 = RE ^ 2
        # RT2 = RT ^ 2
        # RE3 = RE ^ 3

        _re, _rt = self.re(theta), self.rt

        # k1_ = RE + 2 * RE2 * (1 + RT + RT2) + RT2 * RE3
        k1 = _re + 2*(_re**2)*(1 + _rt + _rt**2) + (_rt**2)*(_re**3)

        #     k1_ = Math.Sqr(k1_) - RE * (1 + RT)
        k1 = math.sqrt(k1) - _re*(1 + _rt)

        #     k1_ = k1_ / (1 + RE)
        return k1/(1 + _re)

    def k2(self, theta: float = 90.0) -> float:
        """ Constant K2.

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0 degrees.

        Returns
        -------
        float
        """
        #     k2_ = 2 * (1 + RE)
        _re = self.re(theta)
        k2 = 2*(1 + _re)

        #     k2_ = k2_ + (2 * FYB * (1 + 2 * RE) * (D ^ 2)) / (3 * FEM * (LM ^ 2))
        k2 = (
            k2 +
            (2*self.fyb*(1 + 2*_re)*(self.de**2)) /
            (3*self.fem(theta)*(self.lm**2))
        )

        #     k2_ = Math.Sqr(k2_) - 1
        return math.sqrt(k2) - 1

    def k3(self, theta: float = 90.0) -> float:
        """ Constant K3.

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0 degrees.

        Returns
        -------
        float
        """
        #     k3_ = 2 * (1 + RE) / RE
        _re = self.re(theta)
        k3 = 2*(1 + _re)/_re

        #     k3_ = k3_ + (2 * FYB * (2 + RE) * (D ^ 2)) / (3 * FEM * (LS ^ 2))
        k3 = (
            k3 +
            (2*self.fyb*(2 + _re)*(self.de**2)) /
            (3*self.fem(theta)*(self.ls**2))
        )

        #     k3_ = Math.Sqr(k3_) - 1
        return math.sqrt(k3) - 1

    def fem(self, theta: float = 90.0) -> float:
        """ Compute effective main member bearing strength.

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0 degrees.

        Returns
        -------
        float
        """
        if self.fe_main is None:
            return self.fe(self.gm, theta)
        else:
            return self.fe_main

    def fes(self, theta: float = 90.0) -> float:
        """ Compute effective side member bearing strength.

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0 degrees.

        Returns
        -------
        float
        """
        if self.fe_side is None:
            return self.fe(self.gs, theta)
        else:
            return self.fe_side

    def fe(self, g: float, theta: float = 90.0) -> float:
        """ Compute effective wood bearing strength.

        Parameters
        ----------
        g : float, optional
            Specific gravity, by default 0.50
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0 degrees.

        Returns
        -------
        float
        """
        if self.d < 0.25:
            # FE = 16600 * (G ^ 1.84)
            return 16600.0*(g**1.84)

        else:
            # FEII = 11200 * G
            # FET = (6100 * (G ^ 1.45)) / Math.Sqr(D)
            # rTheta = 3.14159265359 * Theta / 180
            # FE = (FEII * FET) / (FEII * (Math.Sin(rTheta) ^ 2) + FET * (Math.Cos(rTheta) ^ 2))
            fe_ii = 11200.0*g
            fe_t = (6100.0*(g**1.45))/math.sqrt(self.d)

            return (
                fe_ii*fe_t /
                (
                    fe_ii*(math.sin(math.radians(theta))**2) +
                    fe_t*(math.cos(math.radians(theta))**2)
                )
            )

    def re(self, theta: float) -> float:
        """ Ratio of main member to side member bearing stress.

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0 degrees.

        Returns
        -------
        float
        """
        return self.fem(theta)/self.fes(theta)
