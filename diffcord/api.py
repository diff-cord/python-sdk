from typing import Any

import httpx

from diffcord.error import InvalidTokenException, ServerException, HTTPException, RateLimitException


class HTTPApi:

    def __init__(self, token: str, base_url: str):
        self.token: str = token
        """ API Token """

        self.base_url: str = base_url
        """ Base URL of the API in which the requests will be made to """

        self.__headers = {
            "x-api-key": self.token,
            "Content-Type": "application/json",
            "User-Agent": f"Diffcord-Python-SDK",
        }

    async def make_request(self, method: str, path: str, **kwargs: Any) -> Any:
        """ Make a request to the Diffcord API.
        :param: method: The method of the request
        :param: path: The path of the request
        :param: kwargs: The kwargs of the request
        :return: The response from the Diffcord API
        """
        async with httpx.AsyncClient() as client:

            response = await client.request(method, self.base_url + path, **kwargs, headers=self.__headers)

            json_data = response.json()

            if response.status_code == 401:
                if json_data["error"]["code"] == "ERR_INVALID_API_KEY":
                    raise InvalidTokenException(json_data["error"], response)

                raise HTTPException(response.status_code, json_data["error"]["message"], json_data["error"]["code"])

            if response.status_code == 500:
                raise ServerException(json_data["error"], response)

            if response.status_code == 429:
                raise RateLimitException(json_data["error"], response)

            if not str(response.status_code).startswith("2"):

                try:
                    raise HTTPException(response.status_code, json_data["error"]["message"], json_data["error"]["code"])
                except Exception:
                    raise HTTPException(response.status_code, "ERROR", "ERR_CODE")

            if json_data is None:
                return

            return json_data["data"]
