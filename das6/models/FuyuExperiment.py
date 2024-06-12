import json
import os

import requests
from PIL import Image
from tqdm import tqdm
from transformers import FuyuProcessor, FuyuForCausalLM, BitsAndBytesConfig
import torch

from models.ModelExperiment import ModelExperiment
from data.Benchmark import Benchmark


class FuyuExperiment(ModelExperiment):
    def __init__(self, prompt_type=1):
        super().__init__(prompt_type)
        self.name = "Fuyu-8b"
        if self.prompt_type == 1:
            self.prompt = "Which word/phrase is conveyed in this image from the following options (either A, B, C, or D)?\n" \
                          "(A) {} (B) {} (C) {} (D) {}\n"
        if self.prompt_type == 2:
            self.prompt = "You are given a rebus puzzle. " \
                          "It consists of text that is used to convey a word or phrase. " \
                          "It needs to be solved through creative thinking. " \
                          "Which word/phrase is conveyed in this image from the following options (either A, B, C, or D)?\n" \
                          "(A) {} (B) {} (C) {} (D) {}\n"
        elif self.prompt_type == 3:
            self.prompt = "You are given a description of a graph that is used to convey a word or phrase. " \
                          "The nodes are elements that contain text or icons, which are then manipulated through the attributes of their node. " \
                          "The description is as follows:\n" \
                          "{}\n" \
                          "Which word/phrase is conveyed in this description from the following options (either A, B, C, or D)?\n" \
                          "(A) {} (B) {} (C) {} (D) {}\n"
        elif self.prompt_type == 4:
            self.prompt = "You are given a description of a graph that is used to convey a word or phrase. " \
                          "The nodes are elements that contain text or icons, which are then manipulated through the attributes of their node. " \
                          "The edges define spatial relationships between these elements. The description is as follows:\n" \
                          "{}\n" \
                          "Which word/phrase is conveyed in this description from the following options (either A, B, C, or D)?\n" \
                          "(A) {} (B) {} (C) {} (D) {}\n"

        self._load_model()

    def _load_model(self):
        self.processor = FuyuProcessor.from_pretrained(
            "adept/fuyu-8b",
            cache_dir=self.models_dir
        )
        self.model = FuyuForCausalLM.from_pretrained(
            "adept/fuyu-8b",
            cache_dir=self.models_dir,
            device_map={"": 0},
        )

    def run_on_benchmark(self, save_dir):
        benchmark = Benchmark(with_metadata=True)
        puzzles = benchmark.get_puzzles()

        metadata = self.get_metadata(benchmark, save_dir)
        print(json.dumps(metadata, indent=3))

        for puzzle in tqdm(puzzles, desc=f"Prompting {self.name}"):
            image = Image.open(puzzle["image"]).convert("RGB")
            options = puzzle["options"]
            prompt_format = list(options.values())
            if self.prompt_type == 3:
                prompt_format = [puzzle["metadata"]["nodes"]] + list(options.values())
            elif self.prompt_type == 4:
                prompt_format = [puzzle["metadata"]["nodes_and_edges"]] + list(options.values())
            prompt = self.prompt.format(*prompt_format)
            puzzle["prompt"] = prompt
            inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(device=self.device,
                                                                                       dtype=torch.float16)
            generated_ids = self.model.generate(**inputs, max_new_tokens=200)
            generated_text = self.processor.batch_decode(generated_ids[:, -200:], skip_special_tokens=True)[0].strip()
            puzzle["output"] = generated_text

        with open(f"{save_dir}/{'_'.join(self.name.lower().split())}_prompt_{self.prompt_type}.json", "w+") as file:
            json.dump({
                "metadata": metadata,
                "results": puzzles
            }, file, indent=3)

        # self.delete_downloads()
