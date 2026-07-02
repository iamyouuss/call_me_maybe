import sys
from typing import Any

from pydantic import BaseModel, ValidationError
import json
import argparse


class PromptModel(BaseModel):
    prompt: str


class ParameterModel(BaseModel):
    type: str


class FunctionModel(BaseModel):
    name: str
    description: str
    parameters: dict[str, ParameterModel]
    returns: ParameterModel


def load_functions(path: str) -> list[FunctionModel]:
    try:
        with open(path) as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"\033[0;31m[Error]\033[0m File '{path}' not found or invalid "
              f"JSON: {e}")
        sys.exit(1)
    try:
        functions = [FunctionModel(**func_data) for func_data in json_data]
    except ValidationError as e:
        print(f"\033[0;31m[Error]\033[0m Parsing functions from '{path}' "
              f"went wrong: {e}")
        sys.exit(1)
    if not functions:
        print(f"\033[0;31m[Error]\033[0m No valid functions found in '{path}'")
        sys.exit(1)
    return functions


def load_prompts(path: str) -> list[PromptModel]:
    try:
        with open(path) as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"\033[0;31m[Error]\033[0mFile '{path}' "
              f"not found or invalid JSON: {e}")
        sys.exit(1)
    try:
        prompts = [PromptModel(**prompt_data) for prompt_data in json_data]
    except ValidationError as e:
        print(f"\033[0;31m[Error]\033[0m Parsing prompts from '{path}' "
              f"went wrong: {e}")
        sys.exit(1)
    return prompts


def config() -> dict[str, Any]:
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--functions_definition", type=str,
                            default="data/input/functions_definition.json")
        parser.add_argument("--input", type=str,
                            default="data/input/function_calling_tests.json")
        parser.add_argument("--output", type=str,
                            default="data/output/function_calling_results.json"
                            )
        parser.add_argument("--model", type=str, default="Qwen/Qwen3-0.6B")
        args = parser.parse_args()
        return {
            "functions": load_functions(args.functions_definition),
            "prompts": load_prompts(args.input),
            "output": args.output,
            "model": args.model
        }
    except Exception as e:
        print("\033[0;31m[Error]\033[0m Something went wrong "
              f"while parsing files: {e}")
        sys.exit(1)
