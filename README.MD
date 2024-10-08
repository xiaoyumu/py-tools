Tools for downloading models from civitai or huggingface for headless environments.
---


ci-dl.py
--

Tools for downloading models or retrieve actual download links from Civitai API. API Key required.

Download the model to specific output folder.
```commandline    
python ci-dl.py \
    --url "Model URL" \
    --output /workspace/ComfyUI/models/checkpoints/SDXL/
```


Download the model to specific output folder via socks5 proxy
```commandline    
python ci-dl.py \
    --url "Model URL" \
    --output /workspace/ComfyUI/models/checkpoints/SDXL/ \
    --proxy "socks5h://localhost:1080"
```

Inspect the download url and file name for the model via socks5 proxy. Inspect mode is very useful when you download speed is very slow with browser direct download. With this mode, you can get the real download link, then you can download the model file with your favorite download tools.
You can retrieve the download url by **right-clicking** on the ```Download``` button in CIVITAI model page, then select "```Copy Link Address```" (Chrome).
```commandline    
python ci-dl.py \
    --url "Model URL" \
    --proxy "socks5h://localhost:1080" \
    --inspect
```


hf-dl.py
--

Tools for downloading model files from huggingface.co.

Download model files to specific output folder and overwrite exist file.
```commandline
python hf-dl.py \
    --url "Model file url" \
    --output /workspace/ComfyUI/models/checkpoints/SDXL/ \
    --proxy "socks5h://localhost:1080" \
    --overwrite
```