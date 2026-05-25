"""teste para ver se o z3 está funcionando corretamente
obs.: o codigo foi gerado por i.a."""

from z3 import *
x = Int('x')
y = Int('y')

solver = Solver()
solver.add(x + y > 10)
solver.add(x < 5)

if solver.check() == sat:
    print("Solução encontrada!")
    m = solver.model()
    print(f"x = {m[x]}")
    print(f"y = {m[y]}")

    print("Z3 funcionando corretamente!")
else:
    print("Nenhuma solução encontrada.")