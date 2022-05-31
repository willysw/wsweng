from dataclasses import dataclass, KW_ONLY
from functools import cached_property
import math


@dataclass(frozen=True)
class WoodDowel:
    deff: float
    fem: float
    fes: float
    fyb: float
    lm: float
    ls: float
    _: KW_ONLY
    double_shear: bool = False

    def z(self, theta: float = 90.0) -> float:
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

    # =============================
    # =   Calculated Properties   =
    # =============================

    @cached_property
    def re(self) -> float:
        """ Ratio of main member to side member bearing stress.
        """
        return self.fem/self.fes

    @cached_property
    def rt(self) -> float:
        """ Ratio of main member to side member penetration length
        """
        return self.lm/self.ls

    @cached_property
    def kd(self) -> float:
        """ Diameter constant.
        """
        if self.deff <= 0.17:
            # KD = 2.2
            return 2.2
        else:
            # KD = 10 * D + 0.5
            return 10.0*self.deff + 0.5

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
        if self.deff < 0.25:
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
        return self.deff*self.lm*self.fem/self.rd(4.0, theta)

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
        return self.deff*self.ls*self.fes/self.rd(4.0, theta)

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
        return self.k1*self.deff*self.ls*self.fes/self.rd(3.6, theta)

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
        return (self.k2*self.deff*self.lm*self.fem)/((1 + 2*self.re)*self.rd(3.2, theta))

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
        return (self.k3*self.deff*self.ls*self.fem)/((2 + self.re)*self.rd(3.2, theta))

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
        ziv = (2*self.fem*self.fyb)/(3*(1 + self.re))

        #     ZIV = (D ^ 2) / (RD(D, Theta, 3.2)) * Math.Sqr(ZIV)
        return math.sqrt(ziv)*(self.deff**2)/self.rd(3.2, theta)

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

    @cached_property
    def k1(self) -> float:
        """ constant K1.
        """
        # RE2 = RE ^ 2
        # RT2 = RT ^ 2
        # RE3 = RE ^ 3

        re, rt = self.re, self.rt

        # k1_ = RE + 2 * RE2 * (1 + RT + RT2) + RT2 * RE3
        k1 = re + 2*(re**2)*(1 + rt + rt**2) + (rt**2)*(re**3)

        #     k1_ = Math.Sqr(k1_) - RE * (1 + RT)
        k1 = math.sqrt(k1) - re*(1 + rt)

        #     k1_ = k1_ / (1 + RE)
        return k1/(1 + re)

    @cached_property
    def k2(self) -> float:
        """ Constant K2.
        """
        #     k2_ = 2 * (1 + RE)
        k2 = 2*(1 + self.re)

        #     k2_ = k2_ + (2 * FYB * (1 + 2 * RE) * (D ^ 2)) / (3 * FEM * (LM ^ 2))
        k2 = k2 + (2*self.fyb*(1 + 2*self.re)*(self.deff**2)) / \
            (3*self.fem*(self.lm**2))

        #     k2_ = Math.Sqr(k2_) - 1
        return math.sqrt(k2) - 1

    @cached_property
    def k3(self) -> float:
        """ Constant K3.
        """
        #     k3_ = 2 * (1 + RE) / RE
        k3 = 2*(1 + self.re)/self.re

        #     k3_ = k3_ + (2 * FYB * (2 + RE) * (D ^ 2)) / (3 * FEM * (LS ^ 2))
        k3 = k3 + (2*self.fyb*(2 + self.re)*(self.deff**2)) / \
            (3*self.fem*(self.ls**2))

        #     k3_ = Math.Sqr(k3_) - 1
        return math.sqrt(k3) - 1

    # ======================
    # =   Static Helpers   =
    # ======================

    @staticmethod
    def fe(d: float, g: float = 0.50, theta: float = 90.0) -> float:
        """ Compute effective wood bearing strength.

        Parameters
        ----------
        d : float
            Dowel diameter.
        g : float, optional
            Specific gravity, by default 0.50
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0 degrees.

        Returns
        -------
        float
        """
        if d < 0.25:
            # FE = 16600 * (G ^ 1.84)
            return 16600.0*(g**1.84)

        else:
            # FEII = 11200 * G
            # FET = (6100 * (G ^ 1.45)) / Math.Sqr(D)
            # rTheta = 3.14159265359 * Theta / 180
            # FE = (FEII * FET) / (FEII * (Math.Sin(rTheta) ^ 2) + FET * (Math.Cos(rTheta) ^ 2))
            fe_ii = 11200.0*g
            fe_t = (6100.0*(g**1.45))/math.sqrt(d)
            return (
                (fe_ii*fe_t)/(fe_ii*(math.sin(math.radians(theta))**2)
                              + fe_t*(math.cos(math.radians(theta))**2))
            )
