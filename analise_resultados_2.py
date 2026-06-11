import os
import glob
import sys
import pandas as pd
import matplotlib.pyplot as plt

def carregar_dados(pasta: str) -> pd.DataFrame:
    """Busca e unifica os arquivos CSV de resultados do Phi-3."""
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
    #               MÉTRICAS GERAIS (SOMA TOTAL)
    # =======================================================
    total_testes = len(df_total)
    
    acertos_est = len(df_total[df_total['status_estruturado'] == 'CORRETO'])
    acertos_nat = len(df_total[df_total['status_natural'] == 'CORRETO'])
    
    taxa_est_geral = (acertos_est / total_testes) * 100
    taxa_nat_geral = (acertos_nat / total_testes) * 100

    print("=" * 60)
    print("📊 MATRIZ CONSOLIDADA: CLÁUSULAS VS. LINGUAGEM NATURAL")
    print("=" * 60)
    print(f"Total de cenários avaliados: {total_testes}")
    print(f"Abordagem Estruturada (Cláusulas) | Acertos: {acertos_est} | Taxa: {taxa_est_geral:.2f}%")
    print(f"Abordagem Linguagem Natural       | Acertos: {acertos_nat} | Taxa: {taxa_nat_geral:.2f}%")
    print("=" * 60)

    # =======================================================
    #          PROCESSAMENTO DOS DADOS POR QUANTIDADE DE TORRES
    # =======================================================
    # Agrupamos e calculamos a média de acertos (True = 1, False = 0) multiplicada por 100
    df_est = df_total.groupby('qtd_torres')['status_estruturado'].apply(lambda x: (x == 'CORRETO').mean() * 100)
    df_nat = df_total.groupby('qtd_torres')['status_natural'].apply(lambda x: (x == 'CORRETO').mean() * 100)
    
    # Criamos o DataFrame unificado de taxas
    df_agrupado = pd.DataFrame({
        'Taxa_Estruturado_%': df_est,
        'Taxa_Natural_%': df_nat
    }).fillna(0.0).round(2)

    # Exportação do novo DataFrame comparativo para CSV
    df_agrupado.to_csv('acerto-llm-tuplascoord.csv', sep=';', encoding='utf-8')
    print("\nDEBUG: Dados comparativos exportados para 'acerto-llm-tuplascoord.csv'")

    # Extração de Pontos Críticos e Menores Acurácias
    min_est = df_agrupado['Taxa_Estruturado_%'].min()
    min_nat = df_agrupado['Taxa_Natural_%'].min()
    
    ponto_queda_est = None
    ponto_queda_nat = None
    
    for torres in df_agrupado.index:
        if ponto_queda_est is None and df_agrupado.loc[torres, 'Taxa_Estruturado_%'] < 100.0:
            ponto_queda_est = torres
        if ponto_queda_nat is None and df_agrupado.loc[torres, 'Taxa_Natural_%'] < 100.0:
            ponto_queda_nat = torres

    # =======================================================
    #          PLOTAGEM DOS GRÁFICOS (MATPLOTLIB)
    # =======================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle("Análise Comparativa de Paradigmas: Estruturado vs. Linguagem Natural (Phi-3)", fontsize=14, fontweight='semibold')

    # --- Gráfico 1: Barras Comparativas de Acurácia Geral ---
    categorias = ['Estruturado\n(Cláusulas)', 'Linguagem\nNatural']
    valores = [taxa_est_geral, taxa_nat_geral]
    cores_barras = ["#089db1", "#eb991d"]
    
    barras = ax1.bar(categorias, valores, color=cores_barras, width=0.5, edgecolor='black', alpha=0.8)
    ax1.set_title("Acurácia Global Absoluta", fontsize=11, fontweight='bold', pad=15)
    ax1.set_ylabel("Taxa de Acerto Geral (%)", fontsize=10)
    ax1.set_ylim(0, 105)
    ax1.grid(axis='y', linestyle=':', alpha=0.5)
    
    # Adiciona os rótulos de texto no topo de cada barra
    for barra in barras:
        height = barra.get_height()
        ax1.annotate(f'{height:.2f}%',
                     xy=(barra.get_x() + barra.get_width() / 2, height),
                     xytext=(0, 3),  # 3 pontos de offset vertical
                     textcoords="offset points",
                     ha='center', va='bottom', fontweight='bold')

    # --- Gráfico 2: Curvas de Degradação Combinadas ---
    # Linha do Modelo Estruturado
    ax2.plot(df_agrupado.index, df_agrupado['Taxa_Estruturado_%'], marker='o', 
             linewidth=2.0, color="#089db1", label='Phi-3 (Estruturado)')
    
    # Linha do Modelo em Linguagem Natural
    ax2.plot(df_agrupado.index, df_agrupado['Taxa_Natural_%'], marker='s', 
             linewidth=2.0, color="#eb991d", label='Phi-3 (Linguagem Natural)')
    
    # Linha de Base do Gabarito (Z3 Solver)
    ax2.axhline(y=100, color="#135861", linestyle='--', linewidth=1.5, label='Z3 Solver (Gabarito)')

    # Linha pontilhada vertical para início da queda do estruturado
    if ponto_queda_est is not None:
        ax2.axvline(x=ponto_queda_est, color='#056b79', linestyle=':', 
                    linewidth=1.2, label=f'Queda Estruturado ({ponto_queda_est} torres)')
                    
    # Linha pontilhada vertical para início da queda da linguagem natural
    if ponto_queda_nat is not None:
        ax2.axvline(x=ponto_queda_nat, color='#b36b00', linestyle=':', 
                    linewidth=1.2, label=f'Queda Lng. Natural ({ponto_queda_nat} torres)')

    ax2.set_title("Taxa de Acerto vs. Complexidade (Qtd. de Torres)", fontsize=11, fontweight='bold', pad=15)
    ax2.set_xlabel("Quantidade de Torres no Grafo", fontsize=10)
    ax2.set_ylabel("Acurácia por Agrupamento (%)", fontsize=10)
    ax2.set_ylim(-5, 105)
    ax2.grid(True, linestyle=':', alpha=0.3)

    # Inserção das legendas pequenas com a menor acurácia registrada de cada um
    ax2.plot([], [], ' ', label=f'Menor Acurácia Est.: {min_est:.1f}%')
    ax2.plot([], [], ' ', label=f'Menor Acurácia Nat.: {min_nat:.1f}%')
    ax2.legend(loc='lower left', fontsize='small')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()