import os
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from google import genai
from google.genai import types
import logging
import sys


root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
root.addHandler(handler)

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """\
あなたは、ユーザーの質問に対してわかりやすく正確に回答するAIアシスタントです。
以下のプロセスに従って、ユーザーの質問に対する回答を生成してください。

# タスク

1. **質問分析:** ユーザーの質問内容を正確に把握する。
2. **情報検索 (Function Calling):** インデックス一覧を取得し、質問に関連するインデックスを選択する。インデックスのマッピングを確認する。最適な検索クエリを生成し、最適な関数で社内文書を検索する。
3. **回答生成:** 検索結果の情報のみに基づいて回答を生成する。情報がない場合はその旨を伝える。
"""


async def main():
    mcp_server_host = os.getenv("MCP_SERVER_HOST", "localhost")
    mcp_server_port = os.getenv("MCP_SERVER_PORT", "8000")

    client = genai.Client()
    model_name = "gemini-2.5-flash-preview-05-20"
    prompt = "昨日の売上をカテゴリ別に集計してください。"
    contents: list[types.Content] = []

    async with streamablehttp_client(f"http://{mcp_server_host}:{mcp_server_port}/search/mcp/") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0,
                tools=[session],  # type: ignore[arg-type]
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            )

            contents.append(
                types.UserContent(
                    parts=[types.Part(text=prompt)],
                )
            )

            response = await client.aio.models.generate_content(
                model=model_name,
                contents=contents,  # type: ignore[arg-type]
                config=config,
            )
            contents.append(response.candidates[0].content)  # type: ignore

            while contents[-1].parts[-1].function_call:  # type: ignore
                for part in contents[-1].parts:  # type: ignore
                    if part.text:
                        logger.debug(part.text)
                    if part.function_call:
                        function_call = part.function_call
                        assert function_call.name is not None and function_call.args is not None
                        logger.debug(function_call)

                        result = await session.call_tool(function_call.name, arguments=function_call.args)

                        contents.append(
                            types.UserContent(
                                parts=[
                                    types.Part(
                                        function_response=types.FunctionResponse.from_mcp_response(
                                            name=function_call.name, response=result
                                        )
                                    )
                                ],
                            )
                        )

                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=contents,  # type: ignore[arg-type]
                    config=config,
                )
                contents.append(response.candidates[0].content)  # type: ignore

            logger.info(contents[-1].parts[-1].text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
