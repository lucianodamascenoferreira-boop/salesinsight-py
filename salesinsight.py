# %% [markdown]
# # SalesInsight PY - Analise e Visualizacao de Dados de Vendas
# 
# Execute as celulas em ordem. A ultima celula mostra os 4 graficos gerados.

# %%
# ============================================================
# SalesInsight PY - Analise e Visualizacao de Dados de Vendas
# Fluxo: carregar -> inspecionar -> limpar -> transformar
#        -> agregar -> visualizar -> exportar
# Execucao: python salesinsight.py
# ============================================================
import json
import os
import random
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

COLUNAS_TEXTO = ["data_venda", "cliente", "produto", "categoria", "regiao"]

# %%
# ============================================================
# RF01 - Criar ou carregar o dataset de vendas
# ============================================================
def gerar_dataset_vendas(n_registros=500, seed=42):
    """
    Gera um dataset sintetico de vendas com dados sujos (datas invalidas).
    Parametros: n_registros (int) e seed (int, para reproducao).
    Retorna: DataFrame com os dados brutos.
    Obs.: usamos 500 registros e 300 clientes (o exemplo do enunciado usa
    200 e 50) para que os clientes se distribuam entre Bronze, Prata e Ouro.
    """
    random.seed(seed)
    np.random.seed(seed)

    produtos = ["Notebook", "Smartphone", "Tablet", "Monitor",
                "Teclado", "Mouse", "Headset"]
    categorias = {"Notebook": "Computadores", "Smartphone": "Celulares",
                  "Tablet": "Celulares", "Monitor": "Computadores",
                  "Teclado": "Perifericos", "Mouse": "Perifericos",
                  "Headset": "Perifericos"}
    precos = {"Notebook": 3500, "Smartphone": 2200, "Tablet": 1800,
              "Monitor": 1200, "Teclado": 250, "Mouse": 120,
              "Headset": 350}
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]

    data_inicio = datetime(2025, 1, 1)
    dados = []

    for i in range(n_registros):
        produto = random.choice(produtos)
        categoria = categorias[produto]
        quantidade = random.randint(1, 10)
        preco = round(precos[produto] * random.uniform(0.85, 1.15), 2)
        data = data_inicio + timedelta(days=random.randint(0, 364))
        data_txt = data.strftime("%Y-%m-%d")
        cliente = f"Cliente_{random.randint(1, 300):03d}"

        # sujeira proposital para a etapa de limpeza
        if random.random() < 0.03:
            data_txt = "DATA INVALIDA"

        dados.append({
            "id_venda": i + 1,
            "data_venda": data_txt,
            "cliente": cliente,
            "produto": produto,
            "categoria": categoria,
            "regiao": random.choice(regioes),
            "quantidade": quantidade,
            "preco_unitario": preco,
        })

    return pd.DataFrame(dados)

# %%
# ============================================================
# RF02 - Inspecao inicial do dataset
# ============================================================
def inspecionar_dados(df):
    """Exibe as informacoes estruturais do DataFrame e o devolve."""
    print("\n=== INSPECAO INICIAL DO DATASET ===")
    print(f"Shape: {df.shape}")
    print(f"\nColunas: {list(df.columns)}")
    print(f"\nTipos de dados:\n{df.dtypes}")
    print(f"\nValores nulos por coluna:\n{df.isnull().sum()}")
    print(f"\nPrimeiros registros:\n{df.head()}")
    return df

# %%
# ============================================================
# RF03 - Tratamento dos dados (limpeza com datetime)
# ============================================================
def padronizar_texto(serie):
    """
    Padroniza uma coluna de texto: remove espacos nas pontas (.str.strip)
    e colapsa espacos repetidos no meio do texto (re.sub).
    """
    return serie.astype(str).str.strip().apply(lambda t: re.sub(r"\s+", " ", t))


