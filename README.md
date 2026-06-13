# **Alocação Frequências em Torres GSM com Z3 Solver** 

Este projeto aplica conceitos de **Satisfatibilidade Proposicional (SAT)** para resolver o problema real de alocação de frequências em redes de telefonia celular (GSM). Utilizando o provador de teoremas **Z3 Solver**, o sistema distribui frequências de forma randomizada e otimizada a fim de mitigar interferências entre torres vizinhas.

Ainda, o projeto conta com um módulo de **LLM**, comparando a precisão matemática do algoritmo tradicional (Z3) contra a capacidade de aproximação semântica e probabilística de uma LLM de Grande Porte (**Ollama Phi-3**, executado localmente e via Google Colab, devido às restrições de GPU da minha máquina pessoal).

**Documentação Adicional:** Conteúdos utilizados para a resolução desse trabalho podem ser visualizados na nossa página no [Notion](https://www.notion.so/LogiComp-28a52f2869068093abcffeffbed3a2b3)  

**Memorial Descritivo:** [Overleaf](https://www.overleaf.com/read/krnpmcbgbjvj#c1e12f)

---

## **Sobre o problema e a Modelagem**

O desafio consiste em atribuir frequências a $n$ torres, isto é, colorir um grafo dinâmico e aleatório contendo entre $3$ e $15$ torres utilizando um espectro limitado de apenas **3 frequências possíveis**. Essa limitação entre $3 \leq n \leq 15$ foi estabelecida arbitrariamente, de modo a evitar poluição visual ao plotar o grafo. Para que o sistema funcione sem erros, adicionamos as seguintes restrições (Cláusulas) para garantir a satisfatibilidade:

> **Restrição 1 (R1)**: Cobertura Total  

Toda torre $i$ deve, obrigatoriamente, operar em pelo menos uma das frequências disponíveis dentro do conjunto $F = \{1, 2, 3\}$.
$$x_{i,1} \lor x_{i,2} \lor x_{i,3}$$

  
> **Restrição 2 (R2)**: Exclusividade (uma torre só pode operar em uma ÚNICA frequência)

Uma torre $i$ opera em uma única frequência por vez. Se ela estiver alocada em um canal, não pode operar nos demais simultaneamente.
$$(\neg x_{i,1} \lor \neg x_{i,2}) \land (\neg x_{i,1} \lor \neg x_{i,3}) \land (\neg x_{i,2} \lor \neg x_{i,3})$$

  
> **Restrição 3 (R3)**: Validação da Vizinhança

Torres vizinhas geograficamente (representadas pelo par $(i, j)$ pertencente ao conjunto de adjacências $V$) não podem compartilhar o mesmo canal de frequência.  
$$\forall(i,j) \in V, \ \forall f \in F: \neg(x_{i,f} \land x_{j,f}) \equiv (\neg x_{i,f} \lor \neg x_{j,f})$$

---

## **Solução Geral**
Todas as restrições devem ser atendidas ao mesmo tempo para verificar a satisfatibilidade do sistema, conforme descrito abaixo:

$$\text{Solução} = R_1 \land R_2 \land R_3$$

---

## **Metodologia de Validação e Benchmark (Z3 vs. LLM)**

Para avaliar as soluções do Z3 x IA, o projeto adota uma arquitetura de testes em lotes.

1. **Geração e Gabarito (Z3):** O script `gsm.py` gera topologias aleatórias e utiliza o Z3 Solver para determinar se a malha é `SAT` ou `UNSAT`. Esses cenários são exportados para arquivos estruturados na pasta `cenariosZ3`.
2. **Análise de Restrições por LLM (Phi-3):** O script `phi3.py` consome os cenários gerados e, por meio de engenharia de prompt estruturada sob temperatura zero ($0.0$), submete as tuplas de coordenadas às restrições do problema para que o modelo deduza a satisfatibilidade. Os resultados encontrados são salvos na pasta `cenariosphi3`.
3. **Taxa de acerto da LLM:** O sistema confronta as respostas em tempo real, calculando a taxa de acerto do modelo estatístico.
4. **Fusão dos Modelos (Performance):** O script de análise consolida os CSVs históricos, exportando as métricas e gerando curvas de degradação. Assim, é possível comparar como os modelos performam lado a lado de acordo com a abordagem utilizada.

---

### **Tecnologias utilizadas:**   
O ecossistema do projeto foi construído utilizando as seguintes ferramentas e bibliotecas:

* **Python 3.14.2** - Linguagem base do projeto.
* **Z3-Solver** - Mecanismo de inferência para checagem de problemas do tipo SAT.
* **Ollama (Phi-3)** - Ambiente de execução local.
* **NetworkX** - Criação, manipulação e cálculo de posições estruturais dos grafos.
* **Pandas e Matplotlib** - Renderização e estilização da malha de torres.

---

## **Como Executar o Projeto**

### **Pré-requisitos**
Certifique-se de ter o [Ollama](https://ollama.com/) instalado e o modelo Phi-3 baixado localmente em sua máquina:
```bash
ollama run phi3

# Clonar o Repositório
git clone [https://github.com/hosanafg/LogiComp.git](https://github.com/hosanafg/LogiComp.git)
cd LogiComp  

# Criar o ambiente virtual
python -m venv venv

# Ativar no Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Ativar no Linux/macOS
source venv/bin/activate

# Instalar as bibliotecas necessárias
pip install -r requirements.txt

# ETAPA 1: Gerar os lotes de testes via Z3 Solver
python gsm.py

# ETAPA 2: Rodar a avaliação combinatória com a LLM local
python phi3.py

# ETAPA 3: Consolidar resultados, exportar métricas e plotar gráficos comparativos
python analisar_resultados.py
AnaliseComparativaFinal.ipynb 
```

## **Avaliando os resultados**
### **Z3 Solver: gsm.py**

[SAT] Solução encontrada!  
   ↳ Quantidade de Torres: 8  
   ↳ Quantidade de Conexões: 9

### **LLM: phi3.py**
O script processa as linhas sequencialmente, validando em comparação com a resposta do Z3
```bash
  ↳ Linha 01 | Torres: 05 | Conexões: 06 | ✅ CORRETO (Z3=SAT | Phi3=SAT)
  ↳ Linha 02 | Torres: 14 | Conexões: 19 | ❌ ERRADO [Z3=UNSAT | Phi3=SAT]
  ```
---
## **Parâmetros de Customização e Testes**
Você pode modificar a complexidade combinatória dos problemas alterando as seguintes variáveis em gsm.py e phi3.py, respectivamente:

**Densidade e Escala:**  
- Altere o valor de probabilidade_conexao. Valores elevados (ex: 0.35) geram grafos densos e altamente propensos a estrangulamento de canais (UNSAT), ideais para avaliar a capacidade da LLM.
- Ajuste min_torres e max_torres. Redes que excedem 10 vértices evidenciam o limite do raciocínio puramente linguístico do Phi-3 quando comparado à exatidão do Z3.
---
  
  
### **Resultados**  
Para não sobrecarregar o processamento local, a análise comparativa entre as três abordagens na LLM foi realizada no Google Colab e pode ser vista no arquivo ```AnaliseComparativaFinal.ipynb```. Em suma, quando forçamos o Phi-3 a agir como o Solver (Linguagem Natural), ele performa muito abaixo do esperado(27.90%). Ao alterarmos o papel da LLM para agir estritamente como um Tradutor de Especificações (gerando tuplas ou cláusulas para o Z3), a performance dispara. 

**Gráfico de Barras** 
- **LLM (Linguagem Natural) | 27.90%:** Pior desempenho. Demonstra a incapacidade do modelo de processar e solucionar restrições lógicas complexas puramente através de inferência autorregressiva textual.  
  
- **LLM (Tuplas) | 62.68% e Abordagem LLM p/ Z3 (Atual/Tradução) | 63.41%:** Ambas utilizam o Z3 Solver como motor de execução simbólica, praticamente "empatando". Ao delegar o cálculo lógico para o solver, a taxa de sucesso mais que dobra, saltando de 27.90% para a faixa de ~63%.

**Gráfico de Linhas**
Este, por sua vez, mapeia o comportamento dos modelos à medida que o problema ganha escala (de 2.5 a 20 torres):  

**- Abordagem com LN:** o modelo degrada quase que instantaneamente. A partir de 10 torres, sua acurácia zera completamente em vários pontos, mostrando que o modelo alucina as conexões lógicas quando o número de variáveis cresce de forma linear ou exponencial.

**- Pontos críticos:** A linha verde (Abordagem LLM p/ Z3 Atual) sofre uma queda abrupta logo nas 4 torres (caindo para ~57%). A partir daí, o comportamento de ambos os modelos baseados em código/Z3 assume um padrão "dente de serra" (alta volatilidade). Eles conseguem resolver problemas complexos de 12 ou 13 torres, mas falham erraticamente em cenários intermediários. Isso pode estar relacionado à baixa quantidade de parâmetros do Phi3, que não é bom em processar contextos.

---
## **Estrutura de arquivos do projeto**  
```bash
├── cenariosZ3/              # Datasets originais com os gabaritos do Z3 (.csv)
├── cenariosphi3/            # Resultados das inferências da LLM a partir das tuplas de coord. do Z3 (.csv)
├── cenarioLN/               # Resultados das inferências da LLM com Linguagem Natural (.csv)
├── cenarios_z3_phi3/        # Resultados das inferências da LLM traduzindo de Linguagem Natural para código estruturado Z3(.csv)
├── gsm.py                   # Módulo de execução do Z3
├── phi3.py                  # Pipeline de inferência estruturada (Tuplas) com a LLM local
├── analisar_resultados.py   # Script de fusão de dados, auditoria e plotagem de gráficos
├── AnaliseComparativaFinal  # Resultados de todas as inferências da LLM (.ipynb)
├── requirements.txt         # Dependências de bibliotecas Python
└── README.md                # Documentaçãos
```
---
<div style="background-color: #dfdac0; padding:25px; border-radius: 25px; color: #380450; font-family: 'Courier New', Courier, monospace;">
    <strong style="display: block; margin-bottom: 5px;">Lógica para Computação 2026.1</strong>
    <span style="display: block; margin-bottom: 5px;"> Hosana F. Gomes (representante) <a href ="https://github.com/hosanafg" style="color: #eb1d8e; font-weight: bold; text-decoration: none;">[Github]</a></span>
    Milo Cavalcante <a href="https://github.com/MiloOliveira" style="color: #eb1d8e; font-weight: bold; text-decoration: none;">[Github]</a></span>
    <span style="display: block; margin: 0;">IFCE Maracanaú</span>
</div>
<hr style="border: 0; border-top: 1px solid #cccccc00; margin-bottom: 20px;">