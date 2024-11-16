# Projeto Airflow 

Este projeto utiliza o Apache Airflow para orquestrar e agendar tarefas de scraping de citações a partir de uma URL definida. O processo também envolve o uso de bibliotecas como `requests`, `beautifulsoup4` e a conexão com um banco de dados PostgreSQL via `psycopg2`.

## Dependências Necessárias

Este projeto utiliza as seguintes bibliotecas Python e serviços para funcionar corretamente:

### 1. Bibliotecas Python

- **Apache Airflow**: Para orquestração e agendamento de tarefas.
  ```bash
  pip install apache-airflow

## Requests: Para realizar requisições HTTP e coletar dados de sites.
pip install requests

## BeautifulSoup4: Para fazer o scraping das páginas web.
pip install beautifulsoup4

## psycopg2: Biblioteca necessária para a conexão do Airflow com o banco de dados PostgreSQL.
pip install psycopg2

2. Configuração do Banco de Dados
O Airflow precisa de um banco de dados para armazenar metadados, como informações sobre tarefas e DAGs executados.
O banco de dados configurado neste projeto é PostgreSQL, e a conexão é feita via PostgresHook do Airflow.
Para configurar o PostgreSQL, você precisa de um banco de dados funcionando e as credenciais de acesso, que podem ser fornecidas por meio de variáveis de ambiente ou diretamente no Airflow via Connections.
3. Variáveis do Airflow
O DAG do Airflow precisa de uma variável para definir a URL para o scraping. Você pode configurar isso no Airflow UI ou diretamente no código:
Variable: quotes_url - URL base para a coleta de citações.
4. Docker (Opcional)
Se você está utilizando o Docker para rodar o Airflow, você pode utilizar a imagem oficial do Apache Airflow com suporte para PostgreSQL.

## Instalação do Docker
docker pull apache/airflow:2.3.0

### Como Configurar e Executar o Airflow
1. Instalando o Airflow
Configuração inicial: Após instalar o Apache Airflow, configure o banco de dados do Airflow executando o comando:

airflow db init

Isso irá criar o banco de dados do Airflow para armazenar todos os metadados necessários para o gerenciamento de DAGs e execução de tarefas.

2. Iniciando o Servidor Web do Airflow
O Airflow fornece uma interface web para monitoramento e controle dos DAGs. Para iniciar o servidor web, utilize o seguinte comando:

airflow webserver --port 8080
O servidor web estará disponível em http://localhost:8080. Por padrão, a interface estará disponível nesta URL.

3. Inicializando o Scheduler
O Scheduler do Airflow é responsável por agendar e executar as tarefas conforme o intervalo configurado no DAG. Para iniciar o Scheduler, utilize o comando:

airflow scheduler

Isso permite que o Airflow execute os DAGs de acordo com os horários programados.

4. Executando o DAG
Airflow UI: Após iniciar o servidor web e o scheduler, você pode acessar a interface web do Airflow para executar e monitorar os DAGs.
Abra o navegador e acesse http://localhost:8080.
No painel, você verá o DAG scrape_quotes. Clique nele e você poderá visualizar as tarefas e iniciar a execução manualmente, se necessário.
5. Monitorando a Execução
Na interface web, é possível monitorar o progresso de cada tarefa, visualizar logs de execução e agendar novos runs.
Ao visualizar o DAG, você poderá ver se ele foi executado corretamente ou se houve falhas.

### Passos de Execução no Docker (Caso Utilize Docker)
Se você preferir usar Docker para rodar o Airflow, você pode configurar tudo dentro de containers Docker. Aqui está o passo a passo para configurar o Airflow com Docker:

1. Criação do docker-compose.yml
Utilize um arquivo docker-compose.yml para configurar o Airflow com suporte a PostgreSQL. Este arquivo irá configurar os serviços necessários para rodar o Airflow no Docker.

2. Iniciar os Containers Docker
Após configurar o docker-compose.yml, execute o comando para iniciar os containers:
bash

docker-compose up

3. Acessando o Airflow no Docker
Após iniciar os containers, você pode acessar a interface web do Airflow em http://localhost:8080, utilizando as credenciais definidas no arquivo docker-compose.yml.


### Como Testar e Executar
1. Verificar se as Dependências estão Instaladas
Certifique-se de que todas as bibliotecas necessárias estão instaladas no seu ambiente Python (ou Docker).
2. Iniciar o Airflow
No ambiente local, inicie o servidor web e o scheduler com os comandos mencionados acima.
3. Executar o DAG
Acesse a interface web do Airflow e execute o DAG scrape_quotes.
Você poderá ver os logs e o status da execução diretamente na interface.

1. Visão Geral do Pipeline
O pipeline de dados foi projetado para processar dados de maneira contínua e eficiente, permitindo ingestão em tempo real, validação, transformação e carregamento no Data Warehouse (DW). A arquitetura é dividida nas seguintes etapas:

Extração: Os dados são obtidos diretamente da Covid19 Brazil API ou via web scraping em http://quotes.toscrape.com. Esta etapa garante a coleta das informações necessárias para análise e monitoramento.
Processamento/Transformação: Os dados extraídos são atualizados uma vez por dia, utilizando um processo incremental que inclui validação, transformação e, quando necessário, atualização de registros existentes. Esta abordagem foi escolhida devido à falta de suporte a webhooks na API, impossibilitando notificações automáticas de alterações.
Carregamento (ETL): Dados processados são carregados no banco de dados de destino, para posterior análise.
A ingestão de dados ocorre diariamente em um processo incremental, garantindo que novos dados sejam refletidos no sistema de destino com consistência e eficiência.

2. Arquitetura do Pipeline
A arquitetura do pipeline é composta pelos seguintes componentes:

Banco de Dados de Origem: O sistema de origem é uma API (para dados COVID-19) e o site http://quotes.toscrape.com. Esses sistemas fornecem os dados a serem ingeridos.

Airflow como Orquestrador: O Airflow é utilizado para gerenciar e agendar as tarefas de extração, transformação e carga (ETL), garantindo a execução ordenada e monitorada de cada etapa do pipeline.

Tasks do Airflow: Cada etapa do pipeline (extração, transformação e carga) é implementada como uma tarefa individual, garantindo modularidade e fácil manutenção.
Transformações e Processamento: As transformações e validações são realizadas diretamente no Airflow, utilizando Python e bibliotecas específicas para garantir que os dados estejam consistentes e enriquecidos antes de serem enviados ao banco de dados de destino.

Banco de Dados de Destino: Os dados processados são armazenados em um banco de dados PostgreSQL, estruturados de forma incremental e atualizados diariamente.

Diferenciais da Arquitetura:

A ingestão não é em tempo real, mas o processo é otimizado para rodar diariamente, garantindo atualização frequente e consistência dos dados no sistema de destino.
3. ETL/ELT: Processos e Decisões
3.1 Extração de Dados (E)
Os dados são extraídos diretamente utilizando scripts Python, integrados ao Airflow, que realiza requisições à API (para os dados de COVID-19) ou consultas a bancos de dados PostgreSQL, dependendo do pipeline.

A extração é incremental, buscando apenas dados novos ou atualizados.
Decisões Tomadas:

O Airflow foi escolhido para gerenciar a orquestração de tarefas e garantir que o pipeline fosse modular e monitorável.
A extração incremental foi implementada para otimizar o desempenho, reduzindo o volume de dados processados diariamente.
Em vez de utilizar Debezium ou CDC, foram implementadas estratégias personalizadas de atualização com base em identificadores exclusivos.
3.2 Transformação de Dados (T)
Durante o processo de transformação, os dados são validados, normalizados, formatados e enriquecidos.

Validação: Verificação da conformidade com o formato esperado e ausência de valores inconsistentes ou ausentes.
Transformação: Conversão de tipos de dados, ajustes de fusos horários, entre outras.
Enriquecimento: Derivação de informações adicionais, como cálculos de totais ou enriquecimento com dados complementares de outras fontes.
Decisões Tomadas:

Todo o processamento de dados é realizado no Airflow utilizando Python e bibliotecas como Pandas para validação, transformação e enriquecimento.
O uso de transformações programáticas em Python garante flexibilidade para atender a regras de negócio específicas.
Implementação de um mecanismo de logs para rastrear falhas ou inconsistências no processamento.
3.3 Carregamento de Dados (L)
Após a transformação, os dados são carregados no banco de dados de destino (PostgreSQL) de forma incremental. A inserção é realizada utilizando uma estratégia de UPSERT (inserção ou atualização) para garantir que os registros existentes sejam atualizados quando necessário.

Decisões Tomadas:

O carregamento incremental foi escolhido para garantir a consistência dos dados e evitar duplicação no banco de destino.
As conexões são gerenciadas pelo Airflow para garantir segurança e eficiência na comunicação com o banco de dados.
4. Governança de Dados
4.1 Controle de Qualidade
Validação de Dados: Durante o processo de transformação, os dados são validados para garantir que a estrutura esperada esteja presente (por exemplo, verificar se 'data' está no dicionário antes de processá-lo).
Auditoria de Dados: O uso do Airflow permite rastrear todas as etapas do pipeline por meio de logs e histórico de execuções.
Monitoramento: O Airflow, com sua interface e notificações integradas, permite o gerenciamento de falhas e atrasos nas tarefas.
4.2 Segurança de Dados
Criptografia: Embora o script não mostre diretamente o uso de SSL/TLS, é uma boa prática configurar essas opções nas variáveis de conexão do PostgreSQL e ao acessar a API.
Controle de Acesso: O acesso ao banco de dados é feito por meio do PostgresHook, com credenciais armazenadas de maneira segura no Airflow.
4.3 Conformidade e Regulações
Diretrizes de Retenção: A lógica de atualização (INSERT ou UPDATE dependendo da data mais recente) garante que os dados antigos sejam mantidos ou substituídos apenas quando necessário.
Auditoria e Logs: O Airflow fornece rastreamento completo da execução de cada tarefa, permitindo revisões detalhadas em caso de necessidade.

### Documentação DAG scrape_quotes 

Este DAG foi projetado para realizar a coleta automatizada de citações de um site por meio de web scraping, e inseri-las no banco de dados PostgreSQL de maneira incremental. O processo envolve a navegação por várias páginas de citações, o scraping das informações relevantes e a inserção dos dados no banco de dados, verificando duplicatas antes de realizar a inserção.

Objetivo
Automatizar a coleta de citações de um site e a inserção desses dados em um banco de dados PostgreSQL, garantindo que as citações sejam inseridas de forma incremental, sem duplicação de registros.

Descrição das Tarefas
1. Tarefa scrape_quotes

Descrição: Realiza o scraping das citações de um site, acessando todas as páginas de citações disponíveis.
Lógica:
A URL base do site é recuperada da variável quotes_url do Airflow.
A cada página, a tarefa coleta todas as citações, incluindo texto, autor e tags associadas.
Verifica se há uma próxima página e, se houver, continua o scraping até que todas as páginas sejam processadas.
Tratamento de Erros:
Lança uma exceção caso ocorra um erro de requisição (se o status da resposta não for 200).
Critério de Avaliação:
Capacidade de navegar pelas páginas e extrair dados de forma eficiente e sem erros.
2. Tarefa insert_quotes_into_db

Descrição: Insere as citações coletadas no banco de dados PostgreSQL de forma incremental, evitando duplicações.
Lógica:
Conecta-se ao banco de dados PostgreSQL utilizando o PostgresHook.
Para cada citação, verifica se ela já existe no banco (com base no texto da citação).
Se a citação não existir, ela é inserida no banco. Caso contrário, é ignorada.
Tratamento de Erros:
Lança uma exceção se nenhuma citação for encontrada para inserção.
Logs são gerados em caso de falha na inserção.
Critério de Avaliação:
Eficiência na inserção de dados e verificação de duplicatas.
Configuração do DAG
start_date: 15 de novembro de 2024 (data inicial para execução).
schedule_interval: Executa diariamente à meia-noite (0 0 * * *).
catchup: Falso, evitando execuções retroativas desnecessárias.
Lógica de Execução
scrape_quotes: Realiza o scraping de todas as páginas de citações, coletando as citações e as armazenando.
insert_quotes_into_db: Insere as citações no banco de dados PostgreSQL de forma incremental, verificando e evitando duplicação.
Observações
1. Capacidade de lidar com APIs e Web Scraping:

Utiliza a biblioteca requests para realizar requisições HTTP e o BeautifulSoup para fazer o parsing HTML das páginas.
Navega pelas páginas de citações e extrai dados de forma eficiente, gerenciando links de páginas seguintes automaticamente.
2. Tratamento de Erros:

A tarefa scrape_quotes lida com falhas de requisição, lançando exceções quando o status da resposta não for 200.
A tarefa insert_quotes_into_db trata a possibilidade de não haver citações para inserir e também garante que apenas citações não duplicadas sejam inseridas.
3. Frequência e Eficiência na Coleta de Dados:

Executa diariamente para garantir que novas citações sejam coletadas e armazenadas com regularidade.
A inserção no banco é feita de forma eficiente, evitando reprocessamento de citações já existentes, otimizando o uso de recursos.

Automação: Elimina a necessidade de intervenção manual para coletar e inserir as citações, mantendo os dados sempre atualizados.
Escalabilidade: O DAG pode ser facilmente adaptado para coletar dados de outras fontes ou aumentar a frequência de execução.
Eficiência: Evita duplicações de dados e realiza inserções de forma incremental, mantendo o banco de dados otimizado.