# Liga SWU Price Scraper

Web scraper para monitoramento diário de preços do site ligaswu.com.br.

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Execução única
```bash
python liga_scraper.py
```

### Execução agendada (diária às 9:00)
```bash
python scheduler.py
```

## Funcionalidades

- Scraping das marcas 79 e 2 do Liga SWU
- Delays aleatórios para evitar bloqueios
- Headers de navegador real
- Retry automático em caso de falha
- Exportação em JSON e CSV
- Agendamento automático diário

## Arquivos gerados

- `liga_precos_YYYYMMDD_HHMMSS.json` - Dados em formato JSON
- `liga_precos_YYYYMMDD_HHMMSS.csv` - Dados em formato CSV

## Estrutura dos dados

Cada produto contém:
- `name`: Nome do produto
- `price`: Preço extraído
- `link`: Link para o produto
- `image`: URL da imagem
- `scraped_at`: Timestamp da coleta
- `marca`: Identificador da marca (apenas no CSV)