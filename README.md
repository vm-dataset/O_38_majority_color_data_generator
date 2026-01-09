# Majority Color Task Data Generator 🎨

A data generator for creating majority color reasoning tasks. Generates images with multiple colored shapes and asks models to identify which color appears most frequently.

This task generator follows the [template-data-generator](https://github.com/vm-dataset/template-data-generator.git) format and is compatible with [VMEvalKit](https://github.com/Video-Reason/VMEvalKit.git).

Repository: [O_38_majority_color_data_generator](https://github.com/vm-dataset/O_38_majority_color_data_generator)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vm-dataset/O_38_majority_color_data_generator.git
cd O_38_majority_color_data_generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python examples/generate.py --num-samples 50
```

---

## 📁 Structure

```
majority-color-task-data-generator/
├── core/                    # ✅ KEEP: Standard utilities
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py          # Pydantic models
│   ├── image_utils.py      # Image helpers
│   ├── video_utils.py      # Video generation
│   └── output_writer.py    # File output
├── src/                     # ⚠️ CUSTOMIZE: Your task logic
│   ├── generator.py        # Majority color task generator
│   ├── prompts.py          # Task prompt templates
│   └── config.py           # Task configuration
├── examples/
│   └── generate.py         # Entry point
└── data/questions/         # Generated output
```

---

## 📦 Output Format

Every generator produces:

```
data/questions/{domain}_task/{task_id}/
├── first_frame.png          # Initial state (REQUIRED)
├── final_frame.png          # Goal state (or goal.txt)
├── prompt.txt               # Instructions (REQUIRED)
└── ground_truth.mp4         # Solution video (OPTIONAL)
```

---

## 🎨 Task Description

The majority color task generates images containing multiple colored shapes (circles, rectangles, ellipses) and asks video models to identify which color appears most frequently in the image.

**Task Components:**
- **Initial State** (`first_frame.png`): An image with multiple colored shapes randomly distributed
- **Final State** (`final_frame.png`): The same image with non-majority colors removed, highlighting the majority color
- **Prompt**: Instructions asking the model to identify the dominant color
- **Video** (optional): Animation showing the transition from initial to final state

**Configuration Options:**
- `num_colors`: Number of different colors to use (default: 4)
- `num_shapes`: Total number of colored shapes (default: 15)
- `shape_types`: Types of shapes to use (circle, rectangle, ellipse, triangle)
- `min_shape_size` / `max_shape_size`: Size range for shapes

---

## 🎨 Customization (3 Files to Modify)

### 1. Update `src/generator.py`

The majority color generator is already implemented. You can customize it to add more features:

```python
from core import BaseGenerator, TaskPair, ImageRenderer

class TaskGenerator(BaseGenerator):
    def __init__(self, config):
        super().__init__(config)
        self.renderer = ImageRenderer(config.image_size)
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        # Generate your problem
        task_data = self._generate_task_data()
        
        # Render images
        first_image = self._render_initial_state(task_data)
        final_image = self._render_final_state(task_data)
        
        # Create TaskPair
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=self.select_prompt(),
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=None  # Optional
        )
```

### 2. Update `src/prompts.py`

Customize the prompts for your task:

```python
PROMPTS = {
    "default": [
        "Identify which color appears most frequently in the image.",
        "Determine the dominant color in this image.",
    ]
}

def get_prompt(task_type: str = "default") -> str:
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)
```

### 3. Update `src/config.py`

**All hyperparameters go here** - both general and task-specific:

```python
from core import GenerationConfig
from pydantic import Field

class TaskConfig(GenerationConfig):
    """Your task-specific configuration."""
    # Inherits: num_samples, domain, seed, output_dir, image_size
    
    # Override defaults
    domain: str = Field(default="majority_color")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    # Task-specific hyperparameters
    num_colors: int = Field(default=4, description="Number of different colors")
    num_shapes: int = Field(default=15, description="Total number of shapes")
    shape_types: list[str] = Field(default_factory=lambda: ["circle", "rectangle", "ellipse"])
    min_shape_size: int = Field(default=30)
    max_shape_size: int = Field(default=80)
```

**Single entry point:** `python examples/generate.py --num-samples 50`
