# watertap-solvers

## Getting started (for contributors)

```sh
conda create --yes -n watertap-solvers-dev -c conda-forge python=3.11
conda activate watertap-solvers-dev
conda install -c conda-forge cyipopt
pip install -r requirements-dev.txt

pytest --pyargs watertap_solvers -v
```
