# **Alocação Frequências em Torres GSM com Z3 Solver**  
  
Este projeto aplica conceitos de **Lógica Computacional** e **Satisfatibilidade Proposicional (SAT)** para resolver o problema real de alocação de frequências em redes de telefonia celular (GSM). Utilizando o provador de teoremas **Z3 Solver**, o sistema distribui frequências de forma otimizada a fim de mitigar interferências entre torres vizinhas.

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

### **Tecnologias utilizadas:** 
O ecossistema do projeto foi construído utilizando as seguintes ferramentas e bibliotecas:

* **Python 3.14.2** - Linguagem base do projeto.
* **Z3-Solver** - Mecanismo de inferência lógica da Microsoft Research para checagem de matrizes SAT.
* **NetworkX** - Criação, manipulação e cálculo de posições estruturais dos grafos.
* **Matplotlib** - Renderização visual e estilização da malha de torres.

---

## **Como Executar o Projeto**


```bash
# Clonar o Repositório
git clone [https://github.com/hosanafg/LogiComp.git](https://github.com/hosanafg/LogiComp.git)
cd LogiComp  

# Criar o ambiente virtual
python -m venv venv

# Ativar no Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Ativar no Linux/macOS
source venv/bin/activate

#Instalar as bibliotecas necessárias
pip install -r requirements.txt

# Executar o código principal
python gsm.py
```
---

## **Avaliando os resultados**

Se a quantidade de torres for $satisfatível$, será aberta uma janela popup com a distribuição topológica das torres e as conexões (que representam vizinhanças), como mostra a figura abaixo:

<p align="center">
  <table>
    <tr>
      <td>
        <p align="center"><b>Exemplo 1 (SAT)</b></p>
        <img src="ex1.png" alt="Exemplo 1" width="200">
      </td>
      <td>
        <p align="center"><b>Exemplo 2 (SAT)</b></p>
        <img src="ex2.png" alt="Exemplo 2" width="200">
      </td>
    </tr>
    <tr>
      <td>
        <p align="center"><b>Exemplo 3 (SAT)</b></p>
        <img src="ex3.png" alt="Exemplo 3" width="200">
      </td>
      <td>
        <p align="center"><b>Exemplo 4 (SAT)</b></p>
        <img src="ex4.png" alt="Exemplo 4" width="200">
      </td>
    </tr>
  </table>
</p>

Caso a quantidade de torres $não$ $seja$ $satisfatível$, o programa retorna a seguinte mensagem, onde n é o número de torres aleatório escolhido a cada execução do programa:
```bash
Com n torres, o modelo não é satisfatível
```
---
## **Opcional:** Como Contribuir e Testar Novos Cenários

Se você quiser realizar novos cenários, pode modificar os seguintes parâmetros diretamente no arquivo gsm.py:
1. **Modificar a densidade da rede:** Altere o valor de $probabilidade_conexao$ na função $gerar_topologia_aleatoria$. Valores maiores (ex: 0.4) geram redes extremamente conectadas, ideais para testar os limites do Z3 e forçar cenários UNSAT (Insatisfatíveis).
2. Mudar o tamanho do problema: Altere os argumentos $min_torres$ e $max_torres$ para testar o tempo de processamento do solver com redes maiores.
---

## **Sobre o projeto**
A organização dos arquivos no projeto segue a estrutura abaixo:

```text
├── .gitignore          # Arquivos e pastas ignorados pelo Git (venv, ex*.png)
├── README.md           # Documentação principal do projeto
├── gsm.py              # Script principal com a lógica Z3 e plotagem
└── requirements.txt    # Biblioteca de dependências do projeto
```
<div style="background-color: #dfdac0; padding:25px; border-radius: 25px; color: #380450; font-family: 'Courier New', Courier, monospace;">
    <strong style="display: block; margin-bottom: 5px;">Lógica para Computação 2026.1</strong>
    <span style="display: block; margin-bottom: 5px;"> Hosana F. Gomes (representante) <a href ="https://github.com/hosanafg" style="color: #eb1d8e; font-weight: bold; text-decoration: none;">[Github]</a></span>
    Milo Cavalcante <a href="https://github.com/MiloOliveira" style="color: #eb1d8e; font-weight: bold; text-decoration: none;">[Github]</a></span>
    <span style="display: block; margin: 0;">IFCE Maracanaú</span>
</div>
<hr style="border: 0; border-top: 1px solid #cccccc00; margin-bottom: 20px;">