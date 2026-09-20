"""The same client drives every hosted model listed in birefnet_api.MODELS."""
from birefnet_api import Client, MODELS

client = Client()
for slug, info in MODELS.items():
    print(slug, "->", info["category"], "required:", info["required"])
# pick one explicitly
output = client.run({"input_image": "https://example.com/input.png"}, model="supavisual/remove-background")
print(output)