def tratar_dados(df):
    """
    Trata o DataFrame de vendas: padroniza textos, converte tipos
    (data, quantidade e preco) e remove linhas que nao puderam ser convertidas.
    Nao ha imputacao de nulos nem tratamento de outliers.
    Retorna: (df_limpo, relatorio), onde relatorio e um dicionario
    com as contagens de registros iniciais, convertidos, removidos e finais.
    """
    df = df.copy()
    n_inicial = len(df)

    # 1. remover espacos extras nas colunas de texto
    antes = df[COLUNAS_TEXTO].astype(str)
    depois = antes.apply(padronizar_texto)
    texto_alterado = (antes != depois).any(axis=1)
    df[COLUNAS_TEXTO] = depois

    # 2. converter data_venda; datas invalidas viram NaT
    df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")

    # 3. converter quantidade e preco; valores invalidos viram NaN
    qtd_ja_int = pd.api.types.is_integer_dtype(df["quantidade"])
    preco_ja_float = pd.api.types.is_float_dtype(df["preco_unitario"])
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
    df["preco_unitario"] = pd.to_numeric(df["preco_unitario"], errors="coerce")

    invalida_data = df["data_venda"].isna()
    invalida_qtd = df["quantidade"].isna()
    invalida_preco = df["preco_unitario"].isna()
    invalidos = invalida_data | invalida_qtd | invalida_preco

    # 4. remover o que nao pode ser convertido e fixar os tipos finais
    df = df.loc[~invalidos].copy()
    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = df["preco_unitario"].astype(float)
    df = df.reset_index(drop=True)
    n_final = len(df)

    n_validos = int((~invalidos).sum())
    tipos_ajustados = (not qtd_ja_int) or (not preco_ja_float)
    n_sem_alteracao = 0 if tipos_ajustados else int(
        (~texto_alterado[~invalidos]).sum())

    relatorio = {
        "registros_iniciais": n_inicial,
        "datas_convertidas": int((~invalida_data).sum()),
        "datas_invalidas": int(invalida_data.sum()),
        "quantidade_convertida": 0 if qtd_ja_int else n_validos,
        "quantidade_invalida": int(invalida_qtd.sum()),
        "preco_convertido": 0 if preco_ja_float else n_validos,
        "preco_invalido": int(invalida_preco.sum()),
        "registros_com_texto_ajustado": int(texto_alterado.sum()),
        "registros_removidos_total": int(invalidos.sum()),
        "registros_sem_alteracao": n_sem_alteracao,
        "registros_finais": n_final,
    }

    print("\n=== RELATORIO DE LIMPEZA ===")
    print(f"Registros iniciais:                 {relatorio['registros_iniciais']}")
    print("Conversoes de tipo:")
    print(f"  data_venda (texto -> datetime):   "
          f"{relatorio['datas_convertidas']} convertidas, "
          f"{relatorio['datas_invalidas']} invalidas")
    print(f"  quantidade -> int:                "
          f"{relatorio['quantidade_convertida']} convertidas, "
          f"{relatorio['quantidade_invalida']} invalidas"
          f"{' (ja era int)' if qtd_ja_int else ''}")
    print(f"  preco_unitario -> float:          "
          f"{relatorio['preco_convertido']} convertidos, "
          f"{relatorio['preco_invalido']} invalidos"
          f"{' (ja era float)' if preco_ja_float else ''}")
    print(f"Registros com texto ajustado:       {relatorio['registros_com_texto_ajustado']}")
    print(f"Registros removidos (nao conv.):    {relatorio['registros_removidos_total']}")
    print(f"Registros sem alteracao*:           {relatorio['registros_sem_alteracao']}")
    print(f"Registros finais:                   {relatorio['registros_finais']}")
    print("* sem ajuste de texto nem conversao de quantidade/preco "
          "(a data e sempre convertida)")

    return df, relatorio

# %%
# ============================================================
# RF04 - Colunas derivadas com transformacoes condicionais
# ============================================================
def criar_colunas_derivadas(df):
    """
    Cria receita_total, mes, mes_nome, ano, trimestre e faixa_receita_item.
    Retorna: o DataFrame com as novas colunas.
    """
    # 1. receita por linha (operacao vetorizada)
    df["receita_total"] = df["quantidade"] * df["preco_unitario"]

    # 2. componentes da data
    df["mes"] = df["data_venda"].dt.month
    df["ano"] = df["data_venda"].dt.year
    df["trimestre"] = "Q" + df["data_venda"].dt.quarter.astype(str)

    # 3. nome do mes em portugues (dicionario, evita o locale em ingles)
    mapa_meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }
    df["mes_nome"] = df["mes"].map(mapa_meses)

    # 4. faixa de receita do item (condicional vetorizada com df.loc)
    condicoes = [
        df["receita_total"] < 500,
        (df["receita_total"] >= 500) & (df["receita_total"] < 5000),
        df["receita_total"] >= 5000,
    ]
    faixas = ["Baixo Valor", "Medio Valor", "Alto Valor"]
    df["faixa_receita_item"] = "Nao Classificado"
    for condicao, faixa in zip(condicoes, faixas):
        df.loc[condicao, "faixa_receita_item"] = faixa

    return df

