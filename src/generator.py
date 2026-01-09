"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK GENERATOR                                 ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to implement your data generation logic.                 ║
║  Replace the example implementation with your own task.                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from typing import Dict, List, Tuple

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class TaskGenerator(BaseGenerator):
    """
    Majority Color Task Generator.
    
    Generates images with multiple colored shapes and asks to identify
    which color appears most frequently.
    """
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        
        # Initialize video generator if enabled
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
        
        # Define color palette
        self.color_palette = [
            (255, 0, 0),      # Red
            (0, 255, 0),      # Green
            (0, 0, 255),      # Blue
            (255, 255, 0),    # Yellow
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Cyan
            (255, 165, 0),    # Orange
            (128, 0, 128),    # Purple
            (255, 192, 203),  # Pink
            (165, 42, 42),    # Brown
        ]
        
        # Color names mapping
        self.color_names = {
            (255, 0, 0): "red",
            (0, 255, 0): "green",
            (0, 0, 255): "blue",
            (255, 255, 0): "yellow",
            (255, 0, 255): "magenta",
            (0, 255, 255): "cyan",
            (255, 165, 0): "orange",
            (128, 0, 128): "purple",
            (255, 192, 203): "pink",
            (165, 42, 42): "brown",
        }
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one task pair."""
        
        # Generate task data
        task_data = self._generate_task_data()
        
        # Render initial state image
        first_image = self._render_initial_state(task_data)
        
        # Render final state (always generate final_frame.png)
        final_image = self._render_final_state(task_data)
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id, task_data)
        
        # Select prompt
        prompt = get_prompt(task_data.get("type", "default"))
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC METHODS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_task_data(self) -> dict:
        """Generate task data with colored shapes."""
        width, height = self.config.image_size
        
        # Select colors to use
        num_colors = min(self.config.num_colors, len(self.color_palette))
        selected_colors = random.sample(self.color_palette, num_colors)
        
        # Determine majority color (will have more shapes)
        majority_color = random.choice(selected_colors)
        other_colors = [c for c in selected_colors if c != majority_color]
        
        # Calculate distribution: majority gets 40-50%, others share the rest
        num_shapes = self.config.num_shapes
        majority_count = random.randint(
            max(1, num_shapes // 2 + 1),  # At least 50% + 1
            num_shapes - len(other_colors)  # Leave at least 1 for each other color
        )
        
        # Distribute remaining shapes among other colors
        remaining = num_shapes - majority_count
        other_counts = self._distribute_shapes(remaining, len(other_colors))
        
        # Create shape list with colors
        shapes = []
        
        # Add majority color shapes
        for _ in range(majority_count):
            shapes.append({
                "color": majority_color,
                "is_majority": True
            })
        
        # Add other color shapes
        for i, color in enumerate(other_colors):
            count = other_counts[i] if i < len(other_counts) else 1
            for _ in range(count):
                shapes.append({
                    "color": color,
                    "is_majority": False
                })
        
        # Shuffle shapes for random placement
        random.shuffle(shapes)
        
        # Generate positions and sizes for each shape
        shape_data = []
        for shape_info in shapes:
            shape_type = random.choice(self.config.shape_types)
            size = random.randint(self.config.min_shape_size, self.config.max_shape_size)
            
            # Random position (ensure shape fits within image)
            x = random.randint(size // 2, width - size // 2)
            y = random.randint(size // 2, height - size // 2)
            
            shape_data.append({
                "type": shape_type,
                "color": shape_info["color"],
                "is_majority": shape_info["is_majority"],
                "x": x,
                "y": y,
                "size": size,
            })
        
        return {
            "shapes": shape_data,
            "majority_color": majority_color,
            "majority_color_name": self.color_names[majority_color],
            "type": "default",
        }
    
    def _distribute_shapes(self, total: int, num_colors: int) -> List[int]:
        """Distribute shapes among colors (at least 1 per color)."""
        if num_colors == 0:
            return []
        
        if total < num_colors:
            # Not enough for all colors, give 1 to first few
            return [1] * total + [0] * (num_colors - total)
        
        # Give at least 1 to each
        result = [1] * num_colors
        remaining = total - num_colors
        
        # Distribute remaining randomly
        for _ in range(remaining):
            idx = random.randint(0, num_colors - 1)
            result[idx] += 1
        
        return result
    
    def _render_initial_state(self, task_data: dict) -> Image.Image:
        """Render image with all colored shapes."""
        img = self.renderer.create_blank_image(bg_color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        for shape in task_data["shapes"]:
            self._draw_shape(
                draw,
                shape["type"],
                shape["x"],
                shape["y"],
                shape["size"],
                shape["color"]
            )
        
        return img
    
    def _render_final_state(self, task_data: dict) -> Image.Image:
        """Render image showing only the majority color shapes (remove all others)."""
        img = self.renderer.create_blank_image(bg_color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Only draw majority color shapes - completely remove non-majority colors
        for shape in task_data["shapes"]:
            if shape["is_majority"]:
                self._draw_shape(
                    draw,
                    shape["type"],
                    shape["x"],
                    shape["y"],
                    shape["size"],
                    shape["color"]
                )
        
        return img
    
    def _draw_shape(
        self,
        draw: ImageDraw.Draw,
        shape_type: str,
        x: int,
        y: int,
        size: int,
        color: Tuple[int, int, int]
    ):
        """Draw a shape at the given position."""
        half_size = size // 2
        
        if shape_type == "circle":
            bbox = [x - half_size, y - half_size, x + half_size, y + half_size]
            draw.ellipse(bbox, fill=color, outline=(0, 0, 0), width=2)
        
        elif shape_type == "rectangle":
            bbox = [x - half_size, y - half_size, x + half_size, y + half_size]
            draw.rectangle(bbox, fill=color, outline=(0, 0, 0), width=2)
        
        elif shape_type == "ellipse":
            # Ellipse with different width/height
            w = size
            h = int(size * 0.7)
            bbox = [x - w // 2, y - h // 2, x + w // 2, y + h // 2]
            draw.ellipse(bbox, fill=color, outline=(0, 0, 0), width=2)
        
        elif shape_type == "triangle":
            # Draw triangle
            points = [
                (x, y - half_size),
                (x - half_size, y + half_size),
                (x + half_size, y + half_size),
            ]
            draw.polygon(points, fill=color, outline=(0, 0, 0), width=2)
    
    def _fade_color(self, color: Tuple[int, int, int], fade_factor: float = 0.3) -> Tuple[int, int, int]:
        """Fade a color by blending with gray."""
        bg_gray = 200
        return tuple(
            int(c * fade_factor + bg_gray * (1 - fade_factor))
            for c in color
        )
    
    def _generate_video(
        self,
        first_image: Image.Image,
        final_image: Image.Image,
        task_id: str,
        task_data: dict
    ) -> str:
        """Generate ground truth video showing the answer."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames
        frames = self._create_animation_frames(task_data, first_image, final_image)
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_animation_frames(
        self,
        task_data: dict,
        first_image: Image.Image,
        final_image: Image.Image,
        hold_frames: int = 10,
        transition_frames: int = 20
    ) -> List[Image.Image]:
        """Create animation frames revealing the majority color."""
        frames = []
        
        # Hold initial position
        for _ in range(hold_frames):
            frames.append(first_image.copy())
        
        # Create transition: fade out non-majority colors
        if final_image:
            # Use crossfade if we have final image
            start_rgba = first_image.convert('RGBA')
            end_rgba = final_image.convert('RGBA')
            
            if start_rgba.size != end_rgba.size:
                end_rgba = end_rgba.resize(start_rgba.size, Image.Resampling.LANCZOS)
            
            for i in range(transition_frames):
                alpha = i / (transition_frames - 1) if transition_frames > 1 else 1.0
                blended = Image.blend(start_rgba, end_rgba, alpha)
                frames.append(blended.convert('RGB'))
        else:
            # Create custom animation: gradually fade non-majority shapes
            frames.extend(self._create_fade_animation_frames(
                task_data, first_image, transition_frames
            ))
        
        # Hold final position
        final_frame = final_image if final_image else frames[-1]
        for _ in range(hold_frames):
            frames.append(final_frame.copy())
        
        return frames
    
    def _create_fade_animation_frames(
        self,
        task_data: dict,
        first_image: Image.Image,
        num_frames: int
    ) -> List[Image.Image]:
        """Create frames that gradually fade non-majority colors."""
        frames = []
        width, height = self.config.image_size
        
        for i in range(num_frames):
            progress = i / (num_frames - 1) if num_frames > 1 else 1.0
            
            # Create new frame
            img = Image.new('RGB', (width, height), (240, 240, 240))
            draw = ImageDraw.Draw(img)
            
            for shape in task_data["shapes"]:
                if shape["is_majority"]:
                    # Majority color stays fully visible
                    color = shape["color"]
                else:
                    # Non-majority colors fade out
                    fade_factor = 1.0 - progress * 0.7  # Fade to 30% opacity
                    color = self._fade_color(shape["color"], fade_factor)
                
                self._draw_shape(
                    draw,
                    shape["type"],
                    shape["x"],
                    shape["y"],
                    shape["size"],
                    color
                )
            
            frames.append(img)
        
        return frames
