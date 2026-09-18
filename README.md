# BiRefNet API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/bria/rmbg-2.0)

BiRefNet (Bilateral Reference Network) is a high-resolution dichotomous image segmentation model that separates a foreground subject from its background with clean edges on hair, fur and thin structures. This package is a BiRefNet API client for Python: one `pip install` gives you background removal as an HTTPS call, with no weights to download and no GPU to provision.

You get a blocking `run()` that returns the cutout URL, a submit-and-poll path for long batches, webhook delivery on completion, and a single runtime dependency (`httpx`). It is built for product backends, catalogue pipelines and notebooks that need a transparent-background cutout and do not want to own the inference stack.

> **Try it now:** [https://synexa.ai/explore/bria/rmbg-2.0](https://synexa.ai/explore/bria/rmbg-2.0) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About BiRefNet](#about-birefnet)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **No GPU to provision.** BiRefNet uses a Swin Transformer backbone and is meant for 1024×1024 inputs and above; comfortable inference needs a data-centre class card, and the 2048×2048 HR checkpoints need more. The hosted endpoint runs on managed GPUs.
- **No environment to maintain.** No PyTorch/CUDA version matching, no checkpoint mirrors, no custom ops to compile. Install, set a key, call `run()`.
- **No cold starts on your side.** Loading a segmentation model per request, or keeping one warm around the clock, is your cost when you self-host. Here you pay per prediction only.
- **A known price per image.** `bria/rmbg-2.0` is $0.018 per run; `danielgatis/rembg` and `supavisual/remove-background` are $0.01 per run. There is no idle GPU billing.

## Installation

```bash
pip install git+https://github.com/birefnet-dev/birefnet-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import birefnet_api

output = birefnet_api.run({
    "image_url": "https://example.com/input.png"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from birefnet_api import Client

client = Client(api_key="sk-...")
output = client.run({"image_url": "https://example.com/input.png"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`bria/rmbg-2.0`](https://synexa.ai/explore/bria/rmbg-2.0) | image-to-image | RMBG 2.0 cuts the subject out of an image and returns it on a transparent background. | $0.018 |
| [`supavisual/remove-background`](https://synexa.ai/explore/supavisual/remove-background) | image-to-image | Remove the background from an image, producing a clean cutout with a transparent background. | $0.01 |
| [`danielgatis/rembg`](https://synexa.ai/explore/danielgatis/rembg) | image-to-image | A fast, no-frills background remover that returns the subject on a transparent background. | $0.01 |

The default model is **`bria/rmbg-2.0`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `bria/rmbg-2.0`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `image_url` | file | yes | — | — | Image whose background should be removed (.jpg/.png/.webp) |

### `supavisual/remove-background`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `input_image` | file | yes | `https://files.synexa.ai/models/supavisua…` | — | Input image |

### `danielgatis/rembg`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `image_url` | file | yes | — | — | Image whose background should be removed (.jpg/.png/.webp) |
| `crop_to_bbox` | boolean | no | `False` | — | If set to true, the resulting image be cropped to a bounding box around the subject |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from birefnet_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About BiRefNet

BiRefNet is introduced in *Bilateral Reference for High-Resolution Dichotomous Image Segmentation* by Zheng Peng and colleagues (2024). Its target task, dichotomous image segmentation (DIS), is to produce one high-resolution foreground mask of the salient object with a level of edge precision that ordinary saliency and matting models miss.

The network has two parts: a localisation module that finds the object at low resolution, and a reconstruction module that recovers detail. The reconstruction module is fed *bilateral references*: inward references (patches of the source image at their original resolution) and outward references (gradient maps) that push the decoder to keep fine structure rather than smoothing it away. The Swin backbone is trained on DIS5K, and the project publishes variants for HRSOD, camouflaged-object detection, portrait matting and a 2048×2048 high-resolution checkpoint.

The output is a single-channel alpha mask at the input resolution; composite it over the source to get a transparent PNG. Practical limits: the model is biased towards one dominant subject per image, VRAM scales with resolution, and per-image latency on consumer GPUs is measured in seconds rather than milliseconds.

The hosted endpoint used by this client is `bria/rmbg-2.0`, which provides the same background-removal capability; Bria's model card describes RMBG 2.0 as built on the BiRefNet architecture and trained on Bria's own licensed dataset. The original BiRefNet weights are not served here; they are available at https://github.com/ZhengPeng7/BiRefNet if you want to self-host. `danielgatis/rembg` and `supavisual/remove-background` are also exposed as lighter, cheaper options.

**Official project:** https://github.com/ZhengPeng7/BiRefNet

## Use cases

- **E-commerce product cutouts** — call `run({"image_url": ...})` on each catalogue photo and store the returned PNG on a white or transparent background.
- **Profile and avatar processing** — strip the background from user uploads before cropping to a circle or placing on a brand colour.
- **Marketing composites** — isolate a subject, then feed the cutout into an image-editing or generation model as a layer.
- **Bulk archive cleanup** — submit thousands of images with `wait=False`, let a webhook collect the results, and skip the GPU queue entirely.
- **Dataset preparation** — produce masks for training or evaluating your own segmentation models at $0.01–$0.018 per image.
- **Print-on-demand pipelines** — generate clean transparent artwork automatically when a customer uploads a design.

## FAQ

**Is there a BiRefNet API?**

Not from the original authors. BiRefNet is published as open-source weights. This client exposes the same capability through a hosted endpoint (`bria/rmbg-2.0` by default), so you can call background removal over HTTPS instead of running the model yourself.

**How much does the BiRefNet API cost?**

The default `bria/rmbg-2.0` model is $0.018 per run. `danielgatis/rembg` and `supavisual/remove-background` are $0.01 per run. You are billed per prediction; there is no hourly GPU charge.

**Can I run BiRefNet without a GPU?**

With this client, yes: inference happens on the hosted service, and your code only makes HTTP requests. Self-hosting BiRefNet at full resolution needs a CUDA GPU with a large amount of memory.

**Does this client work with the original BiRefNet repo or ComfyUI?**

No. It does not load the ZhengPeng7/BiRefNet checkpoints or plug into ComfyUI nodes. It is a network client for the hosted endpoint. If you want the exact original weights, run the official repository locally.

**What input formats does it accept?**

A publicly reachable image URL (`image_url`) in .jpg, .png or .webp. The `supavisual/remove-background` model uses the field name `input_image`. The output is a URL to a PNG with a transparent background.

**Is this the official BiRefNet SDK?**

No. This is an independent, community-maintained client and is not affiliated with the BiRefNet authors. The official project lives at https://github.com/ZhengPeng7/BiRefNet.

## Related

- [BiRefNet (official repository)](https://github.com/ZhengPeng7/BiRefNet) — paper, weights and training code.
- [Synexa Python client](https://github.com/synexa-ai/synexa-python) — the general-purpose client this package wraps.
- [bria/rmbg-2.0](https://synexa.ai/explore/bria/rmbg-2.0) — the default hosted background-removal model.
- [danielgatis/rembg](https://synexa.ai/explore/danielgatis/rembg) — fast, no-frills background remover with optional crop-to-bbox.
- [supavisual/remove-background](https://synexa.ai/explore/supavisual/remove-background) — lightweight cutout endpoint at $0.01 per run.

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of BiRefNet. Model weights and trademarks belong to their respective owners.
