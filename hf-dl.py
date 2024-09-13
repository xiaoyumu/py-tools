#!/usr/bin/env python3
import os
import argparse
import requests
from tqdm import tqdm
from urllib.parse import urlparse, unquote


def download_file(url, output_folder, overwrite=False, http_proxy=None):
    # Check if the output path is a file
    if os.path.isfile(output_folder):
        print(f"Error: The specified output path '{output_folder}' is a file, not a folder.")
        return

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Extract the filename from the URL
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    filename = unquote(filename)  # Decodes any percent-encoded characters in the filename
    file_path = os.path.join(output_folder, filename)

    # Check if file already exists
    if os.path.exists(file_path) and not overwrite:
        print(f"Error: File '{file_path}' already exists. Use --overwrite to overwrite it.")
        return
    print(f"Downloading {filename}:")

    proxies = {
        'http': http_proxy,
        'https': http_proxy,
    } if http_proxy else None

    # Download the file with progress bar
    response = requests.get(url, stream=True, proxies=proxies)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibi byte
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

    with open(file_path, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()

    if total_size != 0 and progress_bar.n != total_size:
        print("Error: Something went wrong during the download.")
    else:
        print(f"File downloaded successfully: {file_path}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Download huggingface model from URL to local folder.",
                                     )
    parser.add_argument("--url", type=str, required=True, help="URL of the file to download.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output folder.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing file if it exists.")
    parser.add_argument("--proxy", type=str, required=False,
                        help="Http proxy, set to use proxy to download files. Support socks5 proxies. "
                             "Use socks5h:// to enable host resolving with socks5 proxy.")

    args = parser.parse_args()

    download_file(args.url, args.output, args.overwrite, args.proxy)
