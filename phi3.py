import csv
import json
import ollama
import os

pasta_origem = "cenariosZ3"
pasta_destino = "cenariosphi3"
modelo_llm = "phi3"  # Ajuste para "phi3:latest" caso necessário

os.makedirs(pasta_destino, exist_ok=True) 

total_arquivos = 10

print(f"🤖 Iniciando a maratona do Phi-3 lendo '{pasta_origem}'...")
print("Monitorando erros linha por linha em tempo real...\n")

for i_arquivo in range(1, total_arquivos + 1):
    arq_entrada = f"cenarios_gsm_{i_arquivo:02d}.csv"
    arq_saida = f"phi3-{i_arquivo:02d}.csv"
    
    caminho_entrada = os.path.join(pasta_origem, arq_entrada)
    caminho_saida = os.path.join(pasta_destino, arq_saida)
    
    if not os.path.exists(caminho_entrada):
        print(f"⚠️ Arquivo {arq_entrada} não encontrado. Pulando...")
        continue
        
    print(f"\n=======================================================")
    print(f"📦 ABRINDO LOTE {i_arquivo:02d}: {arq_entrada}")
    print(f"=======================================================")
    
    resumos_rodadas = []
    acertos_lote = 0
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
            
            prompt = f"""
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
            
            try:
                resposta = ollama.chat(
                    model=modelo_llm,
                    messages=[{'role': 'user', 'content': prompt}],
                    options={'temperature': 0.0}
                )
                
                predicao_phi3 = resposta['message']['content'].strip().upper()
                
                if "UNSAT" in predicao_phi3:
                    predicao_phi3 = "UNSAT"
                elif "SAT" in predicao_phi3:
                    predicao_phi3 = "SAT"
                else:
                    predicao_phi3 = "ERRO_FORMATO"

                # Validação
                if predicao_phi3 == gabarito_z3:
                    acertos_lote += 1
                    status_print = f"✅ CORRETO (Z3={gabarito_z3} | Phi3={predicao_phi3})"
                    vencedor = "CORRETO"
                else:
                    # Destaca o erro no terminal para fácil visualização
                    status_print = f"❌ ERRADO ➜ [Z3={gabarito_z3} | Phi3={predicao_phi3}]"
                    vencedor = "ERRADO"
                
                # 🟢 NOVO: Print linha por linha detalhado no terminal
                print(f"  ↳ Linha {rodada:02d} | Torres: {n:02d} | Conexões: {qtd_conexoes:02d} | {status_print}")
                    
                resumos_rodadas.append([rodada, n, qtd_conexoes, gabarito_z3, predicao_phi3, vencedor])
                
            except Exception as e:
                print(f"  ❌ Erro crítico na linha {rodada}: {e}")
                resumos_rodadas.append([rodada, n, qtd_conexoes, gabarito_z3, "ERRO_API", "ERRADO"])

    # Grava os resultados consolidados
    with open(caminho_saida, mode='w', newline='', encoding='utf-8') as f_out:
        escritor = csv.writer(f_out)
        escritor.writerow(["rodada", "qtd_torres", "qtd_conexoes", "resultado_z3", "predicao_phi3", "status"])
        escritor.writerows(resumos_rodadas)
        
    taxa_lote = (acertos_lote * 100.0) / total_lote
    print(f"\n📈 FIM DO LOTE {i_arquivo:02d} ➜ Taxa de Acerto: {taxa_lote:.2f}%")

print("\n🎉 Todos os testes foram processados e armazenados na pasta 'cenariosphi3'!")