# %%
# ============================================================
# RF08 - Funcao de ordem superior (recebe outra funcao)
# ============================================================
def processar_coluna(df, coluna, funcao_transformacao, nome_saida=None):
    """
    Aplica uma funcao de transformacao a uma coluna do DataFrame.
    Parametros: df, nome da coluna, funcao (ex.: lambda) e nome da coluna nova.
    Retorna: o DataFrame com a coluna de saida criada.
    Demonstra o conceito de funcao de ordem superior.
    """
    nome_saida = nome_saida or f"{coluna}_transformado"
    df[nome_saida] = df[coluna].apply(funcao_transformacao)
    return df

# %%
# ============================================================
# RF05 - Metricas agregadas com groupby
# ============================================================
def calcular_metricas(df):
    """
    Calcula as metricas agregadas do dataset.
    Retorna: dicionario {nome_da_metrica: DataFrame} com as chaves
    por_mes, top_produtos, por_categoria e por_regiao.
    """
    metricas = {}

    metricas["por_mes"] = (
        df.groupby("mes")
          .agg(receita_total=("receita_total", "sum"),
               quantidade=("quantidade", "sum"),
               n_vendas=("id_venda", "count"))
          .reset_index()
          .sort_values("mes")
    )

    metricas["top_produtos"] = (
        df.groupby("produto")
          .agg(receita_total=("receita_total", "sum"))
          .reset_index()
          .sort_values("receita_total", ascending=False)
          .head(5)
    )

    metricas["por_categoria"] = (
        df.groupby("categoria")
          .agg(receita_total=("receita_total", "sum"))
          .reset_index()
          .sort_values("receita_total", ascending=False)
    )

    metricas["por_regiao"] = (
        df.groupby("regiao")
          .agg(receita_total=("receita_total", "sum"),
               ticket_medio=("receita_total", "mean"))
          .reset_index()
          .sort_values("receita_total", ascending=False)
    )

    print("\n=== RECEITA POR MES ===")
    print(metricas["por_mes"].to_string(index=False))
    print("\n=== TOP 5 PRODUTOS ===")
    print(metricas["top_produtos"].to_string(index=False))
    print("\n=== RECEITA POR CATEGORIA ===")
    print(metricas["por_categoria"].to_string(index=False))
    print("\n=== RECEITA E TICKET MEDIO POR REGIAO ===")
    print(metricas["por_regiao"].to_string(index=False))

    return metricas

# %%
# ============================================================
# RF06 - Segmentacao de clientes por nivel de gasto
# ============================================================
def segmentar_clientes(df):
    """
    Agrupa por cliente, soma a receita e classifica em Bronze / Prata / Ouro
    (abaixo de 5.000 / de 5.000 a 15.000 / acima de 15.000).
    Retorna: DataFrame com cliente, total_gasto e segmento.
    """
    clientes = (
        df.groupby("cliente")
          .agg(total_gasto=("receita_total", "sum"))
          .reset_index()
    )

    # classificacao com funcao lambda aplicada via .apply()
    clientes["segmento"] = clientes["total_gasto"].apply(
        lambda gasto: (
            "Ouro" if gasto > 15000 else
            "Prata" if gasto >= 5000 else
            "Bronze"
        )
    )
    clientes = clientes.sort_values("total_gasto", ascending=False)

    print("\n=== TOP 10 CLIENTES ===")
    print(clientes.head(10).to_string(index=False))
    print("\n=== DISTRIBUICAO POR SEGMENTO ===")
    print(clientes["segmento"].value_counts())

    return clientes

# %%
# ============================================================
# RF07 - Visualizacoes com Matplotlib e Seaborn
# ============================================================
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 11

PALETA = "viridis"
CORES_CATEGORIA = {"Computadores": "#2E86AB",
                   "Celulares": "#F18F01",
                   "Perifericos": "#C73E1D"}


def salvar_figura(caminho, mostrar=False, rect=None):
    """Aplica tight_layout, salva a figura atual em PNG (dpi=150) e a fecha."""
    plt.tight_layout(rect=rect)
    plt.savefig(caminho, dpi=150)
    if mostrar:
        plt.show()
    plt.close()


