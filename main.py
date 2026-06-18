from llm_sdk import llm_sdk
import json
from parsing_json import config_files, load_functions, load_prompts

def get_valid_tokens_ids(id_to_token, allowed_chars):
    result = []
    for token_id, token in id_to_token.items():
        if token and all(c in allowed_chars for c in token):
            result.append(token_id)
    return result

def get_tokens_without_chars(id_to_token, forbidden_chars):
    result = []
    for token_id, token in id_to_token.items():
        if token and all(not c in forbidden_chars for c in token):
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

def generate_value(llm, id_to_token, vocab, ids_list, param_type):
    char = ""
    if param_type == "number":
        has_dot = False
        has_digit = False
        while not (has_digit and ("," in char or "}" in char)):
            allowed = "0123456789}," if has_dot else "0123456789},."
            if not has_digit:
                allowed = "0123456789-"
            logits = llm.get_logits_from_input_ids(ids_list)
            valid_ids = get_valid_tokens_ids(id_to_token, allowed)
            best_id = pick_best_valid_token(logits, valid_ids)
            char = id_to_token[best_id]
            if char == ".":
                has_dot = True
            if char.isdigit():
                 has_digit = True
            if char not in (",", "}"):
                ids_list.append(best_id)
    elif param_type == "string":
        while char != '"':
            logits = llm.get_logits_from_input_ids(ids_list)
            valid_ids = get_tokens_without_chars(id_to_token, '"')
            valid_ids.append(vocab['"'])
            best_id = pick_best_valid_token(logits, valid_ids)
            char = id_to_token[best_id]
            ids_list.append(best_id)
    return ids_list

def main() -> None:
    files = config_files()
    functions = load_functions(files["functions"])
    prompts = load_prompts(files["prompts"])
    llm = llm_sdk.Small_LLM_Model()
    voc = llm.get_path_to_vocab_file()

    with open(voc) as f:
        vocab = json.load(f)
    id_to_token = {v: k for k, v in vocab.items()}
    
    text = '{"name": "fn_greet", "parameters": {"name": "'    
    ids_list = llm.encode(text)[0].tolist()
    print(llm.decode(generate_value(llm, id_to_token, vocab, ids_list, "string")))
    text = '{"name": "fn_add", "parameters": {"a": '
    ids_list = llm.encode(text)[0].tolist()
    print(llm.decode(generate_value(llm, id_to_token, vocab, ids_list, "number")))

main()