import os
import glob
import json
import pandas as pd
import matplotlib.pyplot as plt

# =======================================================
#                 LENDO OS ARQUIVOS
# =======================================================
pasta_phi3="cenariosphi3"
arquivos_csv=glob.glob(os.path.join(pasta_phi3, "phi3-*.csv"))

if not arquivos_csv:
    print(f"ERRO: Nenhum arquivo encontrado em '{pasta_phi3}'. Rode o teste do Phi-3 primeiro!")
    exit()

lista_dataframes=[pd.read_csv(arq) for arq in arquivos_csv]
df_total=pd.concat(lista_dataframes, ignore_index=True)

total_testes=len(df_total)
acertos=len(df_total[df_total['status']=='CORRETO'])
erros=len(df_total[df_total['status']=='ERRADO'])
taxa_acerto_geral=(acertos/total_testes)*100

df_agrupado=df_total.groupby('qtd_torres')['status'].value_counts(normalize=True).unstack().fillna(0)
if 'CORRETO' in df_agrupado.columns:
    df_agrupado['Taxa_Acerto_%']=df_agrupado['CORRETO'] * 100
else:
    df_agrupado['Taxa_Acerto_%']= 0.0


# =======================================================
#              LEITURA DOS DADOS CRÍTICOS
# =======================================================

# Identificando os pontos críticos (Menor Acurácia)
menor_acuracia=df_agrupado['Taxa_Acerto_%'].min()

# Encontra o primeiro ponto onde a acurácia cai abaixo de 100%
ponto_queda=None
for torres in df_agrupado.index:
    if df_agrupado.loc[torres, 'Taxa_Acerto_%'] < 100.0:
        ponto_queda=torres
        break

print("\nTaxa de Acerto:")
df_agrupado = df_total.groupby('qtd_torres')['status'].value_counts(normalize=True).unstack().fillna(0)
if 'CORRETO' in df_agrupado.columns:
    df_agrupado['Taxa_Acerto_%'] = (df_agrupado['CORRETO'] * 100).round(2)
    #print(df_agrupado[['Taxa_Acerto_%']]) ---print debug
    
    # Salvar resultados p/ .csv
    df_agrupado[['Taxa_Acerto_%']].to_csv('acerto-llm-tuplascoord.csv', sep=';', encoding='utf-8')
    print("\nDados exportados com sucesso para 'acerto-llm-tuplascoord.csv'")
else:
    print("ERRO: Nenhuma linha com status 'CORRETO' encontrada")

# =======================================================
#          PLOTAGEM DOS GRÁFICOS (MATPLOTLIB)
# =======================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Análise Comparativa (Acerto): Z3 Solver vs. LLM (Phi-3)", fontsize=14, fontweight='semibold')

# --- Gráfico 1: Gráfico de Pizza ---
cores_pizza = ["#3c8a65", "#eb991d"]
ax1.pie([acertos, erros], labels=['Acertos LLM', 'Erros LLM'], 
    autopct='%1.1f%%', startangle=90, colors=cores_pizza,
    textprops={'fontsize': 10, 'weight': 'bold'}
)
ax1.set_title("Taxa de Acerto LLM", fontsize=10, fontweight='bold', pad=15)

# --- Gráfico 2: Gráfico de Linhas ---
ax2.plot(df_agrupado.index, df_agrupado['Taxa_Acerto_%'], marker='o', 
    linewidth=2.5, color="#089db1", label='Phi-3'
)

ax2.axhline(y=100, color="#135861", linestyle='--', linewidth=1.5, label='Z3 Solver (Gabarito)')

if ponto_queda is not None:
    ax2.axvline(x=ponto_queda, color='red', linestyle=':', 
        linewidth=1, label=f'Início da Queda ({ponto_queda} torres)'
    )

ax2.set_title("Taxa de Acerto vs. Qtd. de Torres", fontsize=10, fontweight='bold', pad=15)
ax2.set_xlabel("Quantidade de Torres", fontsize=10)
ax2.set_ylabel("Acurácia do Modelo (%)", fontsize=10)
ax2.set_ylim(-5, 105)
ax2.grid(True, linestyle=':', alpha=0.2)

ax2.plot([], [], ' ', label=f'Menor Acurácia: {menor_acuracia:.1f}%')
ax2.legend(loc='lower left', fontsize='small')

plt.tight_layout()
plt.show()