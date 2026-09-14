
import sys
import json
from foundry_local_sdk import Configuration, FoundryLocalManager
import config


def main():
    texts = json.loads(sys.stdin.read())

    cfg = Configuration(app_name="local_rag_embed")
    FoundryLocalManager.initialize(cfg)
    manager = FoundryLocalManager.instance

    model = manager.catalog.get_model(config.EMBEDDING_MODEL_ALIAS)
    model.download(lambda p: None)
    model.load()

    client = model.get_embedding_client()
    vectors = []
    for text in texts:
        response = client.generate_embedding(text)
        vectors.append(response.data[0].embedding)

    model.unload()
    print(json.dumps(vectors))


if __name__ == "__main__":
    main()