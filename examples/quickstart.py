        """Minimal BiRefNet example: create one prediction and print the output URL(s)."""
        import birefnet_api

        output = birefnet_api.run({
    "image_url": "https://example.com/input.png"
})
        print(output)
