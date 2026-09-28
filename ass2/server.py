import numpy as np
from client import encode

class Server:
    def __init__(self, documents):
        self.documents = documents
        self.embeddings = encode(documents, dim=256, q_prefix=False)
        
    def search(self, query_vector, k):
        """
        Search for the top k most similar documents to the query vector.
        """
        # cosine similarity - since vectors are normalized, we just do dot product
        similarities = np.dot(self.embeddings, query_vector.T)
        # top k - idea from https://stackoverflow.com/questions/6910641/how-do-i-get-indices-of-n-maximum-values-in-a-numpy-array/23734295#23734295
        top_k_indices = np.argpartition(similarities, -k)[-k:]
        # get the top k similarities
        top_k_similarities = similarities[top_k_indices]
        # sort by similarity in descending order and get indices
        sorted_top_k_indices = top_k_indices[np.argsort(-top_k_similarities)]
        # return top k documents and their similarities
        return [(self.documents[i], similarities[i]) for i in sorted_top_k_indices]
        