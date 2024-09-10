import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

import cv2
import numpy as np
import pytesseract
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from skimage.feature import hog

from ..base.out_mixin import OutMixin


class Command(OutMixin, BaseCommand):
    help = "Detect text and analyze fonts in images from a specified folder"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def add_arguments(self, parser):
        parser.add_argument(
            "--folder-src",
            type=str,
            required=True,
            help="Source folder containing images to analyze",
        )
        parser.add_argument(
            "--folder-dst",
            type=str,
            default="analyzed_images",
            help="Destination folder for results (relative to MEDIA_ROOT)",
        )
        parser.add_argument(
            "--max-images",
            type=int,
            default=0,
            help="Maximum number of images to process (0 = all images)",
        )
        parser.add_argument(
            "--verbose",
            type=int,
            default=1,
            help="Verbose mode (0=silent, 1=verbose), default is verbose",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        folder_src: Path = Path(options["folder_src"]).resolve()
        folder_dst: Path = Path(settings.MEDIA_ROOT, options["folder_dst"])
        max_images: int = options["max_images"]
        verbose: bool = options["verbose"] > 0

        if not folder_src.exists() or not folder_src.is_dir():
            raise CommandError(
                f"Source folder '{folder_src}' does not exist or is not a directory."
            )

        folder_dst.mkdir(parents=True, exist_ok=True)

        image_files: List[Path] = list(folder_src.glob("*.jpg")) + list(
            folder_src.glob("*.png")
        )
        total_images: int = len(image_files)

        if max_images > 0:
            image_files = image_files[:max_images]

        self.stdout.write(
            self.style.SUCCESS(
                f"Processing {len(image_files)} out of {total_images} images found."
            )
        )

        for idx, image_path in enumerate(image_files, 1):
            if verbose:
                self.stdout.write(
                    f"Processing image {idx}/{len(image_files)}: {image_path.name}"
                )

            try:
                results: List[Dict[str, Any]] = self.process_image(image_path)
                self.save_results(results, folder_dst, image_path.stem)
                if verbose:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Analysis completed for {image_path.name}"
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  Error processing {image_path.name}: {str(e)}")
                )

        self.stdout.write(self.style.SUCCESS("Processing completed."))

    def process_image(self, image_path: Path) -> List[Dict[str, Any]]:
        """Process a single image, detecting text regions and extracting font features."""
        image: np.ndarray = cv2.imread(str(image_path))
        gray: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        text_regions: List[Tuple[int, int, int, int]] = self.detect_text_regions(gray)
        results: List[Dict[str, Any]] = []

        for i, (x, y, w, h) in enumerate(text_regions):
            region: np.ndarray = gray[y : y + h, x : x + w]
            text: str = pytesseract.image_to_string(region)
            font_features: np.ndarray = self.extract_font_features(region)

            results.append(
                {
                    "region_id": i,
                    "text": text.strip(),
                    "font_features": font_features.tolist(),  # Convert to list for JSON serialization
                    "position": (x, y, w, h),
                }
            )

        return results

    @staticmethod
    def detect_text_regions(gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect potential text regions in a grayscale image."""
        thresh: np.ndarray = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

        # Find contours
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Filter contours to keep only probable text areas
        text_regions: List[Tuple[int, int, int, int]] = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 40 and h > 10:  # Adjust these values as needed
                text_regions.append((x, y, w, h))

        return text_regions

    @staticmethod
    def extract_font_features(image: np.ndarray) -> np.ndarray:
        """Extract HOG features from the image to represent font characteristics."""
        resized: np.ndarray = cv2.resize(image, (100, 100))
        features, _ = hog(
            resized,
            orientations=8,
            pixels_per_cell=(16, 16),
            cells_per_block=(1, 1),
            visualize=True,
        )
        return features

    @staticmethod
    def save_results(
        results: List[Dict[str, Any]], folder_dst: Path, image_name: str
    ) -> None:
        """Save analysis results to a JSON file."""
        result_file: Path = folder_dst / f"{image_name}_analysis.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
