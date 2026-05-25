"""O repositório de conteúdos referentes a esse trabalho
pode ser acessado em: https://www.notion.so/LogiComp-28a52f2869068093abcffeffbed3a2b3"""

#Adicionando as restrições do problema
"""Restrição 1 (R1): A torre i qualquer deve usar uma das frequências dentro de F(1,2,3): frequencia 1 ou frequência 2 ou 
frequência 3;
(Xi,F1) OR (Xi,F2) OR (Xi,F3)"""

"""
Restrição 2 (R2): Se a torre i opera em determinada frequência, ela não pode operar nas demais frequências de F;
{ 
    (~(Xi,F1) OR (~Xi,F2)) 
    AND ((~Xi,F1) OR (~Xi,F3)) 
    AND ((~Xi,F2) OR (~Xi,F3)) 
}
"""

"""
Restriçao 3 (R3): Vizinhanças. Torres vizinhas (i,j) E {V} não podem usar a mesma frequência
PARA TDO (i,j) E {V} AND F={1,2,3}: ~( (Xi,f) AND (Xj,f) )
"""

"""Solução: (R1) AND (R2) AND (R3)"""

##################################################################################################

from z3 import *
import numpy as np

"""PASSO INICIAL: Gerando a topologia de torres GSM
Essa parte está como teste. Até o dia da entrega vamos tentar
gerar a matriz com o numpy a partir de um número n
fornecido pelo usuário"""

n=6
V = [
    (1, 2), (2, 3), (3, 4), (4, 1), # Quadrado central
    (1, 5),                         # Antena da esquerda
    (2, 6)                          # Antena da direita
]

#iniciando o solver para, em seguida, add as restrições:
solver=Solver()
x = {}

#-------------------------------------------------------
#                   RESTRIÇÃO 1
#-------------------------------------------------------

for i in range(1, n+1):
    for f in range(1, 4):  # Frequências 1, 2 e 3
        x[(i, f)] = Bool(f"x_{i}_{f}")

for i in range(1, n+1):
    solver.add(Or(x[(i, 1)], x[(i, 2)], x[(i, 3)]))


#-------------------------------------------------------
#                   RESTRIÇÃO 2
#-------------------------------------------------------

for i in range(1,n+1):
    solver.add(
        And(
            Or(Not(x[(i,1)]), Not(x[(i,2)])),  #(~Xi,F1 OR ~Xi,F2)
            Or(Not(x[(i,1)]), Not(x[(i,3)])),  #(~Xi,F1 OR ~Xi,F3)
            Or(Not(x[(i,2)]), Not(x[(i,3)]))   #(~Xi,F2 OR ~Xi,F3)
        )
    )
    

#-------------------------------------------------------
#                   RESTRIÇÃO 3
#-------------------------------------------------------
for (i, j) in V:
    for f in range(1, 4):
        # ~(Xi,f AND Xj,f) que equivale a: Not(Xi,f) OR Not(Xj,f)
        solver.add(Or(Not(x[(i, f)]), Not(x[(j, f)])))

#-------------------------------------------------------
#                   RESULTADOS
#-------------------------------------------------------
if solver.check() == sat:
    print(f"Com {n} torres, o modelo é satisfatível\n")
    modelo = solver.model()
    
    print("Configuração recomendada:\n")
    for i in range(1, n+1):
        for f in range(1, 4):
            if is_true(modelo[x[(i, f)]]):
                print(f"Torre {i} -> Frequência {f}")
                break
else:
    print(f"Com {n} torres, o modelo é insatisfatível")