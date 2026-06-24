import json
from typing import Any
from llm_sdk.llm_sdk import Small_LLM_Model
from src import FunctionModel


class Engine():
    def __init__(self, config: dict[str, Any]) -> None:
        self.llm = Small_LLM_Model()
        self.functions: list[FunctionModel] = config['functions']
        self.function_names: list[str] = [f.name for f in self.functions]
        self.current_function: FunctionModel | None = None
        self.prompts: list[str] = config['prompts']
        self.output_file: str = config['output']
        self.result: list[dict[str, Any]] = []
        self.id_to_token: dict[int, str] = {}

        voc = self.llm.get_path_to_vocab_file()
        with open(voc) as f:
            self.token_to_id = json.load(f)
        self.id_to_token = {v: k for k, v in self.token_to_id.items()}

    def pick_best_token(self, logits, valid_ids) -> int:
        max_logit = float('-inf')
        best_id = None
        for token_id in valid_ids:
            logit = logits[token_id]
            if logit > max_logit:
                max_logit = logit
                best_id = token_id
        return best_id

    def generate_sequence(self, ids_list: list[int], sequence: str
                          ) -> list[int]:
        while len(sequence) > 0:
            valid_ids = []
            logits = self.llm.get_logits_from_input_ids(ids_list)
            for id, token in self.id_to_token.items():
                if not token:
                    continue
                if sequence.startswith(token):
                    valid_ids.append(id)
            if not valid_ids:
                raise ValueError(
                    f"Alert : cannot find token for '{sequence}'")

            best_id = self.pick_best_token(logits, valid_ids)
            token_txt = self.id_to_token[best_id]

            ids_list.append(best_id)
            sequence = sequence[len(token_txt):]
        return ids_list

    def pick_function_model(self, prompt: str, ids_list: list[int]
                            ) -> list[int]:
        f_prompt = "Available functions:\n"
        for f in self.functions:
            f_prompt += f"- {f.name}: {f.description}\n"
        f_prompt += f'User request: {prompt}\n{{"name": "'
        prompt_ids_list = self.llm.encode(f_prompt)[0].tolist()
        generated = ""
        while generated not in self.functions_name:
            valid_ids = []
            logits = self.llm.get_logits_from_input_ids(prompt_ids_list)
            for id, token in self.id_to_token.items():
                test = generated + token
                for f in self.function_names:
                    if not token:
                        continue
                    if f.startswith(test):
                        valid_ids.append(id)
                        break
            if not valid_ids:
                raise ValueError(
                    f"Alert: cannot find token for '{generated}'")

            best_id = self.pick_best_token(logits, valid_ids)
            generated += self.id_to_token[best_id]
            prompt_ids_list.append(best_id)
            ids_list.append(best_id)

        for f in self.functions:
            if f.name == generated:
                self.current_function = f
        return ids_list

    def generate_parameters(self, ids_list: list[int],
                            function_model: FunctionModel) -> list[int]:
        ids_list = self.generate_sequence(ids_list, '", "parameters": {')
        parameters = function_model.parameters

        for i, (p_name, p_detals) in enumerate(parameters.items()):
            if i > 0:
                ids_list = self.generate_sequence(ids_list, ', ')
            ids_list = self.generate_sequence(ids_list, f'"{p_name}": ')
            p_type = p_detals.type

            if p_type == "string":
                ids_list = self.generate_string(ids_list)
            elif p_type in ["number", "integer"]:
                ids_list = self.generate_number(ids_list)
            elif p_type == "boolean":
                ids_list = self.generate_boolean(ids_list)
        ids_list = self.generate_sequence(ids_list, '}')
        return ids_list

    def get_started(self,) -> None:
        for p in self.prompts:
            result = f'{{"prompt": {p},\n'
            ids_list = self.llm.encode(result)
            ids_list = self.pick_function_model(p, ids_list)
            ids_list = self.generate_sequence(ids_list, '"name": "')
            ids_list = self.generate_sequence(ids_list,
                                              f'"{self.current_function.name}"'
                                              )
            ids_list = self.generate_parameters(ids_list,
                                                self.current_function)
            ids_list = self.generate_sequence(ids_list, '}')
            print(self.llm.decode(ids_list))
