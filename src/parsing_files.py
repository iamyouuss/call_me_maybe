from pydantic import BaseModel, ValidationError
import json
import argparse


class Prompt(BaseModel):
    prompt: str


class ParameterModel(BaseModel):
    type: str


class FunctionModel(BaseModel):
    name: str
    description: str
    parameters: dict[str, ParameterModel]
    returns: ParameterModel


def load_functions(path: str) -> list[FunctionModel]:
    json_data = None
    try:
        with open(path) as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"File '{path}' not found or invalid JSON:\n{e}\n")
    functions = []
    if json_data is not None:
        try:
            functions = [FunctionModel(**func_data) for func_data in json_data]
        except ValidationError as e:
            print(f"Error parsing functions from '{path}':\n{e}\n")
    return functions


def load_prompts(path: str) -> list[Prompt]:
    json_data = None
    try:
        with open(path) as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"File '{path}' not found or invalid JSON:\n{e}\n")
    prompts = []
    if json_data is not None:
        try:
            prompts = [Prompt(**prompt_data) for prompt_data in json_data]
        except ValidationError as e:
            print(f"Error parsing prompts from '{path}':\n{e}\n")
    return prompts


def config() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--functions_definition", type=str,
                        default="data/input/functions_definition.json")
    parser.add_argument("--input", type=str,
                        default="data/input/function_calling_tests.json")
    parser.add_argument("--output", type=str,
                        default="data/output/function_calls.json")
    args = parser.parse_args()
    return {
        "functions": load_functions(args.functions_definition),
        "prompts": load_prompts(args.input),
        "output": args.output
    }
