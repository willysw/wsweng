# Where to put this stuff?

```python
    def fe(self, theta: float = 90.0) -> float:
        """_summary_

        Parameters
        ----------
        theta : float, optional
            Angle of dowel load relative to grain, by default 90.0 degrees.
        """
#     If D < 0.25 Then
#         FE = 16600 * (G ^ 1.84)
        if self.deff < 0.25:
            return 16600.0*(self.g**1.84)

#     Else
#         FEII = 11200 * G
#         FET = (6100 * (G ^ 1.45)) / Math.Sqr(D)
#         rTheta = 3.14159265359 * Theta / 180
#         FE = (FEII * FET) / (FEII * (Math.Sin(rTheta) ^ 2) + FET * (Math.Cos(rTheta) ^ 2))
        else:
            fe_ii = 11200.0*self.g
            fe_t = (6100.0*(self.g**1.45))/math.sqrt(self.deff)
            return (
                (fe_ii*fe_t)/(fe_ii*(math.sin(math.radians(theta))**2)
                              + fe_t*(math.cos(math.radians(theta))**2))
            )
```
