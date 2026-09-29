from datasets import load_dataset
import json

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