from server import Server
from client import Client
from utils import load_data_from_json, save_encrypted_setup, load_encrypted_setup
import numpy as np
import time
import json
import os

def run_part_1():
    print("Running PART 1")
    all_results = []
    # Load data from JSON file
    documents, questions = load_data_from_json('ass2/dataset/squad.json')
    document_ids = list(documents.keys())
    document_texts = list(documents.values())
    question_ids = list(questions.keys())
    question_texts = list(questions.values())
    # # Create server and client
    client = Client()
    k = 10
    dimensions = [64, 128, 256, 768]
    for dim in dimensions:
        recall_at_1 = 0
        recall_at_5 = 0
        recall_at_10 = 0
        
        # Timing breakdowns
        t_encode_q = []
        t_server_search = []
        t_top_k = []
        t_fetch_docs = []
        query_details = {}
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
            # Note: the server search function computes similarity, top k and fetch
            # I copied it here to measure each component
            # 1. Encode query
            t0 = time.time()
            query_vector = client.encode([question_text], dim=dim, q_prefix=True)[0]
            t_encode_q.append(time.time() - t0)

            # 2. Server search
            t0 = time.time()
            similarities = np.dot(server.embeddings, query_vector.T)
            t_server_search.append(time.time() - t0)

            # 3. Top-k selection
            t0 = time.time()
            top_k_indices = np.argpartition(similarities, -k)[-k:]
            # get the top k similarities
            top_k_similarities = similarities[top_k_indices]
            # sort by similarity in descending order and get indices
            sorted_top_k_indices = top_k_indices[np.argsort(-top_k_similarities)]
            results = [(server.doc_ids[i], similarities[i]) for i in sorted_top_k_indices]
            t_top_k.append(time.time() - t0)

            top_k_ids = [doc_id for doc_id, _ in results]

            # 4. Fetch docs
            t0 = time.time()
            fetched = [documents[doc_id] for doc_id in top_k_ids]
            t_fetch_docs.append(time.time() - t0)
            
            result_ids = [doc_id for doc_id, _ in results]
            # compute recall
            if question_id in result_ids[:1]: 
                recall_at_1 += 1
            if question_id in result_ids[:5]: 
                recall_at_5 += 1
            if question_id in result_ids[:10]: 
                recall_at_10 += 1

            query_details[question_id] = {
                "top_10_ids": top_k_ids,
                "scores": [float(score) for _, score in results]
            } 
            
        # compute average recall and latency. Recall formula: Recall@k = (Number of queries with target in top-k) / (Total queries), source: https://medium.com/@rajnish_khatri/retrieval-metrics-tutorial-recall-k-and-mrr-explained-d2f12afb9c89
        n_questions = len(questions)
        avg_recall_at_1 = recall_at_1 / n_questions
        avg_recall_at_5 = recall_at_5 / n_questions
        avg_recall_at_10 = recall_at_10 / n_questions

        print(f"Average Recall at 1: {avg_recall_at_1}")
        print(f"Average Recall at 5: {avg_recall_at_5}")
        print(f"Average Recall at 10: {avg_recall_at_10}")
        

        metrics = {
            "dimension": dim,
            "recall_at_1": avg_recall_at_1,
            "recall_at_5": avg_recall_at_5,
            "recall_at_10": avg_recall_at_10,
            "avg_times_ms": {
                "encode_q": np.mean(t_encode_q) * 1000,
                "encrypt_q": 0.0,
                "server_similarity": np.mean(t_server_search) * 1000,
                "decrypt_scores": 0.0,
                "top_k_selection": np.mean(t_top_k) * 1000,
                "fetch_and_decrypt_docs": np.mean(t_fetch_docs) * 1000
            },
            "queries": query_details
        }
        all_results.append(metrics)
        
    with open('ass2/dataset/results_part1.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    print("Savedd results")

def run_part_2():
    print("Running part 2")
    documents, questions = load_data_from_json('ass2/dataset/squad.json')
    client = Client()
    document_ids = list(documents.keys())
    all_results = []
    n_questions = len(questions)
    dim = 256 # default
    cnt = 0
    
    # Step 1: Encode documents and questions with the specified dimension
    embeddings_file_path = f'ass2/dataset/document_embeddings_dim_{dim}.npy'
    if os.path.exists(embeddings_file_path):
        document_embeddings = np.load(embeddings_file_path)
        print(f"Loaded precomputed document embeddings from {embeddings_file_path}.")
    else:
        document_embeddings = client.encode(list(documents.values()), dim=dim, q_prefix=False)
        np.save(embeddings_file_path, document_embeddings)
        print(f"Saved document embeddings to {embeddings_file_path}.")

    # Setup 
    enc_embeddings, enc_documents = load_encrypted_setup(client)
    if enc_embeddings is None:
        # Step 2: encrypt embeddigns
        t0 = time.time()
        enc_embeddings = client.ckks_encrypt_embeddings(document_embeddings)

        # Step 3: encrypt documents with AES-GCM
        enc_documents = client.encrypt_documents(documents)

        setup_time_sec = time.time() - t0
        print(f"One-time Setup Time: {setup_time_sec:.2f} seconds.")

        save_encrypted_setup(client, enc_embeddings, enc_documents)
    
    ckks_bytes = sum(len(v.serialize()) for v in enc_embeddings)
    aes_bytes = sum(len(nonce) + len(ct) for nonce, ct in enc_documents.values())
    storage_mb = (ckks_bytes + aes_bytes) / (1024 * 1024)
    print(f"Server Storage: {storage_mb:.2f} MB (CKKS: {ckks_bytes/(1024*1024):.2f} MB, AES: {aes_bytes/(1024*1024):.2f} MB)")
    server = Server(
        doc_ids = document_ids, 
        embeddings=document_embeddings,
        ckks_embeddings=enc_embeddings,
        encrypted_documents=enc_documents
    )
    recall_at_1 = 0
    recall_at_5 = 0
    recall_at_10 = 0
    t_encode_q = []
    t_encrypt_q = []
    t_server_search = []
    t_decrypt_scores = []
    t_top_k = []
    t_fetch_decrypt = []
    query_details = {}
    k = 10
    
    # Debug print
    print(f"Evaluating {n_questions} questions.")
    # for each question search for the top 10 most similar documents
    for question_id, question_text in questions.items():
        cnt += 1
        print(f"Question {cnt}")
        t0 = time.time()
        # 1 get the query vector for the question
        query_vector = client.encode([question_text], dim=dim, q_prefix=True)[0]
        t_encode_q.append(time.time() - t0)

        # 2 encrypt
        t0 = time.time()
        enc_query = client.ckks_encrypt_embeddings(np.array([query_vector]))[0]
        t_encrypt_q.append(time.time() - t0)

        # 3 perform search and get encrypted scores
        t0 = time.time()
        enc_scores = server.search_ckks(enc_query)
        t_server_search.append(time.time() - t0)
        
        # 4 decrypt
        t0 = time.time()
        dec_scores = np.array(client.ckks_decrypt_scores(enc_scores))
        t_decrypt_scores.append(time.time() - t0)
        
        # 5 top k selection
        t0 = time.time()
        top_k_indices = np.argpartition(dec_scores, -k)[-k:]
        # get top k ids
        top_k_similarities = dec_scores[top_k_indices]
        sorted_top_k_indices = top_k_indices[np.argsort(-top_k_similarities)]
        results = [(server.doc_ids[idx], dec_scores[idx]) for idx in sorted_top_k_indices]
        t_top_k.append(time.time() - t0)

        top_k_ids = [doc_id for doc_id, _ in results]

        # 6 request the encrypted documents from the server
        t0 = time.time()
        enc_docs = server.get_document_by_id(top_k_ids)
        dec_docs = client.decrypt_documents(enc_docs)
        t_fetch_decrypt.append(time.time() - t0)
        
        # compute recall
        if question_id in top_k_ids[:1]: 
            recall_at_1 += 1
        if question_id in top_k_ids[:5]: 
            recall_at_5 += 1
        if question_id in top_k_ids[:10]: 
            recall_at_10 += 1

        query_details[question_id] = {
            "top_10_ids": top_k_ids,
            "top_10_scores": [float(score) for _, score in results]
        }
        
    # compute average recall and latency. Recall formula: Recall@k = (Number of queries with target in top-k) / (Total queries), source: https://medium.com/@rajnish_khatri/retrieval-metrics-tutorial-recall-k-and-mrr-explained-d2f12afb9c89
    avg_recall_at_1 = recall_at_1 / n_questions
    avg_recall_at_5 = recall_at_5 / n_questions
    avg_recall_at_10 = recall_at_10 / n_questions

    print(f"Average Recall at 1: {avg_recall_at_1}")
    print(f"Average Recall at 5: {avg_recall_at_5}")
    print(f"Average Recall at 10: {avg_recall_at_10}")
    
    metrics = {
        "dimension": dim,
        "recall_at_1": avg_recall_at_1,
        "recall_at_5": avg_recall_at_5,
        "recall_at_10": avg_recall_at_10,
        "server_storage_mb": storage_mb,
        "avg_times_ms": {
            "encode_q": np.mean(t_encode_q) * 1000,
            "encrypt_q": np.mean(t_encrypt_q) * 1000,
            "server_similarity": np.mean(t_server_search) * 1000,
            "decrypt_scores": np.mean(t_decrypt_scores) * 1000,
            "top_k_selection": np.mean(t_top_k) * 1000,
            "fetch_and_decrypt_docs": np.mean(t_fetch_decrypt) * 1000
        },
        "queries": query_details
    }
    all_results.append(metrics)
    with open('ass2/dataset/results_part2.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)

def main():
    choice = input("Enter 1 for part 1 or 2 for part 2: ")
    if choice == '1':
        run_part_1()
    elif choice == '2':
        run_part_2()
    else:
        print("Please enter 1 or 2.")
if __name__ == "__main__":
    main()