def gerar_graficos(df, metricas, pasta="outputs/graficos", mostrar=False):
    """
    Gera e exporta as 4 figuras obrigatorias em PNG.
    Parametros: df limpo, dicionario de metricas, pasta de saida e
    mostrar (True exibe as figuras na tela; False apenas salva).
    """
    os.makedirs(pasta, exist_ok=True)

    # FIGURA 1 - Linha: receita por mes
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(metricas["por_mes"]["mes"],
            metricas["por_mes"]["receita_total"],
            marker="o", linewidth=2.5, color="#2E86AB")
    ax.set_title("Receita Total por Mes - SalesInsight PY")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Receita Total (R$)")
    ax.set_xticks(range(1, 13))
    ax.grid(True, alpha=0.3)
    salvar_figura(f"{pasta}/receita_por_mes.png", mostrar)

    # FIGURA 2 - Barra: top 5 produtos
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=metricas["top_produtos"],
                y="produto", x="receita_total",
                hue="produto", legend=False,
                palette=PALETA, ax=ax)
    ax.set_title("Top 5 Produtos por Receita")
    ax.set_xlabel("Receita Total (R$)")
    ax.set_ylabel("Produto")
    ax.ticklabel_format(style="plain", axis="x", useOffset=False)
    salvar_figura(f"{pasta}/top_produtos.png", mostrar)

    # FIGURA 3 - Dispersao: quantidade vs receita, colorido por categoria
    fig, ax = plt.subplots(figsize=(12, 7))
    for categoria, cor in CORES_CATEGORIA.items():
        sub = df[df["categoria"] == categoria]
        ax.scatter(sub["quantidade"], sub["receita_total"],
                   label=categoria, color=cor, alpha=0.6, s=60)
    ax.set_title("Quantidade vs Receita por Transacao (por Categoria)")
    ax.set_xlabel("Quantidade")
    ax.set_ylabel("Receita Total (R$)")
    ax.legend(title="Categoria")
    salvar_figura(f"{pasta}/quantidade_vs_receita.png", mostrar)

    # FIGURA 4 - Painel 2x2 com subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    # [0,0] linha - receita por mes
    axes[0, 0].plot(metricas["por_mes"]["mes"],
                    metricas["por_mes"]["receita_total"],
                    marker="o", color="#2E86AB", linewidth=2)
    axes[0, 0].set_title("Receita por Mes")
    axes[0, 0].set_xlabel("Mes")
    axes[0, 0].set_ylabel("Receita (R$)")

    # [0,1] barra horizontal - top produtos
    axes[0, 1].barh(metricas["top_produtos"]["produto"],
                    metricas["top_produtos"]["receita_total"],
                    color="#F18F01")
    axes[0, 1].invert_yaxis()  # maior receita no topo
    axes[0, 1].set_title("Top 5 Produtos")
    axes[0, 1].set_xlabel("Receita (R$)")
    axes[0, 1].set_ylabel("Produto")
    axes[0, 1].ticklabel_format(style="plain", axis="x", useOffset=False)

    # [1,0] dispersao - quantidade vs receita
    for categoria, cor in CORES_CATEGORIA.items():
        sub = df[df["categoria"] == categoria]
        axes[1, 0].scatter(sub["quantidade"], sub["receita_total"],
                           label=categoria, color=cor, alpha=0.6, s=40)
    axes[1, 0].set_title("Quantidade vs Receita")
    axes[1, 0].set_xlabel("Quantidade")
    axes[1, 0].set_ylabel("Receita (R$)")
    axes[1, 0].legend(title="Categoria", fontsize=8)

    # [1,1] barra - receita por regiao
    axes[1, 1].bar(metricas["por_regiao"]["regiao"],
                   metricas["por_regiao"]["receita_total"],
                   color="#C73E1D")
    axes[1, 1].set_title("Receita por Regiao")
    axes[1, 1].set_xlabel("Regiao")
    axes[1, 1].set_ylabel("Receita (R$)")
    axes[1, 1].tick_params(axis="x", rotation=30)

    fig.suptitle("SalesInsight PY - Painel Resumo", fontsize=16)
    salvar_figura(f"{pasta}/painel_resumo.png", mostrar,
                  rect=(0, 0, 1, 0.97))

    print(f"4 graficos exportados em {pasta}/")

# %%
# ============================================================
# RF09 - Exportacao de resultados em CSV e JSON
# ============================================================
def calcular_estatisticas(df):
    """Calcula as estatisticas gerais (dicionario simples) a serem exportadas."""
    return {
        "total_registros": len(df),
        "receita_total_geral": df["receita_total"].sum(),
        "receita_media_por_venda": df["receita_total"].mean(),
        "quantidade_total_vendida": df["quantidade"].sum(),
        "numero_clientes_unicos": df["cliente"].nunique(),
        "numero_produtos_unicos": df["produto"].nunique(),
    }


