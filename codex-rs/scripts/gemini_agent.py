import os
import subprocess
import importlib.util
import textwrap
from typing import Any, Callable, Dict

import requests
from llm_wrapper import LLMBackend

TOOLS_FILE = os.path.join(os.path.dirname(__file__), "user_tools.py")


class ToolManager:
    def __init__(self, tools_file: str = TOOLS_FILE):
        self.tools_file = tools_file
        self.module = None
        self.load_tools()

    def load_tools(self) -> None:
        if not os.path.exists(self.tools_file):
            with open(self.tools_file, "w") as f:
                f.write("# User tools\n")
        spec = importlib.util.spec_from_file_location("user_tools", self.tools_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.module = module

    def save_tool(self, code: str) -> str:
        with open(self.tools_file, "a") as f:
            f.write("\n" + textwrap.dedent(code) + "\n")
        self.load_tools()
        return "Saved tool"

    def run_tool(self, name: str, *args: str) -> str:
        func: Callable[..., Any] | None = getattr(self.module, name, None)
        if not callable(func):
            return f"Tool {name} not found"
        try:
            result = func(*args)
        except Exception as e:  # noqa: BLE001
            return f"Error running {name}: {e}"
        return str(result)


def fetch(url: str) -> str:
    """Fetch text content from a URL."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:  # noqa: BLE001
        return f"Error fetching {url}: {e}"

PROMPT_TEMPLATE = (
    "You are a command runner with the ability to create and run Python tools.\n"
    "To create a tool, reply with:\n"
    "CREATE_TOOL <name>\n<python function code>\n"
    "To run an existing tool, reply with:\n"
    "RUN_TOOL <name> [args]\n"
    "For shell commands, reply with the command. Reply DONE when finished."
)

def main():
    llm = LLMBackend()
    tools = ToolManager()
    history = [
        {"role": "system", "content": PROMPT_TEMPLATE},
    ]
    task = input("Task: ")
    history.append({"role": "user", "content": task})

    while True:
        reply = llm.ask_llm(history, temperature=0.2, max_tokens=256)
        message = reply["choices"][0]["message"]["content"].strip()
        print("LLM:", message)
        if message.upper().startswith("DONE"):
            break
        elif message.startswith("CREATE_TOOL "):
            _, code = message.split("\n", 1)
            result = tools.save_tool(code)
        elif message.startswith("RUN_TOOL "):
            parts = message.split()
            name = parts[1]
            args = parts[2:]
            if name == "fetch":
                result = fetch(*args)
            else:
                result = tools.run_tool(name, *args)
        else:
            command = message.splitlines()[-1]
            try:
                result = subprocess.check_output(
                    command, shell=True, text=True, stderr=subprocess.STDOUT
                )
            except subprocess.CalledProcessError as e:
                result = e.output
        print(result)
        history.extend([
            {"role": "assistant", "content": message},
            {"role": "user", "content": str(result)},
        ])

if __name__ == "__main__":
    main()
