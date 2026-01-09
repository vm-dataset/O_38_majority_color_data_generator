"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK PROMPTS                                   ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define prompts/instructions for your task.            ║
║  Prompts are selected based on task type and returned to the model.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": [
        "Identify which color appears most frequently in the image. Show the majority color by highlighting or emphasizing it.",
        "Determine the dominant color in this image. Animate to reveal which color has the most presence.",
        "Find the color that appears most often. Create a video that demonstrates the majority color.",
        "What is the most common color in this image? Show the answer by highlighting the majority color.",
        "Count the colors and identify which one is in the majority. Visualize the result by emphasizing the dominant color.",
    ],
    
    "highlight": [
        "Highlight all instances of the majority color in the image.",
        "Show which color is most frequent by making it stand out.",
        "Emphasize the dominant color by highlighting it throughout the image.",
    ],
    
    "reveal": [
        "Reveal the answer by showing only the majority color.",
        "Fade out all colors except the majority color to reveal the answer.",
        "Show the majority color by removing all other colors.",
    ],
}


def get_prompt(task_type: str = "default") -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        
    Returns:
        Random prompt string from the specified type
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])
