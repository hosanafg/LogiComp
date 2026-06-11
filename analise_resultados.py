import os
import glob
import sys 
import pandas as pd
import matplotlib.pyplot as plt

def carregar_dados(pasta: str) -> pd.DataFrame:
    """Busca e unifica os arquivos CSV de resultados."""
    arquivos_csv = glob.glob(os.path.join(pasta, "phi3-*.csv"))

    if not arquivos_csv:
        print(f"ERRO: Nenhum arquivo encontrado em '{pasta}'. Rode o teste do Phi-3 primeiro!")
        sys.exit(1)

    lista_dataframes = [pd.read_csv(arq) for arq in arquivos_csv]
    return pd.concat(lista_dataframes, ignore_index=True)


def main():
    pasta_phi3 = "cenariosphi3"
    df_total = carregar_dados(pasta_phi3)

    # =======================================================
    #               MÉTRICAS GERAIS
    # =======================================================

    total_testes = len(df_total)
    acertos = len(df_total[df_total['status'] == 'CORRETO'])
    erros = len(df_total[df_total['status'] == 'ERRADO'])
    taxa_acerto_geral = (acertos / total_testes) * 100

    print("=" * 50)
    print("📊 MATRIZ DE CONSOLIDAÇÃO DOS RESULTADOS")
    print("=" * 50)
    print(f"Total de cenários avaliados: {total_testes}")
    print(f"Acertos: {acertos} | Erros: {erros}")
    print(f"🎯 Taxa de Acerto Global: {taxa_acerto_geral:.2f}%")
    print("=" * 50)

    # =======================================================
    #          PROCESSAMENTO DOS DADOS
    # =======================================================

    df_agrupado = df_total.groupby('qtd_torres')['status'].value_counts(normalize=True).unstack().fillna(0)
    
    if 'CORRETO' in df_agrupado.columns:
        df_agrupado['Taxa_Acerto_%'] = (df_agrupado['CORRETO'] * 100).round(2)
        
        # Salvar resultados em .csv
        df_agrupado[['Taxa_Acerto_%']].to_csv('acerto-llm-tuplascoord.csv', sep=';', encoding='utf-8')
        print("\nDados exportados com sucesso")
    else:
        df_agrupado['Taxa_Acerto_%'] = 0.0
        print("\nAVISO: Nenhuma linha com status 'CORRETO' encontrada.")

    # Identificando pontos críticos
    menor_acuracia=df_agrupado['Taxa_Acerto_%'].min()
    ponto_queda=None
    
    for torres in df_agrupado.index:
        if df_agrupado.loc[torres, 'Taxa_Acerto_%'] < 100.0:
            ponto_queda = torres
            break

    # =======================================================
    #               PLOTAGEM DOS GRÁFICOS 
    # =======================================================

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Análise Comparativa (Acerto): Z3 Solver vs. LLM (Phi-3)", fontsize=14, fontweight='semibold')

    # --- Gráfico 1: Gráfico de Pizza ---
    cores_pizza = ["#3c8a65", "#eb991d"]
    ax1.pie(
        [acertos, erros], 
        labels=['Acertos LLM', 'Erros LLM'], 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=cores_pizza,
        textprops={'fontsize': 10, 'weight': 'bold'}
    )
    ax1.set_title("Taxa de Acerto LLM", fontsize=10, fontweight='bold', pad=15)

    # --- Gráfico 2: Gráfico de Linhas ---
    ax2.plot(
        df_agrupado.index, 
        df_agrupado['Taxa_Acerto_%'], 
        marker='o', 
        linewidth=2.5, 
        color="#089db1", 
        label='Phi-3'
    )
    ax2.axhline(y=100, color="#135861", linestyle='--', linewidth=1.5, label='Z3 Solver (Gabarito)')

    if ponto_queda is not None:
        ax2.axvline(
            x=ponto_queda, 
            color='red', 
            linestyle=':', 
            linewidth=1, 
            label=f'Início da Queda ({ponto_queda} torres)'
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

# ------------------------------------------
if __name__ == "__main__":
    main()