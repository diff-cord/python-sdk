from typing import Any
import aiohttp

from diffcord.error import InvalidTokenException, ServerException, HTTPException, RateLimitException


class HTTPApi:

    def __init__(self, token: str, base_url: str):
        self.token: str = token
        self.base_url: str = base_url

        headers = {
            "x-api-key": self.token,
            "Content-Type": "application/json",
            "User-Agent": f"Diffcord-Python-SDK",
        }

        self.session = aiohttp.ClientSession(headers=headers)

    async def make_request(self, method: str, path: str, **kwargs: Any) -> Any:
        """ Make a request to the Diffcord API.
        :param: method: The method of the request
        :param: path: The path of the request
        :param: kwargs: The kwargs of the request
        :return: The response from the Diffcord API
        """
        async with self.session.request(method, f"{self.base_url}{path}", **kwargs) as response:
            json_data: dict = await response.json()

            if response.status == 401:
                if json_data["error"]["code"] == "ERR_INVALID_API_KEY":
                    raise InvalidTokenException(json_data["error"], response)

                raise HTTPException(response.status, json_data["error"]["message"], json_data["error"]["code"])

            if response.status == 500:
                raise ServerException(json_data["error"], response)

            if response.status == 429:
                raise RateLimitException(json_data["error"], response)

            if not response.ok:

                try:
                    raise HTTPException(response.status, json_data["error"]["message"], json_data["error"]["code"])
                except Exception:
                    raise HTTPException(response.status, "ERROR", "ERR_CODE")

            if json_data is None:
                return

            return json_data["data"]

    async def close_requests(self) -> None:
        """ Close the aiohttp session.
        """
        await self.session.close()
