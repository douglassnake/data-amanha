# Publicação do observatório

## GitHub
Código: https://github.com/douglassnake/data-amanha

## Streamlit Community Cloud
1. Acesse https://share.streamlit.io/ e entre com sua conta autorizada.
2. Selecione **Create app** > **Deploy a public app from GitHub**.
3. Repositório: `douglassnake/data-amanha`; branch: `main`; main file path: `app.py`.
4. Escolha uma URL livre e a versão do Python 3.12 (se houver escolha).
5. Clique em **Deploy**.
6. Confira as abas, consultas externas, avisos e logs; compartilhe somente após os testes.

O GitHub Pages não executa Streamlit/Python. O aplicativo é independente do governo; não o anuncie como sistema oficial ou como fonte primária de alertas da Defesa Civil.

## Alternativa Docker
```bash
docker compose up -d --build
```
O `compose.yaml` publica apenas em 127.0.0.1:18501, exigindo proxy HTTPS e controle de acesso para expor externamente.
