import numpy as np
import tenseal as ts
class Server:
    def __init__(self, doc_ids, embeddings, ckks_embeddings=None, encrypted_documents=None):
        self.doc_ids = doc_ids
        # those will be encrypted for part2
        self.embeddings = embeddings
        self.ckks_embeddings = ckks_embeddings
        self.encrypted_documents = encrypted_documents
        
    def search(self, query_vector, k):
        """
        Search for the top k most similar documents to the query vector. For part 1 of assignment.
        """
        # cosine similarity - since vectors are normalized, we just do dot product
        similarities = np.dot(self.embeddings, query_vector.T)
        # top k - idea from https://stackoverflow.com/questions/6910641/how-do-i-get-indices-of-n-maximum-values-in-a-numpy-array/23734295#23734295
        top_k_indices = np.argpartition(similarities, -k)[-k:]
        # get the top k similarities
        top_k_similarities = similarities[top_k_indices]
        # sort by similarity in descending order and get indices
        sorted_top_k_indices = top_k_indices[np.argsort(-top_k_similarities)]
        # return top k document ids and their similarities
        return [(self.doc_ids[i], similarities[i]) for i in sorted_top_k_indices]
        
    def inv_sqrt_newton(self, x, num_iterations=3, initial_guess=0.5):
        """
        Compute the inverse square root of x using Newton's method.
        """
        yk = initial_guess
        for _ in range(num_iterations):
            yk = 0.5 * yk * (3 - x * (yk * yk))
            
        return yk

    def search_ckks(self, query_vector: ts.CKKSVector):
        """
        Return the encrypted scores for each document given an encrypted query vector. For part 2 of assignment. We only perform dot since we assume that the vectors are normalized.
        """
        encrypted_scores = []
        for vec in self.ckks_embeddings:
            score = vec.dot(query_vector)
            encrypted_scores.append(score)
        return encrypted_scores
    
    def get_document_by_id(self, doc_ids: list):
        """
        Return encrypted documents based on a list of ids. For part 2 of assignment.
        """
        return {doc_id: self.encrypted_documents[doc_id] for doc_id in doc_ids if doc_id in self.encrypted_documents}