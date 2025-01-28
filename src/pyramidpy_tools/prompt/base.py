import json
import math
import random
import re
import uuid
from datetime import datetime
from typing import Any, Dict

from jinja2 import DictLoader, Environment

# F-string pattern to detect {var} or {var:format}
F_STRING_PATTERN = r"\{([^{}]+?)\}"

env = Environment(extensions=["jinja2.ext.do"], autoescape=False)

# Add commonly used globals
env.globals.update(
    {
        # DateTime
        "now": datetime.now,
        "utcnow": datetime.utcnow,
        "datetime": datetime,
        # Random utilities
        "random": random.random,
        "randint": random.randint,
        "choice": random.choice,
        "uuid": lambda: str(uuid.uuid4()),
        # Math operations
        "round": round,
        "abs": abs,
        "min": min,
        "max": max,
        "sum": sum,
        "math": math,
        # String & data manipulation
        "len": len,
        "range": range,
        "enumerate": enumerate,
        "zip": zip,
        "json": json,
        "re": re,
    }
)


def is_f_string_template(template: str) -> bool:
    """Check if the template uses f-string style formatting."""
    # Skip Jinja2 control structures and expressions
    template = re.sub(r"{%.*?%}", "", template)  # Remove control structures
    template = re.sub(r"{{.*?}}", "", template)  # Remove expressions

    # Now check for remaining single braces
    return bool(re.search(r"(?<!{){[^{].*?}(?!})", template))


def render_f_string(template: str, variables: Dict[str, Any]) -> str:
    """Render a template using f-string style formatting."""

    def replace(match):
        key = match.group(1).split(":")[0].strip()  # Handle {var:format} cases
        return str(variables.get(key, match.group(0)))

    return re.sub(F_STRING_PATTERN, replace, template)


def load_template(template: str) -> DictLoader:
    return DictLoader({"prompt": template})


def render_template(template: str, **kwargs) -> str:
    """
    Render a template using Jinja2.
    Automatically strips any leftover braces from the output.
    """
    if is_f_string_template(template):
        print("f-string template")
        return render_f_string(template, kwargs)
    rendered = env.from_string(template).render(**kwargs)
    rendered = re.sub(r"(?<!{){([^{}]+)}(?!})", r"\1", rendered)
    return rendered.strip()
