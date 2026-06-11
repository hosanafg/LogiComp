import csv
import json
import os
import sys
import ollama

def traduzir_para_linguagem_natural(n: int, V: list) -> str:
    texto = (
        f"Você é o engenheiro chefe responsável por configurar uma nova rede de distribuição de torres GSM "
        f"contendo {n} torres de transmissão, identificadas numericamente de 1 a {n}.\n"
    )
    if not V:
        texto += "Absolutamente nenhuma destas torres deve possuir proximidade geográfica para gerar interferência, isto é, não podem ser vizinhas."
    else:
        texto += "Devido ao posicionamento geográfico, o seu mapeamento de topologia aponta as seguintes fronteiras imediatas:\n"
        vizinhancas = [f"- A torre {i} faz fronteira com a torre {j}" for i, j in V]
        texto += "\n".join(vizinhancas) + "."
    return texto


def analisar_lotes():
    pasta_origem = "cenariosZ3"
    pasta_destino = "cenariosphi3"
    modelo_llm = "phi3"

    os.makedirs(pasta_destino, exist_ok=True)
    total_arquivos = 10 

    for i_arquivo in range(1, total_arquivos + 1):
        arq_entrada = f"cenarios_gsm_{i_arquivo:02d}.csv"
        arq_saida = f"phi3-{i_arquivo:02d}.csv"
        
        caminho_entrada = os.path.join(pasta_origem, arq_entrada)
        caminho_saida = os.path.join(pasta_destino, arq_saida)
        
        if not os.path.exists(caminho_entrada):
            print(f"ERRO: Arquivo {arq_entrada} não encontrado. Pulando...")
            continue
            
        print(f"\n" + "=" * 60)
        print(f"LENDO ARQUIVO: {i_arquivo:02d}: {arq_entrada}")
        print(f"=" * 60)
        
        resumos_rodadas = []
        acertos_estruturado = 0
        acertos_natural = 0
        total_lote = 0
        
        with open(caminho_entrada, mode='r', encoding='utf-8') as f_in:
            leitor = csv.DictReader(f_in)
            
            for linha in leitor:
                total_lote += 1
                rodada = int(linha["rodada"])
                n = int(linha["qtd_torres"])
                qtd_conexoes = int(linha["qtd_conexoes"])
                gabarito_z3 = linha["resultado_z3"]
                V = [tuple(par) for par in json.loads(linha["conexoes"])]
                
                # ---------------------------------------------------
                # PROMPT 1: Abordagem Estruturada (Original)
                # ---------------------------------------------------
                prompt_estruturado = f"""
                Você é um avaliador de lógica estrita e restrições matemáticas.
                Seu objetivo é determinar se um grafo de rede de torres GSM pode ser colorido usando no máximo 3 FREQUÊNCIAS (1, 2 ou 3) sem gerar interferências.

                CONDIÇÕES DE SATISFATIBILIDADE:
                1. Toda torre deve obrigatoriamente operar em uma frequência (1, 2 ou 3).
                2. Torres conectadas por uma aresta NÃO PODEM usar a mesma frequência (interferência).
                3. Se for matematicamente POSSÍVEL atribuir frequências válidas para todas as torres respeitando as regras, o modelo é SAT.
                4. Se houver um gargalo de conexões que torne a distribuição IMPOSSÍVEL com apenas 3 frequências, o modelo é UNSAT.

                DADOS DO PROBLEMA ATUAL:
                - Quantidade de Torres (Vértices): {n}
                - Conexões (Arestas): {V}

                Analise cuidadosamente o nível de conexão do grafo.
                Responda EXCLUSIVAMENTE com uma única palavra em maiúsculo: ou 'SAT' ou 'UNSAT'. Não adicione justificativas ou pontuação.
                """


                # ---------------------------------------------------
                # PROMPT 2: Abordagem em Linguagem Natural 
                # ---------------------------------------------------

                
                cenario_narrativo = traduzir_para_linguagem_natural(n, V)
                prompt_natural = f"""
                Você é um especialista em otimização de sistemas. Resolva o problema real de alocação abaixo baseado em regras de coloração de grafos.

                CENÁRIO CONCRETO:
                {cenario_narrativo}

                REGRAS DE OPERAÇÃO DA REDE:
                - Você dispõe de exatamente 3 canais de frequência de rádio (Canais 1, 2 e 3).
                - Toda e qualquer torre precisa receber exatamente um canal para funcionar.
                - Torres descritas como vizinhas geográficas ou de fronteira NÃO PODEM, sob hipótese alguma, operar no mesmo canal, ou a rede inteira sofrerá colapso por interferência.

                Considerando a quantidade de torres e todas as restrições de vizinhança explicitadas, determine: É matematicamente POSSÍVEL alocar frequências válidas para toda a infraestrutura sem gerar interferências?
                Responda EXCLUSIVAMENTE com a palavra 'SAT' se for possível, ou 'UNSAT' se for impossível. Não escreva nenhuma outra palavra ou pontuação além disso.
                """
                
                try:
                    resp_est = ollama.chat(
                        model=modelo_llm,
                        messages=[{'role': 'user', 'content': prompt_estruturado}],
                        options={'temperature': 0.0}
                    )
                    pred_estruturado = resp_est['message']['content'].strip().upper()
                    pred_estruturado = "UNSAT" if "UNSAT" in pred_estruturado else ("SAT" if "SAT" in pred_estruturado else "ERRO")

                    # Execução do teste em linguagem natural
                    resp_nat = ollama.chat(
                        model=modelo_llm,
                        messages=[{'role': 'user', 'content': prompt_natural}],
                        options={'temperature': 0.0}
                    )
                    pred_natural = resp_nat['message']['content'].strip().upper()
                    pred_natural = "UNSAT" if "UNSAT" in pred_natural else ("SAT" if "SAT" in pred_natural else "ERRO")

                    # Avaliação das métricas
                    status_est = "CORRETO" if pred_estruturado == gabarito_z3 else "ERRADO"
                    status_nat = "CORRETO" if pred_natural == gabarito_z3 else "ERRADO"

                    if status_est == "CORRETO": acertos_estruturado += 1
                    if status_nat == "CORRETO": acertos_natural += 1

                    print(f"--> Linha {rodada:02d} | T:{n:02d} | C:{qtd_conexoes:02d} | Z3={gabarito_z3} | Estruturado={pred_estruturado} ({status_est}) | Natural={pred_natural} ({status_nat})")
                    
                    resumos_rodadas.append([
                        rodada, n, qtd_conexoes, gabarito_z3, 
                        pred_estruturado, status_est, 
                        pred_natural, status_nat
                    ])
                    
                except Exception as e:
                    print(f"Erro crítico na linha {rodada}: {e}")
                    resumos_rodadas.append([rodada, n, qtd_conexoes, gabarito_z3, "ERRO", "ERRADO", "ERRO", "ERRADO"])

        with open(caminho_saida, mode='w', newline='', encoding='utf-8') as f_out:
            escritor = csv.writer(f_out)
            escritor.writerow([
                "rodada", "qtd_torres", "qtd_conexoes", "resultado_z3", 
                "phi3_estruturado", "status_estruturado", 
                "phi3_natural", "status_natural"
            ])
            escritor.writerows(resumos_rodadas)
            
        taxa_est = (acertos_estruturado * 100.0) / total_lote
        taxa_nat = (acertos_natural * 100.0) / total_lote
        print(f"\nFIM {i_arquivo:02d} | % Acerto Cláusulas: {taxa_est:.2f}% | % Acerto Linguagem Natural: {taxa_nat:.2f}%")

    print("\nDEBUG: Todos os testes foram realizados")


if __name__ == "__main__":
    analisar_lotes()