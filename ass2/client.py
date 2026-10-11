import torch
from torch.nn.functional import normalize
from transformers import AutoModel, AutoTokenizer
import numpy as np
import tenseal as ts
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

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
        # set up encryption key and CKKS context. Based on : https://github.com/OpenMined/TenSEAL
        self.key = AESGCM.generate_key(bit_length=256)
        self.context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
          )
        self.context.generate_galois_keys()
        self.context.global_scale = 2**40

    def encode(self, texts, dim=256, q_prefix=False):
        """
        Encode texts into a fixed-size embedding.
        """
        
        # prepend query prefix to the text if question
        if q_prefix:
            texts = [f"{self.query_prefix}{text}" for text in texts]
        
        all_embeddings = []
        # use batches because I was running out of memory
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            tokens = self.tokenizer(batch, padding=True, truncation=True, return_tensors='pt', max_length=512)
            with torch.inference_mode():
                embeddings = self.model(**tokens)[0][:, 0]
            # truncate embeddings to the specified dimension
            embeddings = embeddings[:, :dim]
            # normalize
            embeddings = normalize(embeddings)
            all_embeddings.append(embeddings)
        
        return torch.cat(all_embeddings, dim=0).numpy()
    
    def encrypt_documents(self, documents: dict):
        """
        Encrypt documents using AES-GCM.
        """
        # code is from :https://cryptography.io/en/latest/hazmat/primitives/aead/
        encrypted_documents = {}
        for doc_id, doc_text in documents.items():
            aesgcm = AESGCM(self.key)
            nonce = os.urandom(12)
            ct = aesgcm.encrypt(nonce, doc_text.encode(), None)
            encrypted_documents[doc_id] = (nonce, ct)
        return encrypted_documents
    
    def decrypt_documents(self, encrypted_documents: dict):
        """
        Decrypt documents using AES-GCM.
        """
        decrypted_documents = {}
        for doc_id, (nonce, ct) in encrypted_documents.items():
            aesgcm = AESGCM(self.key)
            pt = aesgcm.decrypt(nonce, ct, None)
            decrypted_documents[doc_id] = pt.decode()
        return decrypted_documents
    
    def ckks_encrypt_embeddings(self, embeddings: np.ndarray):
        """
        Encrypt embeddings using CKKS.
        """
        encrypted_embeddings = []
        for embedding in embeddings:
            enc_embedding = ts.ckks_vector(self.context, embedding)
            encrypted_embeddings.append(enc_embedding)
        return encrypted_embeddings
    
    def ckks_decrypt_scores(self, encrypted_scores: list):
        """
        Decrypt scores using CKKS.
        """
        decrypted_scores = []
        for enc_score in encrypted_scores:
            score = enc_score.decrypt()
            decrypted_scores.append(score[0])
        return decrypted_scores