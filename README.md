# Airflow DAG Execution Metadata Collector

Este projeto tem como objetivo criar uma solução para coletar metadados de execução de Directed Acyclic Graphs (DAGs) do Apache Airflow e enviá-los para um banco de dados Cassandra usando Apache Kafka como intermediário.

## Pré-requisitos

Certifique-se de ter as seguintes ferramentas e bibliotecas instaladas antes de iniciar:

- Apache Airflow
- Apache Kafka
- Apache Cassandra
- Python 3.x
- Dependências Python listadas no arquivo `requirements.txt`

## Estrutura do Projeto

A estrutura do projeto pode ser organizada de uma maneira que facilite a compreensão e manutenção. Aqui está uma sugestão de estrutura para o projeto:

```
/nome-do-repositorio
│
├── README.md
│
├── /script
│   ├── entrypoint.sh
│
├── /src
│   ├── main.py
│   ├── config.py
│   ├── kafka_producer.py
│   ├── cassandra_connector.py
│   └── dag_metadata_collector.py
│
├── /tests
│   └── test_dag_metadata_collector.py
│
├── config.yml
├── Makefile
└── requirements.txt
```

**Explicação dos componentes:**

- **README.md** Fornece informações sobre como configurar, usar e contribuir para o projeto.

- **/script:** Este diretório contém o executável para inicializar o banco do Airflow.
  - `entrypoint.sh`: O arquivo contém os comandos a serem executados assim que o contêiner anexado for inicializado.

- **/src:** Este diretório contém o código-fonte principal do projeto. Aqui estão alguns detalhes sobre os arquivos:
  - `main.py`: O script principal que inicia a execução do coletor de metadados.
  - `config.py`: Módulo para manipular a configuração do projeto, lendo as configurações do arquivo `config.yml`.
  - `kafka_producer.py`: Módulo para interagir com o Apache Kafka e enviar dados.
  - `cassandra_connector.py`: Módulo para conectar e interagir com o Apache Cassandra.
  - `dag_metadata_collector.py`: Módulo responsável por coletar metadados da execução das DAGs no Airflow.

- **/tests:** Este diretório contém os testes unitários para garantir a robustez do código. No exemplo, há um arquivo `test_dag_metadata_collector.py` para testar a funcionalidade específica do coletor de metadados das DAGs.

- **config.yml:** Arquivo de configuração que contém as configurações do projeto, como informações de conexão para o Kafka e Cassandra.

- **Makefile:** Arquivo para facilitar o gerenciamento e execução de tarefas no projeto.

- **requirements.txt:** Arquivo que lista as dependências Python necessárias para executar o projeto.

## Configuração

1. **Configuração do Apache Airflow**: 

    Certifique-se de que o seu ambiente Airflow está configurado corretamente. Configure suas DAGs para incluir ganchos ou operadores necessários para enviar metadados.

2. **Configuração do Apache Kafka**:

    Instale e configure um servidor Apache Kafka. Certifique-se de fornecer as configurações corretas no arquivo de configuração do projeto.

3. **Configuração do Apache Cassandra**:

    Instale e configure um banco de dados Apache Cassandra. Defina as configurações adequadas no arquivo de configuração do projeto.

4. **Configuração do Projeto**:

    - Clone este repositório:

        ```bash
        git clone https://github.com/tiagornandrade/airflow-metadata-kafka-cassandra.git
        ```

    - Navegue até o diretório do projeto:

        ```bash
        cd airflow-metadata-kafka-cassandra
        ```

    - Instale as dependências Python:

        ```bash
        pip install -r requirements.txt
        ```

    - Configure os parâmetros no arquivo `config.yml` de acordo com as informações do seu ambiente.

## Uso

Execute o script principal para iniciar a coleta de metadados e envio para o Cassandra via Kafka:

```bash
python send_metadata_to_kafka_operator.py
```

Este script deve ser agendado para execução periódica ou integrado ao fluxo de execução das suas DAGs no Airflow.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir problemas (issues) e enviar pull requests.
