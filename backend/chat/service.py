import json
import logging
from pathlib import Path

import pandas as pd
from openai import AsyncOpenAI, APIStatusError

from chat.tools import make_tools, tool_schema
from common.config import GROQ_API_KEY
from common.dummyjson import dummyjson

log = logging.getLogger("app.chat")

_SALES_FILE = Path(__file__).parent.parent.parent / "data" / "sales.json"
_MODEL = "openai/gpt-oss-120b"

_SYSTEM_PROMPT = """You are a helpful data assistant for a product management application.
You have access to sales data (~6 000 transactions), a product catalogue (~190 products), and user demographics.
Always call the appropriate tool to query real data before responding — never guess or fabricate numbers.
Always reply in the same language the user used — including refusals and error messages. If the user writes in Portuguese, every response must be in Portuguese, no exceptions.
Be concise: 2–3 sentences unless a ranked list is more useful. For product lists include the product name and units sold.
Never expose internal numeric IDs (such as product IDs, user IDs, warehouse IDs, sale IDs) in your replies — refer to things by their name instead."""


class ChatService:
    def __init__(self) -> None:
        # Created lazily on first use so the app (and the test suite) can import without a key.
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=GROQ_API_KEY,
            )
        return self._client

    def _get_sales_df(self) -> pd.DataFrame:
        with _SALES_FILE.open() as fh:
            return pd.DataFrame(json.load(fh)["sales"])

    async def _get_users_df(self) -> pd.DataFrame:
        data = await dummyjson.request(
            "GET", "/users", params={"limit": 0, "select": "id,age,gender,firstName,lastName"}
        )
        log.info("User demographics loaded (%s users)", len(data["users"]))
        return pd.DataFrame(data["users"])

    async def answer(self, question: str, history: list[dict] | None = None) -> str:
        from products.service import product_service
        from warehouses.service import warehouse_service

        sales_df = self._get_sales_df()
        users_df = await self._get_users_df()
        products = await product_service._all_products()
        products_map = {prod["id"]: prod for prod in products}

        tools = make_tools(sales_df, users_df, products_map, warehouse_service)
        tools_map = {fn.__name__: fn for fn in tools}
        tool_schemas = [tool_schema(fn) for fn in tools]

        messages: list[dict] = [{"role": "system", "content": _SYSTEM_PROMPT}]
        for entry in (history or []):
            messages.append({"role": entry["role"], "content": entry["text"]})
        messages.append({"role": "user", "content": question})

        try:
            while True:
                response = await self.client.chat.completions.create(
                    model=_MODEL,
                    messages=messages,
                    tools=tool_schemas,
                    tool_choice="auto",
                )
                msg = response.choices[0].message

                if not msg.tool_calls:
                    return msg.content or ""

                messages.append(msg)

                for tool_call in msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    log.info("Tool called: %s args=%s", fn_name, fn_args)
                    try:
                        result = tools_map[fn_name](**fn_args)
                    except Exception as exc:
                        result = {"error": str(exc)}
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    })

        except APIStatusError as exc:
            log.error("Groq API error %s: %s", exc.status_code, exc.message)
            if exc.status_code == 413:
                return "O histórico da conversa ficou demasiado longo. Limpa o histórico e tenta novamente."
            if exc.status_code == 429:
                return "Estou a receber demasiados pedidos neste momento. Aguarda um pouco e tenta novamente."
            return "Ocorreu um erro ao contactar o modelo de IA. Tenta novamente."


chat_service = ChatService()
