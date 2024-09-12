import json
import os
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
            gray: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply denoising and contrast enhancement
            gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            gray = cv2.equalizeHist(gray)

            text_regions: List[Tuple[int, int, int, int]] = Command.detect_text_regions(
                gray, image
            )
            results: List[Dict[str, Any]] = []

            annotated_image = image.copy()

            for i, (x, y, w, h) in enumerate(text_regions):
                region: np.ndarray = gray[y : y + h, x : x + w]

                # Apply adaptive thresholding to the region before OCR
                region = cv2.adaptiveThreshold(
                    region,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    11,
                    2,
                )

                text: str = pytesseract.image_to_string(region, config="--psm 6")

                # Process only regions with detected text
                if text.strip():
                    font_features: np.ndarray = Command.extract_font_features(region)

                    results.append(
                        {
                            "region_id": i,
                            "text": text.strip(),
                            "font_features": font_features.tolist(),
                            "position": (x, y, w, h),
                        }
                    )

                    # Draw a rectangle on the annotated image
                    cv2.rectangle(
                        annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2
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
    def detect_text_regions(
        gray: np.ndarray, color_image: np.ndarray
    ) -> List[Tuple[int, int, int, int]]:
        # Use a combination of methods for better detection
        mser_regions = Command.detect_mser_regions(gray)
        east_regions = Command.detect_east_regions(gray)

        # Merge regions detected by both methods
        all_regions = mser_regions + east_regions

        # Filter and merge overlapping regions
        text_regions = Command.filter_and_merge_regions(all_regions, gray, color_image)

        return text_regions

    @staticmethod
    def detect_mser_regions(gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        return [cv2.boundingRect(region) for region in regions]

    @staticmethod
    def detect_east_regions(image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        east_model_path = os.path.abspath("frozen_east_text_detection.pb")
        if not os.path.exists(east_model_path):
            raise FileNotFoundError(
                f"EAST model file not found at location: {east_model_path}"
            )
        try:
            net = cv2.dnn.readNet(east_model_path)
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise

        height, width = image.shape[:2]
        new_width = 320
        new_height = 320

        # Ensure the image is in BGR format
        if len(image.shape) == 2:  # If the image is grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.shape[2] == 4:  # If the image has an alpha channel
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        blob = cv2.dnn.blobFromImage(
            image, 1.0, (new_width, new_height), (123.68, 116.78, 103.94), True, False
        )
        net.setInput(blob)
        try:
            output_layers = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
            outputs = net.forward(output_layers)
            scores, geometry = outputs
        except Exception as e:
            print(f"Error during inference: {str(e)}")
            return []

        rectangles = []
        confidences = []

        for y in range(0, geometry.shape[2]):
            scores_data = scores[0, 0, y]
            x_data0 = geometry[0, 0, y]
            x_data1 = geometry[0, 1, y]
            x_data2 = geometry[0, 2, y]
            x_data3 = geometry[0, 3, y]
            angles_data = geometry[0, 4, y]

            for x in range(0, geometry.shape[3]):
                if scores_data[x] < 0.5:
                    continue

                (offset_x, offset_y) = (x * 4.0, y * 4.0)

                angle = angles_data[x]
                cos = np.cos(angle)
                sin = np.sin(angle)

                h = x_data0[x] + x_data2[x]
                w = x_data1[x] + x_data3[x]

                end_x = int(offset_x + (cos * x_data1[x]) + (sin * x_data2[x]))
                end_y = int(offset_y - (sin * x_data1[x]) + (cos * x_data2[x]))
                start_x = int(end_x - w)
                start_y = int(end_y - h)

                rectangles.append((start_x, start_y, end_x, end_y))
                confidences.append(scores_data[x])

        # Apply non-maximum suppression
        from imutils.object_detection import non_max_suppression

        boxes = non_max_suppression(
            np.array(rectangles), probs=confidences, overlapThresh=0.5
        )

        # Adjust coordinates to the scale of the original image
        result = []
        for start_x, start_y, end_x, end_y in boxes:
            start_x = int(start_x * (width / new_width))
            start_y = int(start_y * (height / new_height))
            end_x = int(end_x * (width / new_width))
            end_y = int(end_y * (height / new_height))
            result.append((start_x, start_y, end_x - start_x, end_y - start_y))
        return result

    @staticmethod
    def filter_and_merge_regions(
        regions: List[Tuple[int, int, int, int]],
        gray: np.ndarray,
        color_image: np.ndarray,
    ) -> List[Tuple[int, int, int, int]]:
        filtered_regions = [
            region
            for region in regions
            if Command.is_valid_text_region(gray, color_image, *region)
        ]
        return Command.merge_overlapping_regions(filtered_regions)

    @staticmethod
    def is_valid_text_region(
        gray: np.ndarray, color_image: np.ndarray, x: int, y: int, w: int, h: int
    ) -> bool:
        # Improve filtering criteria
        if w < 10 or h < 10 or w > gray.shape[1] * 0.8 or h > gray.shape[0] * 0.8:
            return False

        aspect_ratio = w / h
        if aspect_ratio < 0.1 or aspect_ratio > 15:
            return False

        region = gray[y : y + h, x : x + w]

        # Check text variance
        if np.var(region) < 100:  # Adjust this threshold as needed
            return False

        # Check edge density
        edges = cv2.Canny(region, 100, 200)
        edge_density = np.sum(edges) / (w * h)
        if edge_density < 0.1:  # Adjust this threshold as needed
            return False

        return True

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
        results: List,
        annotated_image: np.ndarray,
        folder_dst: Path,
        image_name: str,
    ):
        """Save analysis results to a JSON file and the annotated image."""
        result_file: Path = folder_dst / f"{image_name}_analysis.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        image_file: Path = folder_dst / f"{image_name}_annotated.jpg"
        cv2.imwrite(str(image_file), annotated_image)
        print(f"{result_file=} <=> {image_file=}")
