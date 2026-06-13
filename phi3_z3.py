import csv
import json
import os
import sys
import ollama


def extrair_e_executar_z3(codigo_cru: str) -> str:
    linhas = codigo_cru.strip().split("\n")
    codigo_limpo = []
    for linha in linhas:
        if not linha.strip().startswith("```"):
            codigo_limpo.append(linha)
    
    codigo_final = "\n".join(codigo_limpo)
    escopo_local = {}
    
    try:
        exec(codigo_final, {}, escopo_local)
        resultado = escopo_local.get("RESULTADO_PROVER", "ERRO")
        return str(resultado).strip().upper()
    except Exception as e:
        # DEBUG:
        print("\n--- [DEBUG] CÓDIGO GERADO PELA LLM ---")
        print(codigo_final)
        print(f"--- [DEBUG] ERRO DE EXECUÇÃO: {e} ---\n")
        return "ERRO"


def analisar_lotes_neuro_simbolicos():
    pasta_origem = "cenariosZ3"
    pasta_destino = "cenarios_z3_phi3"  # Nova pasta exclusiva para não misturar os dados
    modelo_llm = "phi3"

    os.makedirs(pasta_destino, exist_ok=True)

    total_arquivos = 10 

    for i_arquivo in range(1, total_arquivos + 1):
        arq_entrada = f"cenarios_gsm_{i_arquivo:02d}.csv"
        arq_saida = f"phi3-code-{i_arquivo:02d}.csv"
        
        caminho_entrada = os.path.join(pasta_origem, arq_entrada)
        caminho_saida = os.path.join(pasta_destino, arq_saida)
        
        if not os.path.exists(caminho_entrada):
            print(f"ERRO: Arquivo {arq_entrada} não encontrado. Pulando...")
            continue
            
        print(f"\n" + "=" * 60)
        print(f"LENDO: {arq_entrada}")
        print(f"=" * 60)
        
        resumos_rodadas = []
        acertos_cod_z3 = 0
        total_lote = 0
        
        with open(caminho_entrada, mode='r', encoding='utf-8') as f_in:
            leitor = csv.DictReader(f_in)
            
            for table_row in leitor:
                total_lote += 1
                rodada = int(table_row["rodada"])
                n = int(table_row["qtd_torres"])
                qtd_conexoes = int(table_row["qtd_conexoes"])
                gabarito_z3 = table_row["resultado_z3"]
                V = [tuple(par) for par in json.loads(table_row["conexoes"])]
                
                # Prompt focado estritamente na geração do script do Solver
                prompt_gerar_z3 = f"""
                Você é um compilador determinístico de código. Seu único trabalho é preencher o template abaixo gerando restrições de desigualdade simples para um grafo.

                DADOS DO GRAFO:
                - Quantidade de Torres: {n}
                - Lista de Arestas: {V}

                REGRAS CRÍTICAS DE COMPILAÇÃO:
                1. Para cada par (A, B) presente na lista de arestas {V}, você DEVE escrever exatamente uma linha com a seguinte sintaxe: s.add(torres[A] != torres[B])
                2. NÃO use nenhuma outra função do Z3 como 'Distinct', 'DistinctQ', 'Implies' ou loops.
                3. Escreva apenas restrições usando o operador '!=' (diferente).
                4. Escreva todas as arestas. Não use reticências (...) nem pule nenhuma conexão.

                TEMPLATE OBRIGATÓRIO:
                ```python
                import z3

                s = z3.Solver()

                # Criação das variáveis
                torres = {{i: z3.Int(f'T{{i}}') for i in range(1, {n} + 1)}}

                # Restrição de domínio (Cores 1, 2 ou 3)
                for t in torres.values():
                    s.add(t >= 1, t <= 3)

                # Restrições de arestas geradas:
                # [INSIRA AS LINHAS 's.add(torres[A] != torres[B])' AQUI]

                # Verificação do resultado
                if s.check() == z3.sat:
                    RESULTADO_PROVER = "SAT"
                else:
                    RESULTADO_PROVER = "UNSAT"
                
                Responda EXCLUSIVAMENTE com o código preenchido. Não adicione nenhuma explicação textualmente fora do bloco de código.
                """
                try:
                    # Execução da Tradução de Código Z3 no Phi-3
                    resp_cod = ollama.chat(
                        model=modelo_llm,
                        messages=[{'role': 'user', 'content': prompt_gerar_z3}],
                        options={'temperature': 0.0}
                    )
                    codigo_gerado = resp_cod['message']['content']
                    
                    # Executa o código gerado pela IA no Z3 
                    pred_cod_z3 = extrair_e_executar_z3(codigo_gerado)
                    status_cod = "CORRETO" if pred_cod_z3 == gabarito_z3 else "ERRADO"

                    if status_cod == "CORRETO": 
                        acertos_cod_z3 += 1

                    print(f"--> Linha {rodada:02d} | Torres:{n:02d} | Conexões:{qtd_conexoes:02d} | Gabarito Z3={gabarito_z3} | Resposta IA Código={pred_cod_z3} ({status_cod})")
                    
                    resumos_rodadas.append([
                        rodada, n, qtd_conexoes, gabarito_z3, pred_cod_z3, status_cod
                    ])
                    
                except Exception as e:
                    print(f"Erro crítico na linha {rodada}: {e}")
                    resumos_rodadas.append([rodada, n, qtd_conexoes, gabarito_z3, "ERRO", "ERRADO"])

        # Gravando os resultados na nova pasta
        with open(caminho_saida, mode='w', newline='', encoding='utf-8') as f_out:
            escritor = csv.writer(f_out)
            escritor.writerow(["rodada", "qtd_torres", "qtd_conexoes", "resultado_z3", "phi3_cod_z3", "status_cod_z3"])
            escritor.writerows(resumos_rodadas)
            
        taxa_cod = (acertos_cod_z3 * 100.0) / total_lote
        print(f"\n[LIDO] {i_arquivo:02d} | % Acerto LLM-Z3: {taxa_cod:.2f}%")

    print("\nDEBUG: Processamento isolado concluído com sucesso!")


if __name__ == "__main__":
    analisar_lotes_neuro_simbolicos()