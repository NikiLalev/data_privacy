from server import Server
from client import Client
from utils import load_data_from_json
import numpy as np
import time
import json
import os

def main():
    all_results = []
    # Load data from JSON file
    documents, questions = load_data_from_json('ass2/dataset/squad.json')
    document_ids = list(documents.keys())
    document_texts = list(documents.values())
    question_ids = list(questions.keys())
    question_texts = list(questions.values())
    # # Create server and client
    client = Client()
    
    dimensions = [64, 128, 256, 768]
    for dim in dimensions:
        recall_at_1 = 0
        recall_at_5 = 0
        recall_at_10 = 0
        latencies = []
        print(f"Dimension: {dim}")
        # Encode documents and questions with the specified dimension
        embeddings_file_path = f'ass2/dataset/document_embeddings_dim_{dim}.npy'
        if os.path.exists(embeddings_file_path):
            document_embeddings = np.load(embeddings_file_path)
            print(f"Loaded precomputed document embeddings from {embeddings_file_path}.")
        else:
            document_embeddings = client.encode(list(documents.values()), dim=dim, q_prefix=False)
            np.save(embeddings_file_path, document_embeddings)
            print(f"Saved document embeddings to {embeddings_file_path}.")
        server = Server(doc_ids = document_ids, embeddings=document_embeddings)
        # for each question search for the top 10 most similar documents
        for question_id, question_text in questions.items():
            start_time = time.time()

            # get the query vector for the question
            query_vector = client.encode([question_text], dim=dim, q_prefix=True)[0]
            # perform search and time it
            results = server.search(query_vector, k=10)
            end_time = time.time()
            latency = end_time - start_time
            latencies.append(latency)
            
            result_ids = [doc_id for doc_id, _ in results]
            # compute recall
            if question_id in result_ids[:1]: 
                recall_at_1 += 1
            if question_id in result_ids[:5]: 
                recall_at_5 += 1
            if question_id in result_ids[:10]: 
                recall_at_10 += 1
            
        # compute average recall and latency. Recall formula: Recall@k = (Number of queries with target in top-k) / (Total queries), source: https://medium.com/@rajnish_khatri/retrieval-metrics-tutorial-recall-k-and-mrr-explained-d2f12afb9c89
        n_questions = len(questions)
        avg_recall_at_1 = recall_at_1 / n_questions
        avg_recall_at_5 = recall_at_5 / n_questions
        avg_recall_at_10 = recall_at_10 / n_questions
        avg_latency = sum(latencies) / n_questions

        print(f"Average Recall at 1: {avg_recall_at_1}")
        print(f"Average Recall at 5: {avg_recall_at_5}")
        print(f"Average Recall at 10: {avg_recall_at_10}")
        print(f"Average Latency: {avg_latency}")
        
        metrics = {
            "dimension": dim,
            "recall_at_1": avg_recall_at_1,
            "recall_at_5": avg_recall_at_5,
            "recall_at_10": avg_recall_at_10,
            "latency": avg_latency
        }
        all_results.append(metrics)
        
    with open('ass2/dataset/results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
if __name__ == "__main__":
    main()