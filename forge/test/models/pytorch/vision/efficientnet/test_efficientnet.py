# SPDX-FileCopyrightText: © 2024 Tenstorrent AI ULC

# SPDX-License-Identifier: Apache-2.0

import pytest
import timm
import torch
from loguru import logger
from PIL import Image
from third_party.tt_forge_models.tools.utils import get_file
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
from torch.hub import load_state_dict_from_url
from torchvision.models import (
    EfficientNet_B0_Weights,
    EfficientNet_B1_Weights,
    EfficientNet_B2_Weights,
    EfficientNet_B3_Weights,
    EfficientNet_B4_Weights,
    EfficientNet_B5_Weights,
    EfficientNet_B6_Weights,
    EfficientNet_B7_Weights,
    efficientnet_b0,
    efficientnet_b1,
    efficientnet_b2,
    efficientnet_b3,
    efficientnet_b4,
    efficientnet_b5,
    efficientnet_b6,
    efficientnet_b7,
)
from torchvision.models._api import WeightsEnum

import forge
from forge._C import DataFormat
from forge.config import CompilerConfig
from forge.forge_property_utils import (
    Framework,
    ModelArch,
    ModelGroup,
    ModelPriority,
    Source,
    Task,
    record_model_properties,
)
from forge.verify.verify import verify

from test.models.models_utils import print_cls_results
from test.utils import download_model

## https://huggingface.co/docs/timm/models/efficientnet

variants = [
    pytest.param(
        "efficientnet_b0",
        id="efficientnet_b0",
        marks=[pytest.mark.push],
    ),
    pytest.param(
        "efficientnet_b4",
        id="efficientnet_b4",
    ),
    pytest.param("hf_hub:timm/efficientnet_b0.ra_in1k", id="hf_hub_timm_efficientnet_b0_ra_in1k"),
    pytest.param("hf_hub:timm/efficientnet_b4.ra2_in1k", id="hf_hub_timm_efficientnet_b4_ra2_in1k"),
    pytest.param("hf_hub:timm/efficientnet_b5.in12k_ft_in1k", id="hf_hub_timm_efficientnet_b5_in12k_ft_in1k"),
    pytest.param("hf_hub:timm/tf_efficientnet_b0.aa_in1k", id="hf_hub_timm_tf_efficientnet_b0_aa_in1k"),
    pytest.param("hf_hub:timm/efficientnetv2_rw_s.ra2_in1k", id="hf_hub_timm_efficientnetv2_rw_s_ra2_in1k"),
    pytest.param("hf_hub:timm/tf_efficientnetv2_s.in21k", id="hf_hub_timm_tf_efficientnetv2_s_in21k"),
]


@pytest.mark.nightly
@pytest.mark.parametrize("variant", variants)
def test_efficientnet_timm(variant):
    if variant in ["efficientnet_b0"]:
        group = ModelGroup.RED
        priority = ModelPriority.P1
    else:
        group = ModelGroup.GENERALITY
        priority = ModelPriority.P2

    # Record Forge Property
    module_name = record_model_properties(
        framework=Framework.PYTORCH,
        model=ModelArch.EFFICIENTNET,
        variant=variant,
        source=Source.TIMM,
        task=Task.CV_IMAGE_CLS,
        group=group,
        priority=priority,
    )

    # Load model
    framework_model = download_model(timm.create_model, variant, pretrained=True).to(torch.bfloat16)
    framework_model.eval()

    # Load and pre-process image
    try:
        if variant == "hf_hub:timm/tf_efficientnetv2_s.in21k":
            file_path = get_file(
                "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/beignets-task-guide.png"
            )
            img = Image.open(file_path).convert("RGB")
            use_1k_labels = False
        else:
            file_path = get_file("https://github.com/pytorch/hub/raw/master/images/dog.jpg")
            img = Image.open(file_path).convert("RGB")
            use_1k_labels = True
        config = resolve_data_config({}, model=framework_model)
        transform = create_transform(**config)
        img_tensor = transform(img).unsqueeze(0)
    except:
        logger.warning(
            "Failed to download the image file, replacing input with random tensor. Please check if the URL is up to date"
        )
        img_tensor = torch.rand(1, 3, 224, 224)

    inputs = [img_tensor.to(torch.bfloat16)]

    data_format_override = DataFormat.Float16_b
    compiler_cfg = CompilerConfig(default_df_override=data_format_override)

    # Forge compile framework model
    compiled_model = forge.compile(
        framework_model,
        sample_inputs=inputs,
        module_name=module_name,
        compiler_cfg=compiler_cfg,
    )

    # Model Verification
    fw_out, co_out = verify(inputs, framework_model, compiled_model)

    # Run model on sample data and print results
    print_cls_results(fw_out[0], co_out[0], use_1k_labels=use_1k_labels)


