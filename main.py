from llm_sdk import llm_sdk
import json
from parsing_json import config_files, load_functions, load_prompts

def get_valid_tokens_ids(id_to_token, allowed_chars):
    result = []
    for token_id, token in id_to_token.items():
        if token and all(c in allowed_chars for c in token):
            result.append(token_id)
    return result

def pick_best_valid_token(logits, valid_ids):
    max_logit = float('-inf')
    best_id = None
    for token_id in valid_ids:
        logit = logits[token_id]
        if logit > max_logit:
            max_logit = logit
            best_id = token_id
    return best_id

def main() -> None:
    files = config_files()
    functions = load_functions(files["functions"])
    prompts = load_prompts(files["prompts"])
    llm = llm_sdk.Small_LLM_Model()
    voc = llm.get_path_to_vocab_file()

    with open(voc) as f:
        vocab = json.load(f)
    """ for token, token_id in list(vocab.items())[:30]:
        print(token, "->", token_id)
 """
    id_to_token = {v: k for k, v in vocab.items()}
    text = "The capital of France is"
    """
     input_ids = llm.encode(text) #list[list]
    ids_list = input_ids[0].tolist() #list[list] -> list
    print(ids_list)
    logits = llm.get_logits_from_input_ids(ids_list)
    print(len(logits))
    best_id = logits.index(max(logits))
    print(best_id, id_to_token.get(best_id))
    
    input_ids = llm.encode(text)
    ids_list = input_ids[0].tolist()

    for _ in range(20):
        logits = llm.get_logits_from_input_ids(ids_list)
        best_id = logits.index(max(logits))
        ids_list.append(best_id)
        print(llm.decode(ids_list))
    valid_ids = get_valid_tokens_ids(id_to_token, "0123456789")
    print(len(valid_ids))
    for tid in valid_ids[:20]:
        print(tid, repr(id_to_token[tid]))
    print(vocab.get("42"))
    print(vocab.get("123"))

    for tid, tok in id_to_token.items():
        if tok == "":
            print(tid)"""
    text = '{"a": '
    ids_list = llm.encode(text)[0].tolist()
    for _ in range(10):
        logits = llm.get_logits_from_input_ids(ids_list)
        valid_ids = get_valid_tokens_ids(id_to_token, "0123456789")
        best_id = pick_best_valid_token(logits, valid_ids)
        ids_list.append(best_id)
        print(llm.decode(ids_list))
        #print(best_id, repr(id_to_token[best_id]))
main()