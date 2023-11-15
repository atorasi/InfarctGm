import asyncio
import random

from src.runner import Intrarct
from utils import logger
from config import KEYS_DIR, PROX_DIR, USE_PROXY, NEED_SLEEP, SLEEP_FROM, SLEEP_TO, THREADS, TEXT


with open(KEYS_DIR, 'r') as file:
    keys_list = [key.strip() for key in file]
    
list_proxy = [None] * len(keys_list)

if USE_PROXY:
    with open(PROX_DIR, 'r') as file:
        list_proxy = [proxy.strip() for proxy in file]
    

async def run_script(index: int, key: str, proxy: str):
    client = Intrarct(key, proxy)
    logger.info(f'Acc.{index} | {client.address} | Starting to execute the account')
    code, text = await client.connect_wallet()
    logger.info(f'Acc.{index} | {client.address} | Response code: {code} - {text} ')
    code, text = await client.claim_hueta()
    logger.info(f'Acc.{index} | {client.address} | Response code: {code} - {text} ')
    if NEED_SLEEP:
        time = random.randint(SLEEP_FROM, SLEEP_TO)
        logger.info(f'Acc.{index} | {client.address} | Sleeping {time} seconds ')
        await asyncio.sleep(time)


async def main():
    tasks = []
    for index, (key, proxy) in enumerate(zip(keys_list, list_proxy), start=1):
        task = run_script(index, key, proxy)
        tasks.append(task)

        if len(tasks) == THREADS:
            await asyncio.gather(*tasks)
            tasks.clear()

    if tasks:
        await asyncio.gather(*tasks)
        
        
if __name__ == '__main__':
    print(f'{TEXT}\n')
    
    asyncio.run(main())
    
    print('\n\nThank you for using the software. </3')
    print('donate : | 0x4163dfa9eE4A25e950ce1a0A2221FafA29fe2df6 | :3')
    input('\nPress "ENTER" To Exit..')
    