import json

import httpx
from web3 import AsyncWeb3 
from eth_account.messages import encode_defunct
from fake_useragent import UserAgent

from utils import script_exceptions


class Intrarct:
    def __init__(self, private_key: str, proxy: str = None) -> None:
        self.private = private_key
        self.proxy = proxy
        if proxy != None:
            self.proxy  = {
                "http://": "http://",
                "https://": "http://",
            }   
        
        self.w3 = AsyncWeb3()
        self.account = AsyncWeb3().eth.account.from_key(self.private)
        self.address = self.account.address
        
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://www.intract.io',
            'Referer': 'https://www.intract.io/',
            'User-Agent': UserAgent(browsers=["chrome", "edge", "firefox"]).random,
        }
        
        self.session = httpx.AsyncClient(headers=self.headers, proxies=self.proxy)
    
    @script_exceptions
    async def get_nonce(self) -> str:
        json_data = {
            'walletAddress': self.address,
        }
        r = await self.session.post(
            'https://api.intract.io/api/qv1/auth/generate-nonce', 
            json=json_data,
        )
        
        nonce = json.loads(r.text)['data']['nonce']
        
        return nonce
    
    @script_exceptions
    async def get_signature(self) -> str:
        message_text = f'Please sign this message to verify your identity. Nonce: {await self.get_nonce()}'
        
        message = encode_defunct(text=message_text)
        sign = self.w3.eth.account.sign_message(message, private_key=self.private)
        signature = self.w3.to_hex(sign.signature)
        
        return signature

    @script_exceptions
    async def connect_wallet(self) -> int|str:
        json_data = {
            'signature': await self.get_signature(),
            'userAddress': self.address,
            'chain': {
                'id': 59144,
                'name': 'Linea',
                'network': 'Linea',
                'nativeCurrency': {'decimals': 18, 'name': 'Ether', 'symbol': 'ETH'},
                'rpcUrls': {
                    'public': {'http': ['https://linea.drpc.org']},
                    'default': { 'http': ['https://linea-mainnet.infura.io/v3/bfc263a4f3cf49998641d16c24fd0b46']},
                },
                'blockExplorers': {
                    'etherscan': { 'name': 'Lineascan', 'url': 'https://lineascan.build/'},
                    'default': { 'name': 'Lineascan', 'url': 'https://lineascan.build/'},
                },
                'unsupported': False,
            },
            'isTaskLogin': False,
            'width': '590px',
            'reAuth': False,
            'connector': 'metamask',
            'referralCode': None,
            'referralLink': None,
            'referralSource': None,
        }
        
        r = await self.session.post(
            'https://api.intract.io/api/qv1/auth/wallet',
            json=json_data,
        )
        text = "There's been some kind of mistake"
        if r.status_code == 200:
            text = 'Successfully connected the wallet to the site'
        
        return r.status_code, text
    
    async def claim_hueta(self) -> bool:
        r = await self.session.post('https://api.intract.io/api/qv1/auth/gm-streak')
        
        await self.session.aclose()
        
        if r.status_code == 200:
            text = f"Streak Count : {json.loads(r.text)['streakCount']}"
            return r.status_code, text
        return r.status_code, "There's been some kind of mistake"
