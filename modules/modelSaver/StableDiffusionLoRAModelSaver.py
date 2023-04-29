import json
import os.path
from pathlib import Path

import torch

from modules.model.BaseModel import BaseModel
from modules.model.StableDiffusionModel import StableDiffusionModel
from modules.modelSaver.BaseModelSaver import BaseModelSaver
from modules.util.enum.ModelFormat import ModelFormat
from modules.util.enum.ModelType import ModelType


class StableDiffusionLoRAModelSaver(BaseModelSaver):

    @staticmethod
    def __save_ckpt(
            model: StableDiffusionModel,
            destination: str,
            dtype: torch.dtype,
    ):

        state_dict = {}
        if model.text_encoder_lora is not None:
            state_dict |= model.text_encoder_lora.state_dict()
        if model.unet_lora is not None:
            state_dict |= model.unet_lora.state_dict()
        save_state_dict = BaseModelSaver._convert_state_dict_dtype(state_dict, dtype)

        os.makedirs(Path(destination).parent.absolute(), exist_ok=True)
        torch.save(save_state_dict, destination)

    @staticmethod
    def __save_internal(
            model: StableDiffusionModel,
            destination: str,
    ):
        text_encoder_dtype = None if model.text_encoder_lora is None else \
            model.text_encoder_lora.parameters()[0].data.dtype

        unet_dtype = None if model.unet_lora is None else \
            model.unet_lora.parameters()[0].data.dtype

        if text_encoder_dtype is not None and text_encoder_dtype != torch.float32 \
                or unet_dtype is not None and unet_dtype != torch.float32:
            # The internal model format requires float32 weights.
            # Other formats don't have the required precision for training.
            raise ValueError("Model weights need to be in float32 format. Something has gone wrong!")

        os.makedirs(destination, exist_ok=True)

        # embedding
        StableDiffusionLoRAModelSaver.__save_ckpt(
            model,
            os.path.join(destination, "lora", "lora.pt"),
            torch.float32
        )

        # optimizer
        os.makedirs(os.path.join(destination, "optimizer"), exist_ok=True)
        torch.save(model.optimizer.state_dict(), os.path.join(destination, "optimizer", "optimizer.pt"))

        # meta
        with open(os.path.join(destination, "meta.json"), "w") as meta_file:
            json.dump({
                'train_progress': {
                    'epoch': model.train_progress.epoch,
                    'epoch_step': model.train_progress.epoch_step,
                    'epoch_sample': model.train_progress.epoch_sample,
                    'global_step': model.train_progress.global_step,
                },
            }, meta_file)

    def save(
            self,
            model: BaseModel,
            model_type: ModelType,
            output_model_format: ModelFormat,
            output_model_destination: str,
            dtype: torch.dtype,
    ):
        if model_type.is_stable_diffusion():
            match output_model_format:
                case ModelFormat.DIFFUSERS:
                    raise NotImplementedError
                case ModelFormat.CKPT:
                    self.__save_ckpt(model, output_model_destination, dtype)
                case ModelFormat.SAFETENSORS:
                    raise NotImplementedError
                case ModelFormat.INTERNAL:
                    self.__save_internal(model, output_model_destination)
