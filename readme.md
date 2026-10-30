# SalesInsight PY

**Análise e visualização de dados de vendas com Python**

Mini-projeto avaliativo do Módulo 01 (Semana 07) do curso *Desenvolvedor(a) em IA para Análise Preditiva* (Turma T5).

**Autor(a):** LUCIANO VIDAL DAMASCENO FERREIRA

## Sobre o projeto

O SalesInsight PY simula o trabalho de um analista de dados júnior numa empresa de varejo: a diretoria tem um histórico de vendas e quer entender o desempenho do negócio para a reunião trimestral.

O programa **cria, carrega, limpa, transforma, agrega e visualiza** um dataset de vendas, gerando métricas por período, produto, categoria e região, além de uma segmentação simples de clientes por faixa de gasto. Os resultados são exportados em CSV, JSON e PNG.

Todo o fluxo está organizado em **funções reutilizáveis** e em uma classe (`AnalisadorDeVendas`), executados a partir de uma função `main()`.

## O que o projeto analisa

- Receita total, quantidade vendida e número de vendas **por mês**
- **Top 5 produtos** por receita e receita por **categoria**
- Receita e **ticket médio por região**
- Segmentação de clientes por nível de gasto: **Bronze** (abaixo de R$ 5.000), **Prata** (de R$ 5.000 a R$ 15.000) e **Ouro** (acima de R$ 15.000)
- Relação entre a **quantidade vendida** e a **receita** de cada transação

## Como o fluxo funciona

1. **Gerar ou carregar** o dataset (`vendas.csv`), com dados sujos de propósito
2. **Inspecionar** a estrutura (formato, colunas, tipos, nulos e primeiros registros)
3. **Limpar** os dados e exibir o relatório de limpeza (antes de qualquer transformação)
4. **Criar colunas derivadas** (receita, mês, ano, trimestre, nome do mês e faixa de receita)
5. **Agregar** com `groupby` e **segmentar** os clientes
6. **Gerar os gráficos** e salvar em PNG
7. **Exportar** os resultados em CSV e JSON, e ler o JSON de volta para conferir

## Principais resultados

Valores obtidos com o dataset sintético gerado pelo próprio código (semente fixa `42`, então qualquer pessoa obtém o mesmo resultado):

- Dos **500** registros gerados, **22** tinham data inválida e foram removidos, restando **478** vendas analisadas
- Receita total de **R$ 3.345.291,72** e ticket médio de **R$ 6.998,52**, com **238 clientes** distintos
- O **Notebook** é o produto que mais gera receita (R$ 1.303.162,88), e **Computadores** é a categoria líder
- A região **Sul** tem a maior receita (R$ 789.053,00) e o maior ticket médio, enquanto o **Sudeste** tem a menor receita
- **Agosto** é o mês de maior receita (R$ 441.416,99), seguido por março e dezembro
- Segmentação de clientes: **86 Ouro, 67 Prata e 85 Bronze**
- Quanto maior a quantidade vendida, maior tende a ser a receita da transação, e a inclinação depende do preço do produto: os Computadores sobem mais rápido que os Periféricos


## Conceitos de Python e análise de dados aplicados

- **Lógica de programação:** variáveis, tipos de dados, operadores aritméticos, lógicos e relacionais, `if`/`elif`/`else`, laços `for`
- **Estruturas de dados:** listas, dicionários e estruturas compostas (lista de dicionários, dicionário de DataFrames)
- **Funções:** parâmetros, valores padrão, retorno, docstring, **funções lambda** (em contextos distintos) e **função de ordem superior** (`processar_coluna`)
- **Módulos e importação:** `pandas`, `numpy`, `json`, `os`, `re`, `random`, `datetime`, `matplotlib` e `seaborn`
- **Orientação a objetos básica:** classe `AnalisadorDeVendas` com atributos e métodos
- **Leitura e escrita de arquivos:** CSV (`read_csv`, `to_csv`) e JSON (`json.dump`, `json.load`)
- **Datetime:** `pd.to_datetime(errors="coerce")` e extração de mês, ano e trimestre com `.dt`
- **Pandas:** DataFrames, filtros com máscaras booleanas, `.loc`, `groupby` com `agg`, `sort_values`, `reset_index`, `value_counts`, `map` e `apply`
- **Transformações condicionais vetorizadas** para a faixa de receita de cada venda
- **Visualização:** gráficos de linha, barras e dispersão, **subplots 2×2**, customização (título, rótulos, legenda, paleta e `figsize`) e exportação em PNG com `savefig`
- **Git e GitHub:** branches descritivas, commits no padrão *conventional commits* e repositório público

