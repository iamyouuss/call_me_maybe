from llm_sdk import llm_sdk
import json
from src import (config_files, load_functions, load_prompts,
                 tokens_with_allowed_chars, pick_best_valid_token)


def open_voc(voc):
    with open(voc) as f:
        vocab = json.load(f)
    return {v: k for k, v in vocab.items()}


def get_function_names(functions):
    return [f["name"] for f in functions]


def main() -> None:
    files = config_files()
    functions = load_functions(files["functions"])
    prompts = load_prompts(files["prompts"])
    llm = llm_sdk.Small_LLM_Model()
    voc = llm.get_path_to_vocab_file()

    id_to_token = open_voc(voc)
    names = get_function_names(functions)

    for p in prompts:
        prompt = f'{{\n  "prompt": "{p.prompt}",\n  '
        ids_list = llm.encode(prompt)[0].tolist()
        logits = llm.get_logits_from_input_ids(ids_list)
        valid_ids = tokens_with_allowed_chars(id_to_token, '"name"')
        best_id = pick_best_valid_token(logits, valid_ids)
        ids_list.append(best_id)

        logits = llm.get_logits_from_input_ids(ids_list)
        valid_ids = tokens_with_allowed_chars(id_to_token, ':"')
        best_id = pick_best_valid_token(logits, valid_ids)
        ids_list.append(best_id)

        for _ in range(15):
            logits = llm.get_logits_from_input_ids(ids_list)
            best_id = pick_best_valid_token(logits, list(id_to_token.keys()))
            ids_list.append(best_id)
        print(llm.decode(ids_list))


main()
