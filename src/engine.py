import json
import os
from typing import Any
from llm_sdk.llm_sdk import Small_LLM_Model
from .parsing_files import FunctionModel, PromptModel


class Engine():
    def __init__(self, config: dict[str, Any]) -> None:
        self.llm = Small_LLM_Model(model_name=config['model'])
        self.functions: list[FunctionModel] = config['functions']
        self.function_names: list[str] = [f.name for f in self.functions]
        self.current_function: FunctionModel | None = None
        self.current_ids_list: list[int] = []
        self.prompts: list[PromptModel] = config['prompts']
        self.output_file: str = config['output']
        self.final_result: list[dict[str, Any]] = []
        self.id_to_token: dict[int, str] = {}

        voc = self.llm.get_path_to_vocab_file()
        with open(voc) as f:
            self.token_to_id = json.load(f)
        self.id_to_token = {v: k for k, v in self.token_to_id.items()}

    def pick_best_token(self, logits: list[float], valid_ids: list[int]
                        ) -> int:
        max_logit = float('-inf')
        best_id = None
        for token_id in valid_ids:
            logit = logits[token_id]
            if logit > max_logit:
                max_logit = logit
                best_id = token_id
        if best_id is None:
            raise ValueError("\033[0;31m[Error]\033[0m "
                             "Cannot find token for logits")
        return best_id

    def encode_sequence(self, sequence: str) -> None:
        try:
            ids = self.llm.encode(sequence)[0].tolist()
            self.current_ids_list.extend(ids)
        except ValueError as e:
            print("\033[0;31m[Error]\033[0m failed to encode sequence "
                  f"'{sequence}': {e}")

    def decode_token(self, token_id: int) -> str:
        """Décode un ID en texte propre en gérant les caractères BPE."""
        token_str = self.id_to_token[token_id]
        return token_str.replace("Ġ", " ").replace("Ċ", "\n")

    def assign_current_function(self, name: str, prompt: str) -> None:
        for f in self.functions:
            if f.name == name:
                self.current_function = f
        if self.current_function is None:
            raise RuntimeError("\033[0;31m[Error]\033[0m No function found "
                               f"for the following prompt '{prompt}'")

    def pick_function_model(self, prompt: str,) -> str:
        f_prompt = "Available functions:\n"
        for f in self.functions:
            f_prompt += f"- {f.name}: {f.description}\n"
        f_prompt += f'User request: {prompt}\n{{"name": "'
        prompt_ids_list = self.llm.encode(f_prompt)[0].tolist()
        self.current_ids_list = prompt_ids_list.copy()
        generated = ""
        while generated not in self.function_names:
            valid_ids = []
            logits = self.llm.get_logits_from_input_ids(prompt_ids_list)
            for id, token in self.id_to_token.items():
                test = generated + token
                for f_name in self.function_names:
                    if not token:
                        continue
                    if f_name.startswith(test):
                        valid_ids.append(id)
                        break
            if not valid_ids:
                raise ValueError(
                    "\033[0;31m[Error]\033[0m cannot find token for "
                    f"'{generated}'")

            best_id = self.pick_best_token(logits, valid_ids)
            token_str = self.decode_token(best_id)
            print(f"\033[33m{token_str}\033[0m", end="", flush=True)
            generated += token_str
            prompt_ids_list.append(best_id)
            self.current_ids_list.append(best_id)
        print()

        self.assign_current_function(generated, prompt)
        return generated

    def tokens_with_allowed_chars(self, allowed_chars: str) -> list[int]:
        result = []
        for token_id, token in self.id_to_token.items():
            if token and all(c in allowed_chars for c in token):
                result.append(token_id)
        return result

    def generate_boolean(self) -> bool:
        result = ""
        for _ in range(50):
            allowed = "truefalse"
            valid_ids = self.tokens_with_allowed_chars(allowed)
            logits = self.llm.get_logits_from_input_ids(self.current_ids_list)
            best_id = self.pick_best_token(logits, valid_ids)
            char = self.decode_token(best_id)
            print(f"\033[33m{char}\033[0m", end="", flush=True)
            result += char
            self.current_ids_list.append(best_id)
            if result in ["true", "false"]:
                break
        return result == "true"

    def generate_number(self) -> float:
        result = ""
        for _ in range(50):
            allowed = "-0123456789-.,} Ġ\n"
            valid_ids = self.tokens_with_allowed_chars(allowed)
            logits = self.llm.get_logits_from_input_ids(self.current_ids_list)
            best_id = self.pick_best_token(logits, valid_ids)
            char = self.decode_token(best_id)
            print(f"\033[33m{char}\033[0m", end="", flush=True)
            if any(stop_char in char
                   for stop_char in [',', '}', ' ', 'Ġ', '\n']):
                break
            self.current_ids_list.append(best_id)
            result += char
        try:
            return float(result)
        except ValueError:
            return 0.0

    def generate_string(self) -> str:
        result = ""
        for _ in range(50):
            logits = self.llm.get_logits_from_input_ids(self.current_ids_list)
            best_id = self.pick_best_token(logits,
                                           list(self.id_to_token.keys()))
            char = self.decode_token(best_id)
            if '"' in char:
                result += char.split('"')[0]
                break
            print(f"\033[33m{char}\033[0m",
                  end="", flush=True)
            self.current_ids_list.append(best_id)
            result += char
        return result

    def generate_parameters(self) -> dict[str, Any]:
        self.encode_sequence('", "parameters": {')
        if self.current_function is None:
            raise RuntimeError(
                "\033[0;31m[Error]\033[0m current_function is not set.")
        parameters = self.current_function.parameters
        result: dict[str, Any] = {}
        for i, (p_name, p_details) in enumerate(parameters.items()):
            if i > 0:
                self.encode_sequence(', ')
            self.encode_sequence(f'"{p_name}": ')
            p_type = p_details.type
            if p_type in ["boolean", "bool"]:
                result[p_name] = self.generate_boolean()
            elif p_type in ["number", "integer", "float", "double"]:
                result[p_name] = self.generate_number()
            else:
                self.encode_sequence('"')
                result[p_name] = self.generate_string()
                self.encode_sequence('"')
            print()
        self.encode_sequence('}')
        return result

    def write_to_output_file(self) -> None:
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, "w") as f:
            json.dump(self.final_result, f, indent="\t")

    def get_started(self) -> None:
        try:
            print(f"\n\033[1;35mStarting Generation for Call_Me_Maybe project "
                  f"({len(self.prompts)} prompts given)\033[0m\n")
            for i, prompt in enumerate(self.prompts, 1):
                self.current_ids_list = []
                try:
                    result = {
                        "prompt": prompt.prompt,
                        "name": self.pick_function_model(prompt.prompt),
                        "parameters": self.generate_parameters()
                    }
                    self.final_result.append(result)
                    output = json.dumps(result, indent=2)
                    print(f"\033[1;36mOutput number {i}:\033[0m\n{output}\n")
                except Exception as e:
                    print(f"[Skipped] Unrecoverable error on prompt {i}: {e}")
                    continue
            self.write_to_output_file()
            print("\033[1;35mGeneration completed successfully!\033[0m")
            print(f"Json output stored in '\033[1;32m{self.output_file}'")
        except Exception as e:
            print(f"\033[0;31m[Error]\033[0m Couldn't generate output: {e}")