def get_state_dict(self, *args, **kwargs):
    kwargs.pop("check_hash")
    return load_state_dict_from_url(self.url, *args, **kwargs)


WeightsEnum.get_state_dict = get_state_dict

variants = [
    "efficientnet_b0",
    "efficientnet_b1",
    "efficientnet_b2",
    "efficientnet_b3",
    "efficientnet_b4",
    "efficientnet_b5",
    "efficientnet_b6",
    "efficientnet_b7",
]
variant_model_map = {
    "efficientnet_b0": (efficientnet_b0, EfficientNet_B0_Weights.IMAGENET1K_V1),
    "efficientnet_b1": (efficientnet_b1, EfficientNet_B1_Weights.IMAGENET1K_V1),
    "efficientnet_b2": (efficientnet_b2, EfficientNet_B2_Weights.IMAGENET1K_V1),
    "efficientnet_b3": (efficientnet_b3, EfficientNet_B3_Weights.IMAGENET1K_V1),
    "efficientnet_b4": (efficientnet_b4, EfficientNet_B4_Weights.IMAGENET1K_V1),
    "efficientnet_b5": (efficientnet_b5, EfficientNet_B5_Weights.IMAGENET1K_V1),
    "efficientnet_b6": (efficientnet_b6, EfficientNet_B6_Weights.IMAGENET1K_V1),
    "efficientnet_b7": (efficientnet_b7, EfficientNet_B7_Weights.IMAGENET1K_V1),
}


@pytest.mark.nightly
@pytest.mark.parametrize("variant", variants)
def test_efficientnet_torchvision(variant):

    # Record Forge Property
    module_name = record_model_properties(
        framework=Framework.PYTORCH,
        model=ModelArch.EFFICIENTNET,
        variant=variant,
        source=Source.TORCHVISION,
        task=Task.CV_IMAGE_CLS,
    )

    # Load model
    model_fn, weights = variant_model_map[variant]
    framework_model = model_fn(weights)

    framework_model.eval()
    framework_model = framework_model.to(torch.bfloat16)

    # Load and pre-process image
    try:
        file_path = get_file("https://github.com/pytorch/hub/raw/master/images/dog.jpg")
        img = Image.open(file_path).convert("RGB")
        config = resolve_data_config({}, model=framework_model)
        transform = create_transform(**config)
        img_tensor = transform(img).unsqueeze(0)
    except:
        logger.warning(
            "Failed to download the image file, replacing input with random tensor. Please check if the URL is up to date"
        )
        img_tensor = torch.rand(1, 3, 224, 224)

    inputs = [img_tensor.to(torch.bfloat16)]

    data_format_override = DataFormat.Float16_b
    compiler_cfg = CompilerConfig(default_df_override=data_format_override)

    # Forge compile framework model
    compiled_model = forge.compile(
        framework_model,
        sample_inputs=inputs,
        module_name=module_name,
        compiler_cfg=compiler_cfg,
    )

    # Model Verification
    fw_out, co_out = verify(inputs, framework_model, compiled_model)

    # Run model on sample data and print results
    print_cls_results(fw_out[0], co_out[0])
