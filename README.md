# Observatório de Instabilidade Global

Painel analítico **independente**, com interface de inspiração institucional, desenvolvido em Streamlit. Compila recursos de monitoramento de notícias e desastres, indicadores históricos, cenários e mercados.

> **Não é um site oficial do governo ou da Defesa Civil.** A identidade visual utiliza princípios gerais do [Padrão Digital de Governo](https://www.gov.br/ds), sem uso de marcas oficiais ou alegação de certificação. O projeto não deve ser divulgado como fonte de alertas oficiais.

## Funcionalidades

- Índice histórico de 1900 a 2026, parâmetros e exportação CSV
- Previsões exploratórias, tendências e cenários
- Correlações, rupturas e análise espectral
- Setores de mercado, ETFs e ações
- Índices mundiais, câmbio, criptoativos e commodities
- Aba **Mercado observado**: cotações reais, horários de observação, fonte, nível de atualização e exportação CSV
- Coinbase Exchange para preços recentes de criptoativos; Yahoo Finance para barras indicativas de mercado; Banco Central (SGS 432 e 433) para referências oficiais
- Sinais macro de natureza heurística
- Notícias gerais, conflitos, governos e Defesa Civil local
- Consultas GDACS, NASA EONET, GDELT, feeds RSS e links oficiais

**A série histórica distribuída em `data/` é heurística e NÃO consiste em dados oficiais anuais validados.** Deve ser substituída por séries documentadas antes de qualquer uso técnico para decisões. Rankings setoriais não representam retornos esperados em porcentagem nem aconselhamento financeiro.

## Execução local

Pré-requisito: Python 3.12.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

O dashboard fica normalmente em `http://localhost:8501`.

## Publicação atual: GitHub + Render

**Aplicativo online:** https://data-amanha.onrender.com

**Código:** https://github.com/douglassnake/data-amanha

O serviço gratuito do Render pode dormir por inatividade. Deploys são acionados automaticamente a partir da branch main. O painel não contém credenciais nem operações de corretora.

## Alternativa: Streamlit Community Cloud

O GitHub **não executa o Streamlit em GitHub Pages**. Publique o código no repositório `douglassnake/data-amanha` e execute o aplicativo na [Streamlit Community Cloud](https://share.streamlit.io/).

1. O repositório utilizado é **[`douglassnake/data-amanha`](https://github.com/douglassnake/data-amanha)**, atualmente público. Não inclua dados pessoais, segredos ou informações restritas.
2. Envie os arquivos desta pasta para a raiz do repositório.
3. Acesse https://share.streamlit.io, escolha **Create app** e selecione repositório, branch `main` e arquivo `app.py`.
4. Escolha um subdomínio e finalize o deploy; a URL real é atribuída pela plataforma.
5. Teste a abertura no celular, as fontes, o upload CSV e as abas de exportação.
6. Antes de exposição pública, valide a política de privacidade, as fontes externas, acessibilidade, logs e confiabilidade do monitoramento.

**Atenção:** não publique senhas, tokens, chaves API nem dados de cidadãos; use o painel de secrets da hospedagem quando necessário.

### Comandos Git opcionais

```bash
git init
git add .
git commit -m "Publicação inicial - observatório institucional"
git branch -M main
git remote add origin https://github.com/douglassnake/data-amanha.git
git push -u origin main
```

O repositório acima é o endereço efetivo do código-fonte; a URL pública do aplicativo só existirá após a implantação no serviço de hospedagem.

## Hospedagem local / institucional (ZimaOS ou Linux)

```bash
docker compose up -d --build
```

O serviço fica disponível apenas no host em `127.0.0.1:18501`. Para acesso externo, use proxy HTTPS e configure autenticação, proteção de cabeçalhos e política de acesso antes de expor o serviço. Não execute junto a serviços municipais de produção sem homologação isolada.

## Governança e referências

Consulte `POLITICA_DE_DADOS.md` e `ACESSIBILIDADE.md`. As fontes estão visíveis no próprio app. Este painel NÃO substitui canais oficiais de emergências (Defesa Civil, INMET, CBMMG ou órgãos municipais competentes).

As dependências aceitam faixas de versões; para implantação auditável, gere e mantenha um lockfile com versões testadas e análise de vulnerabilidades.

## Situação da publicação

Código no GitHub: https://github.com/douglassnake/data-amanha

**O Render já hospeda este aplicativo.** O Streamlit Community Cloud é alternativa, não depende de nova publicação para o serviço atual.

## Qualidade e disponibilidade de preços

- **Criptoativos:** a Coinbase Exchange informa o horário do último negócio; não há garantia de negociação a cada segundo.
- **Ações, ETFs, índices, câmbio e commodities:** o yfinance consulta barras de 5 minutos do Yahoo Finance. Há possíveis atrasos, restrições de bolsa, horários de negociação e indisponibilidade. A tabela mostra hora da observação e é sempre classificada como *indicativa*.
- **Referências Brasil:** meta Selic (Banco Central, SGS 432, % ao ano) e IPCA (SGS 433, % no mês) são séries oficiais atualizadas conforme publicação, não cotações instantâneas.
- **Consulta:** fragmento do Streamlit verifica novamente a cada 60 segundos durante uso ativo; caches de 30 segundos para Coinbase, 120 segundos para barras indicativas e 1 hora para BCB. A data da consulta nunca substitui o horário da observação.
- **Proteção:** fontes que falharem não serão substituídas por valores fictícios. Os dados históricos heurísticos nunca serão confundidos com preços observados.

### Cotações licenciadas (opcional)

A aplicação já oferece integração condicional com [Twelve Data](https://twelvedata.com/docs), mas **não está ativa por padrão**. Antes de exibir dados licenciados publicamente, obtenha permissão expressa para redistribuição no site e configure na hospedagem (não no GitHub):

- TWELVE_DATA_API_KEY = segredo do fornecedor
- MARKET_PUBLIC_DISPLAY_LICENSED = 1 **somente se o contrato permitir exibição pública**

O plano gratuito do fornecedor pode ser restrito a uso pessoal/interno; a existência de uma API key não implica autorização para mostrar dados ao público. Para monitoramento de trading, use um feed de bolsa licenciado, com SLA e validação de atraso.

### Testes

```bash
python -m py_compile app.py
python -m unittest discover -s tests -v
```

Os testes verificam recusa de preços inválidos, exigência de timestamp real na Coinbase e tratamento de barras com fuso ausente.
