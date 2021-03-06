import json
from typing import Any, Dict, List, NamedTuple, Optional, Union, overload
from urllib.parse import urlencode

import requests
from typing_extensions import Literal

from rotkehlchen.assets.asset import Asset
from rotkehlchen.errors import RemoteError
from rotkehlchen.utils.serialization import rlk_jsonloads


class CoingeckoImageURLs(NamedTuple):
    thumb: str
    small: str
    large: str


class CoingeckoAssetData(NamedTuple):
    identifier: str
    symbol: str
    name: str
    description: str
    images: CoingeckoImageURLs


class Coingecko():

    def __init__(self) -> None:
        self.session = requests.session()
        self.session.headers.update({'User-Agent': 'rotkehlchen'})

    @overload  # noqa: F811
    def _query(
            self,
            module: Literal['coins/list'],
            subpath: Optional[str] = None,
            options: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        ...

    @overload  # noqa: F811
    def _query(
            self,
            module: Literal['coins'],
            subpath: Optional[str] = None,
            options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        ...

    def _query(
            self,
            module: str,
            subpath: Optional[str] = None,
            options: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Performs a coingecko query

        May raise:
        - RemoteError if there is a problem querying coingecko
        """
        if options is None:
            options = {}
        url = f'https://api.coingecko.com/api/v3/{module}/'
        if subpath:
            url += subpath
        try:
            response = self.session.get(f'{url}?{urlencode(options)}')
        except requests.exceptions.ConnectionError as e:
            raise RemoteError(f'Coingecko API request failed due to {str(e)}')

        if response.status_code != 200:
            raise RemoteError(
                f'Coingecko API request {response.url} failed with HTTP status '
                f'code: {response.status_code}',
            )

        try:
            decoded_json = rlk_jsonloads(response.text)
        except json.decoder.JSONDecodeError as e:
            raise RemoteError(f'Invalid JSON in Kraken response. {e}')

        return decoded_json

    def asset_data(self, asset: Asset) -> CoingeckoAssetData:
        """

        May raise:
        - UnsupportedAsset() if the asset is not supported by coingecko
        - RemoteError if there is a problem querying coingecko
        """
        options = {
            # Include all localized languages in response (true/false) [default: true]
            'localization': False,
            # Include tickers data (true/false) [default: true]
            'tickers': False,
            # Include market_data (true/false) [default: true]
            'market_data': False,
            # Include communitydata (true/false) [default: true]
            'community_data': False,
            # Include developer data (true/false) [default: true]
            'developer_data': False,
            # Include sparkline 7 days data (eg. true, false) [default: false]
            'sparkline': False,
        }
        gecko_id = asset.to_coingecko()
        data = self._query(
            module='coins',
            subpath=f'{gecko_id}',
            options=options,
        )

        try:
            parsed_data = CoingeckoAssetData(
                identifier=gecko_id,
                symbol=data['symbol'],
                name=data['name'],
                description=data['description']['en'],
                images=CoingeckoImageURLs(
                    thumb=data['image']['thumb'],
                    small=data['image']['small'],
                    large=data['image']['large'],
                ),
            )
        except KeyError as e:
            raise RemoteError(f'Missing expected key entry {e} in coingecko coin data response')

        return parsed_data

    def all_coins(self) -> List[Dict[str, Any]]:
        return self._query(module='coins/list')
