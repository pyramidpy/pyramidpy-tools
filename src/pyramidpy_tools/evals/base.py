from autoevals.llm import (
    Factuality,
)
from .classifiers import content_safety_evaluator


def factual_evaluator(output, expected, input):
    """
    Evaluates the factual accuracy of the output.
    """
    evaluator = Factuality()
    result = evaluator(output, expected, input=input)
    return result


def message_safety_evaluator(message: str) -> dict:
    """
    Evaluate the safety of a message directed at an AI system.
    Returns a dict with safety score and analysis.
    """
    result = content_safety_evaluator(input=message)

    # Determine risk level based on score
    risk_level = None
    if result.score == 1.0:
        risk_level = "SAFE"
    elif result.score == 0.5:
        risk_level = "SUSPICIOUS"
    else:
        risk_level = "UNSAFE"

    return {
        "risk_level": risk_level,
        "safety_score": result.score,
        "analysis": result.metadata,
        "should_block": result.score == 0.0,  # Block unsafe content
    }
