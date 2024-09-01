#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, parse_qs, unquote

import requests
from colorama import Fore, Style
from tqdm import tqdm

CHUNK_SIZE = 1638400
TOKEN_FILE = Path.home() / '.civitai' / 'config'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'


def print_info(message: str):
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")


def print_error(message: str):
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")


def get_args():
    parser = argparse.ArgumentParser(
        description='CivitAI Downloader',
    )

    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='CivitAI Download URL, eg: https://civitai.com/api/download/models/46846'
    )

    parser.add_argument(
        '--output',
        type=str,
        required=False,
        help='Output path, eg: /workspace/stable-diffusion-webui/models/Stable-diffusion'
    )

    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing file if it exists.")

    parser.add_argument("--inspect", action="store_true",
                        help="Set to true to inspect the actual model download URL and file name. Default is true.")

    parser.add_argument("--proxy", type=str, required=False,
                        help="Specify a proxy server, e.g., http://proxy.example.com:8080")

    return parser.parse_args()


def get_token():
    try:
        print(f"Loading API token from {TOKEN_FILE} ...")
        with open(TOKEN_FILE, 'r') as file:
            token = file.read().strip()
            return token
    except Exception as e:
        return None


def store_token(token: str):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, 'w') as file:
        file.write(token)


def prompt_for_civitai_token():
    print("CivitAI API token is needed to download models. You can get one at here "
          "(https://civitai.com/user/account) at API Keys section.")
    token = input('Please enter your CivitAI API token: ')
    store_token(token)
    return token


def download_file(url: str, output_path: str, overwrite: bool, inspect: bool, token: str,
                  http_proxy: Optional[str] = None):
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': USER_AGENT,
    }

    proxies = {
        'http': http_proxy,
        'https': http_proxy,
    } if http_proxy else None

    # Disable automatic redirect handling
    session = requests.Session()
    response = session.head(url, headers=headers, allow_redirects=False, proxies=proxies)

    if response.status_code in [301, 302, 303, 307, 308]:
        redirect_url = response.headers['Location']

        # Extract filename from the redirect URL
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        content_disposition = query_params.get('response-content-disposition', [None])[0]

        if content_disposition:
            filename = unquote(content_disposition.split('filename=')[1].strip('"'))
        else:
            raise Exception('Unable to determine filename')

        if inspect:
            print()
            print_info(f"Actual Filename: {filename}")
            print_info(f"Actual Download URL: \n{redirect_url}")
            exit(0)

        response = session.get(redirect_url, headers=headers, stream=True, proxies=proxies)
    elif response.status_code == 404:
        raise Exception('File not found')
    else:
        raise Exception('No redirect found, something went wrong')

    total_size = int(response.headers.get('Content-Length', 0))

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    output_file = os.path.join(output_path, filename)

    if os.path.exists(output_file) and not overwrite:
        raise Exception(f"Output file {output_file} already exists. Add --overwrite option to overwrite existing file.")

    with open(output_file, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                pbar.update(len(chunk))
    print()
    print_info(f'Download completed. File saved as: {filename}')
    print_info(f'Full Path: {output_file}')


def main():
    args = get_args()
    token = get_token()

    if not token:
        token = prompt_for_civitai_token()

    try:
        download_file(args.url, args.output, args.overwrite, args.inspect, token, args.proxy)
    except Exception as e:
        print_error(f'\nERROR: {e}')


if __name__ == '__main__':
    """
    Download the model to specific output folder via socks5 proxy
    python ci-dl.py \
           --url "Model URL" \
           --output /workspace/ComfyUI/models/checkpoints/SDXL/ \
           --proxy "socks5h:localhost:1080"
    """
    main()
