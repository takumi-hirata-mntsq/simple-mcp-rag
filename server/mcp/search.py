from contextlib import asynccontextmanager
from dataclasses import dataclass
from fastapi import FastAPI
from elasticsearch import Elasticsearch
from mcp.server.fastmcp import FastMCP, Context
from typing import AsyncIterator, Any
import os
import logging

logger = logging.getLogger(__name__)


def get_es_client():
    es_host = os.getenv("ES_HOST", "localhost")
    es_port = os.getenv("ES_PORT", "9200")
    es_user = os.getenv("ES_USER", "")
    es_password = os.getenv("ES_PASSWORD", "")

    es_client = Elasticsearch(
        [f"http://{es_host}:{es_port}"],
        http_auth=(es_user, es_password),
    )

    return es_client


@dataclass
class AppContext:
    es_client: Elasticsearch


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[AppContext]:
    es_client = get_es_client()
    try:
        yield AppContext(es_client=es_client)
    finally:
        es_client.close()


mcp = FastMCP(name="SearchServer", stateless_http=True, lifespan=lifespan)


@mcp.tool(description="Elasticsearchで検索を実行するツール")
def search(index: str, query_body: dict[str, Any], ctx: Context) -> Any:
    logger.info("search tool called")
    logger.debug(f"index: {index}, query: {query_body}")
    es_client: Elasticsearch = ctx.request_context.lifespan_context.es_client
    response = es_client.search(index=index, body=query_body)
    return response


@mcp.tool(description="Elasticsearchのインデックスを取得するツール")
def get_indices(ctx: Context) -> Any:
    logger.info("get_indices tool called")
    es_client: Elasticsearch = ctx.request_context.lifespan_context.es_client
    response = es_client.indices.get_alias("*")
    return response


@mcp.tool(description="Elasticsearchで指定したインデックスのマッピングを取得するツール")
def get_mapping(index: str, ctx: Context) -> Any:
    logger.info("get_mapping tool called")
    logger.debug(f"index: {index}")
    es_client: Elasticsearch = ctx.request_context.lifespan_context.es_client
    response = es_client.indices.get_mapping(index=index)
    return response
