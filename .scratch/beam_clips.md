# Wood Beam Clips

```python
from functools import partial
from itertools import product
from IPython.display import Markdown
import numpy as np
import pandas as pd
from wsweng.wood.dowels import wood_bolt
```

## Givens

```python
diameters = [0.625, 0.75, 0.875, 1.0]  # Nominal diameter, inches
thicknesses = [3.00, 3.50, 5.125, 5.25, 5.50, 7.0]
bolt_counts = range(2, 7, 1)
spacings = [2.5, 3, 4]
clip_thickness = 1/4.0
species = "DFL"
steel = "A36"
make_bolt = partial(
    wood_bolt,
    full_diameter=False,
    main_material=species,
    side_material=steel,
    side_thickness=clip_thickness
)
```

### Generate design permutations

Find all permutations of diameter, thickness, N and double shear:

```python
p_dia = product(diameters, thicknesses, bolt_counts, spacings, [True, False])
bolts = pd.DataFrame(data=p_dia, columns=["d", "t", "n", "s", "ds"])
bolts.sample(3)
```

<div>

<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>d</th>
      <th>t</th>
      <th>n</th>
      <th>s</th>
      <th>ds</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>342</th>
      <td>0.75</td>
      <td>7.0</td>
      <td>4</td>
      <td>2.5</td>
      <td>True</td>
    </tr>
    <tr>
      <th>701</th>
      <td>1.00</td>
      <td>7.0</td>
      <td>3</td>
      <td>4.0</td>
      <td>False</td>
    </tr>
    <tr>
      <th>592</th>
      <td>1.00</td>
      <td>3.5</td>
      <td>5</td>
      <td>4.0</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>

### Calculate capacity

```python
_z0 = [make_bolt(_d, _t, double_shear=_ds).Zv(theta=90.0)
               for _d, _t, _ds in zip(bolts["d"], bolts["t"], bolts["ds"])]
_c_spcg = np.clip(bolts["s"]/(4*bolts["d"]), 0, 1.0)
bolts["c_spcg"] = np.where(_c_spcg < 0.5, 0, _c_spcg)  # Zero capacity for less than min spacing.
bolts["z"] = bolts["n"]*_c_spcg*_z0
bolts.sample(3)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>d</th>
      <th>t</th>
      <th>n</th>
      <th>s</th>
      <th>ds</th>
      <th>c_spcg</th>
      <th>z</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>461</th>
      <td>0.875</td>
      <td>5.250</td>
      <td>3</td>
      <td>4.0</td>
      <td>False</td>
      <td>1.0</td>
      <td>2637.521747</td>
    </tr>
    <tr>
      <th>327</th>
      <td>0.750</td>
      <td>5.500</td>
      <td>6</td>
      <td>3.0</td>
      <td>False</td>
      <td>1.0</td>
      <td>4111.559732</td>
    </tr>
    <tr>
      <th>628</th>
      <td>1.000</td>
      <td>5.125</td>
      <td>6</td>
      <td>4.0</td>
      <td>True</td>
      <td>1.0</td>
      <td>11630.405782</td>
    </tr>
  </tbody>
</table>
</div>

### Geometry

```python
bolts["h_beam"] = (bolts["n"] - 1)*bolts["s"] + 2*4*bolts["d"]
bolts["h_clip"] = (bolts["n"] - 1)*bolts["s"] + 3.0
bolts["d_end"] = np.clip(1.5*bolts["d"], 1.25, np.inf)

bolts.sample(3)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>d</th>
      <th>t</th>
      <th>n</th>
      <th>s</th>
      <th>ds</th>
      <th>c_spcg</th>
      <th>z</th>
      <th>h_beam</th>
      <th>h_clip</th>
      <th>d_end</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>480</th>
      <td>0.875</td>
      <td>5.5</td>
      <td>2</td>
      <td>2.5</td>
      <td>True</td>
      <td>0.714286</td>
      <td>2524.601164</td>
      <td>9.5</td>
      <td>5.5</td>
      <td>1.3125</td>
    </tr>
    <tr>
      <th>217</th>
      <td>0.750</td>
      <td>3.5</td>
      <td>3</td>
      <td>2.5</td>
      <td>False</td>
      <td>0.833333</td>
      <td>1413.798108</td>
      <td>11.0</td>
      <td>8.0</td>
      <td>1.2500</td>
    </tr>
    <tr>
      <th>398</th>
      <td>0.875</td>
      <td>3.5</td>
      <td>3</td>
      <td>3.0</td>
      <td>True</td>
      <td>0.857143</td>
      <td>3175.040419</td>
      <td>13.0</td>
      <td>9.0</td>
      <td>1.3125</td>
    </tr>
  </tbody>
