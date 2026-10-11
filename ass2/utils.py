from datasets import load_dataset
import json
import os
import tenseal as ts
import pickle

CACHE_DIR = 'ass2/dataset/cache_part2'

def load_data(num_documents=1000, num_questions=200, save_path=None):
    """
    Load a subset of the SQuAD dataset.
    """
    # some prints for debugging
    print("Loading SQuAD dataset...")
    ds = load_dataset("rajpurkar/squad", split="validation")
    
    print(f"Number of documents in SQuAD validation set: {len(ds)}")
    
    # collect 1000 documents with unique context and 200 questions.
    seen = set()
    documents = {}
    questions = {}
    cnt_docs = 0
    cnt_questions = 0
    # TO DO: ask TAs if they require random sampling
    for document in ds:
        if cnt_docs < num_documents and document['context'] not in seen:
            seen.add(document['context'])
            documents[document['id']] = document['context']
            cnt_docs += 1
            if cnt_questions < num_questions:
                questions[document['id']] = document['question']
                cnt_questions += 1
    if save_path:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump({'documents': documents, 'questions': questions}, f)
    return documents, questions

def load_data_from_json(json_path):
    """
    Load documents and questions from a JSON file.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['documents'], data['questions']

def save_encrypted_setup(client, enc_doc_embeddings, enc_documents):                                                                              
    """                                                                                                                                           
    Save the client's keys, context, encrypted vectors etc. Note we use this just for running the experiments a bit quicker.                                                       
    """                                                                                                                                           
    os.makedirs(CACHE_DIR, exist_ok=True)                                                                                                         
    with open(f'{CACHE_DIR}/aes_key.bin', 'wb') as f:                                                                                             
        f.write(client.key)                                                                                                                       
    with open(f'{CACHE_DIR}/ts_context.bin', 'wb') as f:                                                                                          
        f.write(client.context.serialize(save_secret_key=True))                                                                                   
    with open(f'{CACHE_DIR}/enc_embeddings.pkl', 'wb') as f:                                                                                      
        pickle.dump([v.serialize() for v in enc_doc_embeddings], f)                                                                               
    with open(f'{CACHE_DIR}/enc_documents.pkl', 'wb') as f:                                                                                       
        pickle.dump(enc_documents, f)                                                                                                             
    print("Saved encrypted setup to disk cache.")                                                                                                 
                                                                                                                                                    
def load_encrypted_setup(client):                                                                                                                 
    """                                                                                                                                           
    Load cached encrypted setup. Note we use this just for running the experiments a bit quicker.                                                                                               
    """                                                                                                                                           
    req_files = ['aes_key.bin', 'ts_context.bin', 'enc_embeddings.pkl', 'enc_documents.pkl']                                                      
    if not all(os.path.exists(f'{CACHE_DIR}/{f}') for f in req_files):                                                                            
        return None, None                                                                                                                         
                                                                                                                                                    
    print("Loading cached encrypted setup from disk...")                                                                                          
    with open(f'{CACHE_DIR}/aes_key.bin', 'rb') as f:                                                                                             
        client.key = f.read()                                                                                                                     
    with open(f'{CACHE_DIR}/ts_context.bin', 'rb') as f:                                                                                          
        client.context = ts.context_from(f.read())                                                                                                
    with open(f'{CACHE_DIR}/enc_documents.pkl', 'rb') as f:                                                                                       
        enc_documents = pickle.load(f)                                                                                                            
    with open(f'{CACHE_DIR}/enc_embeddings.pkl', 'rb') as f:                                                                                      
        serialized_ckks = pickle.load(f)                                                                                                          
    enc_doc_embeddings = [ts.ckks_vector_from(client.context, b) for b in serialized_ckks]                                                        
    return enc_doc_embeddings, enc_documents 

def main():
    # documents, questions = load_data()
    # print(f"Number of documents: {len(documents)}")
    # print(f"Number of questions: {len(questions)}")

    # load data from JSON file
    documents_from_json, questions_from_json = load_data_from_json('ass2/dataset/squad.json')
    print(f"Number of documents from JSON: {len(documents_from_json)}")
    print(f"Number of questions from JSON: {len(questions_from_json)}")

if __name__ == "__main__":
    main()