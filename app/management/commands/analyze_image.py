import json
from pathlib import Path
from typing import List, Tuple, Dict, Any
import multiprocessing as mp

import cv2
import numpy as np
import pytesseract
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from skimage.feature import hog

from ..base.out_mixin import OutMixin


class Command(OutMixin, BaseCommand):
    help = "Detect text and analyze fonts in images from a specified folder using multiprocessing"

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
        parser.add_argument(
            "--num-processes",
            type=int,
            default=mp.cpu_count(),
            help="Number of processes to use (default: number of CPU cores)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        folder_src: Path = Path(options["folder_src"]).resolve()
        folder_dst: Path = Path(settings.MEDIA_ROOT, options["folder_dst"])
        max_images: int = options["max_images"]
        verbose: bool = options["verbose"] > 0
        num_processes: int = options["num_processes"]

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

        self.out_success(
            f"Processing {len(image_files)} out of {total_images} images found."
        )
        self.out_success(f"Using {num_processes} processes.")

        with mp.Pool(processes=num_processes) as pool:
            results = pool.starmap(
                self.process_image,
                [(image_path, folder_dst, verbose) for image_path in image_files],
            )

        successful = sum(1 for result in results if result)
        self.out_success(
            f"Processing completed. Successfully processed {successful} out of {len(image_files)} images."
        )

    @staticmethod
    def process_image(image_path: Path, folder_dst: Path, verbose: bool) -> bool:
        try:
            image: np.ndarray = cv2.imread(str(image_path))

            # Reduce image resolution by half
            height, width = image.shape[:2]
            image = cv2.resize(
                image, (width // 2, height // 2), interpolation=cv2.INTER_AREA
            )

            gray: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            text_regions: List[Tuple[int, int, int, int]] = Command.detect_text_regions(
                gray
            )
            results: List[Dict[str, Any]] = []

            annotated_image = image.copy()

            for i, (x, y, w, h) in enumerate(text_regions):
                region: np.ndarray = gray[y : y + h, x : x + w]
                text: str = pytesseract.image_to_string(region)
                font_features: np.ndarray = Command.extract_font_features(region)

                results.append(
                    {
                        "region_id": i,
                        "text": text.strip(),
                        "font_features": font_features.tolist(),
                        "position": (
                            x * 2,
                            y * 2,
                            w * 2,
                            h * 2,
                        ),  # Scale back to original size
                    }
                )

                # Draw rectangle on the annotated image
                cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Scale annotated image back to original size for saving
            annotated_image = cv2.resize(
                annotated_image, (width, height), interpolation=cv2.INTER_LINEAR
            )

            Command.save_results(results, annotated_image, folder_dst, image_path.stem)

            if verbose:
                print(f"  Analysis completed for {image_path.name}")
            return True
        except Exception as e:
            if verbose:
                print(f"  Error processing {image_path.name}: {str(e)}")
            return False

    @staticmethod
    def detect_text_regions(gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect potential text regions in a grayscale image using MSER."""
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)

        text_regions: List[Tuple[int, int, int, int]] = []
        for region in regions:
            x, y, w, h = cv2.boundingRect(region)
            if 5 < w < gray.shape[1] * 0.9 and 5 < h < gray.shape[0] * 0.9:
                text_regions.append((x, y, w, h))

        return Command.merge_overlapping_regions(text_regions)

    @staticmethod
    def merge_overlapping_regions(
        regions: List[Tuple[int, int, int, int]]
    ) -> List[Tuple[int, int, int, int]]:
        """Merge overlapping regions."""
        if not regions:
            return []

        sorted_regions = sorted(regions, key=lambda r: r[0])

        merged = []
        for region in sorted_regions:
            if not merged:
                merged.append(region)
            else:
                last = merged[-1]
                if Command.regions_overlap(last, region):
                    merged[-1] = Command.combine_regions(last, region)
                else:
                    merged.append(region)

        return merged

    @staticmethod
    def regions_overlap(
        r1: Tuple[int, int, int, int], r2: Tuple[int, int, int, int]
    ) -> bool:
        """Check if two regions overlap."""
        return not (
            r1[0] + r1[2] < r2[0]
            or r2[0] + r2[2] < r1[0]
            or r1[1] + r1[3] < r2[1]
            or r2[1] + r2[3] < r1[1]
        )

    @staticmethod
    def combine_regions(
        r1: Tuple[int, int, int, int], r2: Tuple[int, int, int, int]
    ) -> Tuple[int, int, int, int]:
        """Combine two overlapping regions."""
        x = min(r1[0], r2[0])
        y = min(r1[1], r2[1])
        w = max(r1[0] + r1[2], r2[0] + r2[2]) - x
        h = max(r1[1] + r1[3], r2[1] + r2[3]) - y
        return (x, y, w, h)

    @staticmethod
    def extract_font_features(image: np.ndarray) -> np.ndarray:
        """Extract HOG features from the image to represent font characteristics."""
        max_dimension = 100
        h, w = image.shape
        if h > w:
            new_h, new_w = max_dimension, int(w * (max_dimension / h))
        else:
            new_h, new_w = int(h * (max_dimension / w)), max_dimension
        resized = cv2.resize(image, (new_w, new_h))

        padded = np.zeros((max_dimension, max_dimension), dtype=np.uint8)
        padded[:new_h, :new_w] = resized

        features, _ = hog(
            padded,
            orientations=8,
            pixels_per_cell=(16, 16),
            cells_per_block=(1, 1),
            visualize=True,
        )
        return features

    @staticmethod
    def save_results(
        results: List, annotated_image: np.ndarray, folder_dst: Path, image_name: str
    ):
        """Save analysis results to a JSON file and the annotated image."""
        result_file: Path = folder_dst / f"{image_name}_analysis.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        image_file: Path = folder_dst / f"{image_name}_annotated.jpg"
        cv2.imwrite(str(image_file), annotated_image)
