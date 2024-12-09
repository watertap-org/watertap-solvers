import pyomo.environ as pyo
from watertap_solvers import get_solver
from watertap_solvers.model_debug_mode import activate

activate()


m = pyo.ConcreteModel()
m.x = pyo.Var([1, 2], bounds=(0, 1))
m.c = pyo.Constraint(expr=m.x[1] * m.x[2] == -1)

if __name__ == "__main__":
    solver = get_solver()
    solver.solve(m)
