import csv
import json
import ollama

# Configurações do arquivo e modelo
arquivo_csv = "cenarios_gsm.csv"
modelo_llm = "phi3"

print(f"Iniciando testes com o modelo '{modelo_llm}' usando o arquivo '{arquivo_csv}'...\n")

total_testes = 0
acertos_phi3 = 0

# 1. Abre e lê o arquivo CSV gerado pelo Z3
with open(arquivo_csv, mode='r', encoding='utf-8') as f:
    leitor = csv.DictReader(f)
    
    for linha in leitor:
        total_testes += 1
        rodada = linha["rodada"]
        n = int(linha["qtd_torres"])
        gabarito_z3 = linha["resultado_z3"]
        
        # Converte a string JSON de volta para uma lista de tuplas do Python
        V = [tuple(par) for par in json.loads(linha["conexoes"])]
        
        # 2. Constrói o Prompt explicativo com as condições de satisfatibilidade
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

        Analise cuidadosamente o nível de conectividade do grafo.
        Responda EXCLUSIVAMENTE com uma única palavra em maiúsculo: ou 'SAT' ou 'UNSAT'. Não adicione justificativas, nem introduções, nem pontuação.
        """

        try:
            # 3. Envia o cenário para o Phi-3 local via Ollama
            resposta = ollama.chat(
                model=modelo_llm,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.0} # Força o modelo a ser o mais determinístico possível
            )
            
            # Limpa o texto da resposta tirando espaços e quebras de linha indesejadas
            predicao_phi3 = resposta['message']['content'].strip().upper()
            
            # Caso o modelo dê uma resposta longa, extraímos apenas a palavra-chave
            if "UNSAT" in predicao_phi3:
                predicao_phi3 = "UNSAT"
            elif "SAT" in predicao_phi3:
                predicao_phi3 = "SAT"

            # 4. Verifica se o Phi-3 acertou comparando com o Z3
            acertou = (predicao_phi3 == gabarito_z3)
            if acertou:
                acertos_phi3 += 1
                status = "✅ ACERTOU"
            else:
                status = f"❌ ERROU (Phi3 disse {predicao_phi3} | Z3 disse {gabarito_z3})"

            print(f"Rodada {rodada}: Torres: {n:02d} | Conexões: {len(V):02d} | {status}")

        except Exception as e:
            print(f"Erro ao processar a rodada {rodada}: {e}")

# 5. Exibe os resultados do Benchmark Estatístico
taxa_acerto = (acertos_phi3 * 100.0) / total_testes

print("\n" + "="*45)
print(f"📊 BENCHMARK FINAL: PHI-3 EM PROLEMAS GSM")
print("="*45)
print(f"Total de Cenários Avaliados: {total_testes}")
print(f"Respostas Corretas do Phi-3: {acertos_phi3}")
print(f"🎯 Taxa de Acerto Final:       {taxa_acerto:.2f}%")
print("="*45)
