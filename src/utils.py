def tokens_with_allowed_chars(id_to_token, allowed_chars) -> list:
    result = []
    for token_id, token in id_to_token.items():
        if token and all(c in allowed_chars for c in token):
            result.append(token_id)
    return result


def tokens_without_forbidden_chars(id_to_token, forbidden_chars) -> list:
    result = []
    for token_id, token in id_to_token.items():
        if token and not all(c in forbidden_chars for c in token):
            result.append(token_id)
    return result











def generate_value(llm, id_to_token, vocab, ids_list, param_type) -> list:
    char = ""
    if param_type == "number":
        has_dot = False
        has_digit = False
        while not (has_digit and ("," in char or "}" in char)):
            allowed = "0123456789}," if has_dot else "0123456789},."
            if not has_digit:
                allowed = "0123456789-"
            logits = llm.get_logits_from_input_ids(ids_list)
            valid_ids = tokens_with_allowed_chars(id_to_token, allowed)
            best_id = pick_best_valid_token(logits, valid_ids)
            char = id_to_token[best_id]
            if char == ".":
                has_dot = True
            if char.isdigit():
                has_digit = True
            # if char not in (",", "}"):
            ids_list.append(best_id)
    elif param_type == "string":
        while '"' not in char:
            logits = llm.get_logits_from_input_ids(ids_list)
            # valid_ids = tokens_without_forbidden_chars(id_to_token, '"')
            # valid_ids.append(vocab['"'])
            best_id = pick_best_valid_token(logits, list(id_to_token.keys()))
            char = id_to_token[best_id]
            ids_list.append(best_id)
    return ids_list


def get_function_name(generated_text: str) -> str:
    """ Implementation for extracting function name from generated text """
    m = '"name": "'
    if m not in generated_text:
        return None
    parts = generated_text.split(m)
    next_part = parts[1]
    if '"' in next_part:
        fn = next_part.split('"')[0]
        return fn
    return None