</table>
</div>

## Schedules

```python
full_sched = bolts.pivot(index=["ds", "s", "d", "n", "h_beam", "h_clip"], columns=["t"], values="z")
display(full_sched.head(3).round(1))
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>t</th>
      <th>3.000</th>
      <th>3.500</th>
      <th>5.125</th>
      <th>5.250</th>
      <th>5.500</th>
      <th>7.000</th>
    </tr>
    <tr>
      <th>ds</th>
      <th>s</th>
      <th>d</th>
      <th>n</th>
      <th>h_beam</th>
      <th>h_clip</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="3" valign="top">False</th>
      <th rowspan="3" valign="top">2.5</th>
      <th rowspan="3" valign="top">0.625</th>
      <th>2</th>
      <th>7.5</th>
      <th>5.5</th>
      <td>889.6</td>
      <td>1004.2</td>
      <td>1021.8</td>
      <td>1021.8</td>
      <td>1021.8</td>
      <td>1021.8</td>
    </tr>
    <tr>
      <th>3</th>
      <th>10.0</th>
      <th>8.0</th>
      <td>1334.4</td>
      <td>1506.3</td>
      <td>1532.7</td>
      <td>1532.7</td>
      <td>1532.7</td>
      <td>1532.7</td>
    </tr>
    <tr>
      <th>4</th>
      <th>12.5</th>
      <th>10.5</th>
      <td>1779.2</td>
      <td>2008.5</td>
      <td>2043.5</td>
      <td>2043.5</td>
      <td>2043.5</td>
      <td>2043.5</td>
    </tr>
  </tbody>
</table>
</div>

```python
def display_sched(d, s):
    _md = ""
    _md += f"#### {d:.3f}\"dia at {s:.2f}\"oc., Single Shear\n\n"
    sched = full_sched.loc[(False, s, d, slice(None))]
    _md += sched.round(1).reset_index(level=("h_beam", "h_clip")).to_markdown()

    _md += "\n\n"
    _md += f"#### {d:.3f}\"dia at {s:.2f}\"oc., Double Shear\n\n"
    sched = full_sched.loc[(True, s, d, slice(None))]
    _md += (sched.round(1).reset_index(level=("h_beam", "h_clip"))).to_markdown()

    _md = _md.replace("h_beam", "Min Beam Height")
    _md = _md.replace("h_clip", "Clip Length")

    return Markdown(_md)
```

### 3/4 Bolts, 3" Spacing

```python
display_sched(0.75, 3)
```
#### 0.750"dia at 3.00"oc., Single Shear

| n | Min Beam Height | Clip Length | 3.0 | 3.5 | 5.125 | 5.25 | 5.5 | 7.0 |
|:---:|:--------:|:--------:|:------:|:------:|:-------:|:------:|:------:|:------:|
|   2 |        9 |        6 | 1005.1 | 1131   |  1370.5 | 1370.5 | 1370.5 | 1370.5 |
|   3 |       12 |        9 | 1507.7 | 1696.6 |  2055.8 | 2055.8 | 2055.8 | 2055.8 |
|   4 |       15 |       12 | 2010.3 | 2262.1 |  2741   | 2741   | 2741   | 2741   |
|   5 |       18 |       15 | 2512.8 | 2827.6 |  3426.3 | 3426.3 | 3426.3 | 3426.3 |
|   6 |       21 |       18 | 3015.4 | 3393.1 |  4111.6 | 4111.6 | 4111.6 | 4111.6 |

#### 0.750"dia at 3.00"oc., Double Shear

| n | Min Beam Height | Clip Length | 3.0 | 3.5 | 5.125 | 5.25 | 5.5 | 7.0 |
|:---:|:--------:|:--------:|:------:|:------:|:-------:|:------:|:------:|:------:|
|   2 |        9 |        6 | 1939.8 | 2263.1 |  2741   | 2741   | 2741   | 2741   |
|   3 |       12 |        9 | 2909.7 | 3394.6 |  4111.6 | 4111.6 | 4111.6 | 4111.6 |
|   4 |       15 |       12 | 3879.6 | 4526.2 |  5482.1 | 5482.1 | 5482.1 | 5482.1 |
|   5 |       18 |       15 | 4849.5 | 5657.7 |  6852.6 | 6852.6 | 6852.6 | 6852.6 |
|   6 |       21 |       18 | 5819.4 | 6789.3 |  8223.1 | 8223.1 | 8223.1 | 8223.1 |
