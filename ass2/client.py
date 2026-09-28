import torch
from torch.nn.functional import normalize
from transformers import AutoModel, AutoTokenizer

class Client:
    def __init__(self, model="Snowflake/snowflake-arctic-embed-m-v1.5"):
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModel.from_pretrained(model, add_pooling_layer=False)
        self.model.eval()
        # assignment says everything should run on CPU
        self.device = torch.device("cpu")
        self.model.to(self.device)
        # from the model card
        self.query_prefix = 'Represent this sentence for searching relevant passages: '

    def encode(self, texts, dim=256, q_prefix=False):
        """
        Encode texts into a fixed-size embedding.
        """
        
        # prepend query prefix to the text if question
        if q_prefix:
            texts = [f"{self.query_prefix}{text}" for text in texts]
        
        tokens = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt', max_length=512)
        with torch.inference_mode():
            embeddings = self.model(**tokens)[0][:, 0]
        # truncate embeddings to the specified dimension
        embeddings = embeddings[:, :dim]
        # normalize
        embeddings = normalize(embeddings)
        return embeddings
            