import aiohttp
import asyncio
from re import compile
import random
import time
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TIMEOUT = 5
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, như Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, như Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, như Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 như Mac OS X) AppleWebKit/605.1.15 (KHTML, như Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, như Gecko) Chrome/90.0.4430.93 Safari/537.36",
]

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/'
}

REGEX = compile(r'(\d{1,3}(?:\.\d{1,3}){3})\s*(?::|\s+)(\d{1,5})')
MAX_CONCURRENT_TASKS = 50

scrapped_proxies = []

def is_valid_port(port):
    return 1 <= port <= 65535

async def scrap(url: str, semaphore):
    temp_proxies = 0
    async with semaphore:
        try:
            async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
                headers = HEADERS.copy()
                headers['User-Agent'] = random.choice(USER_AGENTS)
                async with session.get(
                    url, headers=headers, 
                    timeout=aiohttp.ClientTimeout(total=TIMEOUT)
                ) as response:
                    html = await response.text()
                    if tuple(REGEX.finditer(html)):
                        for match in REGEX.finditer(html):
                            ip, port = match.groups()
                            if is_valid_port(int(port)):
                                proxy = f"{ip}:{port}"
                                with open('proxiess.txt', 'a') as proxies:
                                    proxies.write(f'{proxy}\n')
                                scrapped_proxies.append(proxy)
                                temp_proxies += 1
                        print(f' [~] Found: {temp_proxies} Proxies In {url}')
                    else:
                        print(f' [~] Can\'t Find Proxies At: {url}')
        except Exception as e:
            with open('errors.txt', 'a') as errors:
                errors.write(f'[ERROR AT]: {url} {e}\n')
        finally:
            await asyncio.sleep(random.uniform(1, 3))

async def main():
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    with open('sources.txt', 'r') as sources:
        urls = sources.read().splitlines()
        await asyncio.gather(
            *[scrap(url, semaphore) for url in urls]
        )
        
        print(f'\n [!] Done Scraping...\n [~] Total Proxies: {len(scrapped_proxies)}')

if __name__ == "__main__":
    asyncio.run(main())
