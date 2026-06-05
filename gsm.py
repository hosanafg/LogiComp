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
import random
import networkx as nx
import matplotlib.pyplot as plt

#exportar as tuplas
import csv       
import json      

"""Plotar o gráfico ao final, caso a fórmula seja satisfatível"""
def plotar_grafo_gsm(n, V, frequencias_finais):
    G=nx.Graph()
    G.add_nodes_from(range(1, n + 1))
    G.add_edges_from(V)
    
    mapa_cores={1: "#02243b", 2: "#eb1d8e", 3: "#5ee73c"}
    cores_dos_nos=[mapa_cores[frequencias_finais[node]] for node in G.nodes()]

    plt.figure(figsize=(8, 6))
    plt.title("Torres GSM", fontsize=14, fontweight='bold')
    posicao=nx.spring_layout(G, seed=42) 
    
    nx.draw(
        G, 
        posicao, 
        with_labels=True, 
        node_color=cores_dos_nos, 
        node_size=1000, 
        font_size=12, 
        font_color='white', 
        font_weight='bold', 
        edge_color="#a3abac", 
        width=1
    )

    for freq, cor in mapa_cores.items():
        plt.scatter([], [], c=cor, label=f'Frequência {freq}')
    
    plt.legend(loc='lower right', scatterpoints=1, frameon=True, title="Legenda")
    plt.show()


"""Tentativa de randomizar a topologia das torres GSM"""
def gerar_topologia_aleatoria(min_torres=3, max_torres=15, probabilidade_conexao=0.15):
    n = random.randint(min_torres, max_torres)
    V = []

    for i in range(1, n):
        V.append((i, i + 1))

    for i in range(1, n + 1):
        for j in range(i + 2, n + 1): 
            if random.random() < probabilidade_conexao:
                V.append((i, j))
                
    return n, V


"""PASSO INICIAL: Gerando a topologia de torres GSM"""
def resolver_com_z3(n, V):
#n, V = gerar_topologia_aleatoria(min_torres=3, max_torres=15, probabilidade_conexao=0.15)
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

        modelo = solver.model()
        print(f"Com {n} torres, o modelo é satisfatível\n")
        #print(f"Quantidade de Conexões: {len(V)}")
        #print(f"Conexões geradas: {V}\n")


        freqs = {i: f for i in range(1, n + 1) 
                 for f in range(1, 4) 
                 if is_true(modelo[x[(i, f)]])}

        plotar_grafo_gsm(n, V, freqs)
        return True, freqs

    else:
        print(f"Com {n} torres, o modelo é insatisfatível")
        return False, {}

"""PASSO FINAL: Plotar e exportar (json e csv, vou testar qual
desses é melhor para a llm) a topologia das torres 
"""

nome_arquivo = "cenarios_gsm.csv"
print(f"Gerando dados e exportando para '{nome_arquivo}'...\n")

total_experimentos = 20
acertos_z3 = 0

with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
    escritor = csv.writer(arquivo_csv)
    escritor.writerow(["rodada", "qtd_torres", "qtd_conexoes", "conexoes", "resultado_z3"])

    for rodada in range(1, total_experimentos + 1):
        print(f"--- Rodada {rodada:02d} ---")
        n, V = gerar_topologia_aleatoria(min_torres=3, max_torres=15, probabilidade_conexao=0.1)
        
        z3_sat, _ = resolver_com_z3(n, V)
        resultado_texto = "SAT" if z3_sat else "UNSAT"
    
        conexoes_json = json.dumps(V)

        escritor.writerow([rodada, n, len(V), conexoes_json, resultado_texto])

print(f"'{nome_arquivo}' gerado com sucesso.")
    