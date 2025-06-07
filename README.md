# Gemini Function Calling + MCP Streamable HTTP

これはGeminiのFunction Callingを使って、MCPサーバーをStreamable HTTP経由で呼び出す、Pythonで書かれたシンプルなRAGアプリケーションです。
使用する主なパッケージは次のとおりです:

- Geminiクライアント: Google Gen AI SDK
- MCPサーバー: FastAPI + FastMCP
- 検索エンジン: Elasticsearch
- （LangChainは使いません）

## 環境構築

### Python仮想環境

`uv` を使って仮想環境を構築します。
[公式ドキュメント](https://docs.astral.sh/uv/getting-started/installation/)に従って `uv` をインストールし、次のコマンドで仮想環境を作成してください。

```bash
uv sync
```

### Google Cloud

Vertex AIのGeminiを使用するため、Google Cloud CLIでログインします。
[公式ドキュメント](https://cloud.google.com/sdk/docs/install)に従って `gcloud` をインストールし、次のコマンドでログインしてください。

```bash
gcloud auth login
```

### Elasticsearchのサンプルデータ

データは何でも良いのですが、簡易的に動かすためにKibanaを使ってElasticsearchにサンプルデータをインポートします。

次のコマンドでElasticsearchとKibanaを起動してください。

```bash
docker compose up
```

http://localhost:5601 にアクセスし、Integration -> Sample dataを開いて次の3つのデータをインポートしてください。

- Sample eCommerce orders
- Sample flight data
- Sample web logs

## 実行方法

### サーバーの起動

```bash
uv run --env-file .env uvicorn server.main:app
```

### クライアントの実行

```bash
uv run --env-file .env client.py
```