def exportar_resultados(metricas, clientes, estatisticas, pasta="outputs"):
    """
    Exporta metricas por mes e segmentacao em CSV e as estatisticas em JSON.
    Le o JSON de volta (json.load) para conferir a escrita.
    Retorna: caminho do arquivo JSON gravado.
    """
    os.makedirs(pasta, exist_ok=True)

    metricas["por_mes"].to_csv(
        f"{pasta}/metricas_por_mes.csv", index=False, encoding="utf-8-sig")
    clientes.to_csv(
        f"{pasta}/segmentacao_clientes.csv", index=False, encoding="utf-8-sig")

    serializavel = {k: round(float(v), 2) for k, v in estatisticas.items()}
    caminho = f"{pasta}/estatisticas_gerais.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(serializavel, f, indent=4, ensure_ascii=False)

    with open(caminho, "r", encoding="utf-8") as f:
        conferencia = json.load(f)
    print(f"\nJSON gravado e lido de volta: {conferencia}")

    return caminho

# %%
# ============================================================
# RF10 - Classe AnalisadorDeVendas + main()
# ============================================================
class AnalisadorDeVendas:
    """Organiza o fluxo completo do SalesInsight PY."""

    def __init__(self, caminho_csv="vendas.csv"):
        """Define o caminho do CSV e inicializa os resultados como vazios."""
        self.caminho_csv = caminho_csv
        self.df_bruto = None
        self.df_limpo = None
        self.relatorio_limpeza = None
        self.metricas = None
        self.clientes = None

    def carregar(self, regenerar=False):
        """Le o CSV de vendas; gera o dataset sintetico se ele nao existir ou se regenerar=True."""
        if regenerar or not os.path.exists(self.caminho_csv):
            gerar_dataset_vendas().to_csv(self.caminho_csv, index=False)
        self.df_bruto = pd.read_csv(self.caminho_csv)
    #def carregar(self):
     #   """Le o CSV de vendas; se ele nao existir, gera o dataset sintetico."""
      #  if not os.path.exists(self.caminho_csv):
       #     gerar_dataset_vendas().to_csv(self.caminho_csv, index=False)
        #self.df_bruto = pd.read_csv(self.caminho_csv)

    def transformar(self):
        """Limpa os dados (antes de tudo) e cria as colunas derivadas."""
        self.df_limpo, self.relatorio_limpeza = tratar_dados(self.df_bruto)
        self.df_limpo = criar_colunas_derivadas(self.df_limpo)
        # funcao de ordem superior com lambdas em contextos distintos
        self.df_limpo = processar_coluna(
            self.df_limpo, "receita_total",
            lambda x: round(x / 1000, 2), nome_saida="receita_em_milhares")
        self.df_limpo = processar_coluna(
            self.df_limpo, "quantidade",
            lambda q: "Alto Volume" if q > 5 else "Baixo Volume",
            nome_saida="perfil_volume")

    def analisar(self):
        """Calcula as metricas agregadas e segmenta os clientes."""
        self.metricas = calcular_metricas(self.df_limpo)
        self.clientes = segmentar_clientes(self.df_limpo)

    def visualizar(self, mostrar=False):
        """Gera e salva as 4 figuras em PNG (mostrar=True exibe na tela)."""
        gerar_graficos(self.df_limpo, self.metricas, mostrar=mostrar)

    def exportar(self):
        """Exporta as metricas e a segmentacao em CSV e as estatisticas em JSON."""
        estatisticas = calcular_estatisticas(self.df_limpo)
        exportar_resultados(self.metricas, self.clientes, estatisticas)

    def resumo(self):
        """Imprime o resumo final do projeto no console."""
        print("\n" + "=" * 60)
        print("   RESUMO FINAL")
        print("=" * 60)
        print(f"Registros analisados: {len(self.df_limpo)}")
        print(f"Receita total:        R$ {self.df_limpo['receita_total'].sum():,.2f}")
        print(f"Ticket medio:         R$ {self.df_limpo['receita_total'].mean():,.2f}")
        print(f"Clientes unicos:      {self.df_limpo['cliente'].nunique()}")


def main():
    """Executa o fluxo completo do SalesInsight PY, de ponta a ponta."""
    print("=" * 60)
    print("   SALESINSIGHT PY - Analise de Dados de Vendas")
    print("=" * 60)

    analisador = AnalisadorDeVendas()
    analisador.carregar(regenerar=True)
    inspecionar_dados(analisador.df_bruto)
    analisador.transformar()
    analisador.analisar()
    analisador.visualizar()
    analisador.exportar()
    analisador.resumo()

    print("\n[CONCLUIDO] Fluxo finalizado com sucesso.")


if __name__ == "__main__":
    main()

# %%
from IPython.display import Image, display

for nome in ["receita_por_mes", "top_produtos", "quantidade_vs_receita", "painel_resumo"]:
    display(Image(f"outputs/graficos/{nome}.png"))


