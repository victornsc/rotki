import pytest
from eth_utils import is_checksum_address

from rotkehlchen.assets.asset import Asset, EthereumToken
from rotkehlchen.assets.resolver import AssetResolver, asset_type_mapping
from rotkehlchen.errors import DeserializationError, UnknownAsset
from rotkehlchen.externalapis.coingecko import Coingecko
from rotkehlchen.typing import AssetType


def test_unknown_asset():
    """Test than an unknown asset will throw"""
    with pytest.raises(UnknownAsset):
        Asset('jsakdjsladjsakdj')


def test_repr():
    btc_repr = repr(Asset('BTC'))
    assert btc_repr == '<Asset identifier:BTC name:Bitcoin symbol:BTC>'


def test_asset_hashes_properly():
    """Test that assets can be hashed and are equivalent to the canonical string"""
    btc_asset = Asset('BTC')
    eth_asset = Asset('ETH')
    mapping = {btc_asset: 100, 'ETH': 200}

    assert btc_asset in mapping
    assert eth_asset in mapping
    assert 'BTC' in mapping
    assert 'ETH' in mapping

    assert mapping[btc_asset] == 100
    assert mapping[eth_asset] == 200
    assert mapping['BTC'] == 100
    assert mapping['ETH'] == 200


def test_asset_equals():
    btc_asset = Asset('BTC')
    eth_asset = Asset('ETH')
    other_btc_asset = Asset('BTC')

    assert btc_asset == 'BTC'
    assert btc_asset != eth_asset
    assert btc_asset != 'ETH'
    assert btc_asset == other_btc_asset
    assert eth_asset == 'ETH'


def test_ethereum_tokens():
    rdn_asset = EthereumToken('RDN')
    assert rdn_asset.ethereum_address == '0x255Aa6DF07540Cb5d3d297f0D0D4D84cb52bc8e6'
    assert rdn_asset.decimals == 18
    assert rdn_asset.asset_type == AssetType.ETH_TOKEN

    with pytest.raises(DeserializationError):
        EthereumToken('BTC')


def test_tokens_address_is_checksummed():
    """Test that all ethereum saved token asset addresses are checksummed"""
    for _, asset_data in AssetResolver().assets.items():
        asset_type = asset_type_mapping[asset_data['type']]
        if asset_type not in (AssetType.ETH_TOKEN_AND_MORE, AssetType.ETH_TOKEN):
            continue

        msg = (
            f'Ethereum token\'s {asset_data["name"]} ethereum address '
            f'is not checksummed {asset_data["ethereum_address"]}'
        )
        assert is_checksum_address(asset_data['ethereum_address']), msg


def test_coingecko_identifiers_are_reachable():
    """
    Test that all assets have a coingecko entry and that all the identifiers exist in coingecko
    """
    coingecko = Coingecko()
    all_coins = coingecko.all_coins()
    for identifier, asset_data in AssetResolver().assets.items():
        asset_type = asset_type_mapping[asset_data['type']]
        if asset_type == AssetType.FIAT:
            continue

        coingecko_str = asset_data.get('coingecko', None)
        msg = f'Asset {identifier} does not have a coingecko entry'
        assert coingecko_str is not None, msg
        if coingecko_str != '':
            found = False
            for entry in all_coins:
                if coingecko_str == entry['id']:
                    found = True
                    break

        suggestions = []
        if not found:
            for entry in all_coins:
                if entry['symbol'].upper() == asset_data['symbol']:
                    suggestions.append((entry['id'], entry['name'], entry['symbol']))

        msg = f'Asset {identifier} coingecko mapping does not exist.'
        if len(suggestions) != 0:
            for s in suggestions:
                msg += f'\nSuggestion: id:{s[0]} name:{s[1]} symbol:{s[2]}'
        assert found, msg