## Como executar

### Google Colab (recomendado)

1. Acesse o [Google Colab](https://colab.research.google.com/) e abra um novo notebook.
2. Faça upload do arquivo `salesinsight.py` (painel de arquivos à esquerda).
3. Em uma célula, execute:

   ```python
   !python salesinsight.py
   ```

4. Alternativa: abra o `salesinsight.ipynb` no Colab e use *Ambiente de execução > Executar tudo*.

O Colab já vem com pandas, numpy, matplotlib e seaborn instalados.

### Localmente com VS Code

1. Instale o **Python 3.10 ou superior** e o **VS Code** (com a extensão Python).
2. Clone o repositório e entre na pasta:

   ```bash
   git clone https://github.com/[seu-usuario]/salesinsight-py.git
   cd salesinsight-py
   ```

3. Instale as dependências:

   ```bash
   pip install pandas numpy matplotlib seaborn
   ```

4. Execute no terminal:

   ```bash
   python salesinsight.py
   ```

O `vendas.csv` é recriado a cada execução. Os resultados são gravados na pasta `outputs/`.

## Estrutura do projeto

```text
salesinsight-py/
|-- salesinsight.py              # fluxo principal (funções, classe e main)
|-- salesinsight.ipynb           # versão em notebook, com as mesmas células
|-- vendas.csv                   # dataset gerado pelo código
|-- README.md
|-- outputs/
    |-- metricas_por_mes.csv
    |-- segmentacao_clientes.csv
    |-- estatisticas_gerais.json
    |-- graficos/
        |-- receita_por_mes.png
        |-- top_produtos.png
        |-- quantidade_vs_receita.png
        |-- painel_resumo.png
```

## Decisões técnicas

- **Remover as datas inválidas em vez de mantê-las.** Uma data vazia quebraria a extração de mês, ano e trimestre e distorceria as agregações. Como o escopo do projeto não inclui imputação de valores, a decisão mais segura foi remover essas linhas e **registrar a quantidade removida** no relatório de limpeza.
- **Gerador com 500 registros e 300 clientes** (o exemplo do enunciado usa 200 e 50). Com poucos clientes e muitas compras, todos acumulavam mais de R$ 15.000 e viravam Ouro. Com mais clientes, cada um compra menos vezes, e os três segmentos passam a aparecer.
- **Conversão de tipos com `errors="coerce"`.** Datas, quantidades e preços inválidos viram valores vazios e são removidos antes de fixar os tipos finais (`int` e `float`), já que o tipo `int` não aceita valores vazios.
- **`carregar(regenerar=True)` no `main()`.** Garante que toda execução recria o `vendas.csv`, sem reaproveitar um arquivo antigo de outra configuração.
- **Gráficos salvos sem `plt.show()` por padrão.** Em um terminal, `show()` pausa o programa até a janela ser fechada. O parâmetro `mostrar=True` exibe as figuras quando desejado.

## Organização do trabalho

- **Kanban:** [inserir o link do quadro aqui] (colunas: Backlog, A Fazer, Em Andamento e Concluído)
- **Branches:** `main` (versão final estável), `develop` (integração), `feat/pipeline-dados` (limpeza, métricas, gráficos e exportação) e `docs/readme` (documentação)
- **Commits:** padrão *conventional commits*, por exemplo `feat: implementa metricas agregadas com groupby` e `docs: atualiza readme com instrucoes e conceitos`

## Melhorias futuras

- Agregar também **por trimestre** (a coluna `trimestre` já é criada) e montar uma **tabela cruzada** de mês por categoria
- Projeção simples de tendência com **média móvel** dos últimos meses
- Gráficos adicionais, como histograma e mapa de calor
- Receber o caminho do CSV por **argumento de linha de comando**
- **Testes automatizados** para as funções de limpeza e de segmentação

## Ferramentas utilizadas

- Python 3.10+
- Google Colab / VS Code
- Bibliotecas: pandas, numpy, matplotlib, seaborn, json, re, os, random e datetime
- Git e GitHub para versionamento
- [Trello / GitHub Projects] para o Kanban

## Vídeo de demonstração

[inserir o link do Google Drive ou do YouTube aqui]
