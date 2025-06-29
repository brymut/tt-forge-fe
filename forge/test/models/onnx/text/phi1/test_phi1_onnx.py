# SPDX-FileCopyrightText: (c) 2025 Tenstorrent AI ULC
#
# SPDX-License-Identifier: Apache-2.0
import pytest
import subprocess
import onnx
from transformers import (
    AutoTokenizer,
    PhiForCausalLM,
    PhiForSequenceClassification,
    PhiForTokenClassification,
)

import forge
from forge.verify.verify import verify

from forge.forge_property_utils import Framework, Source, Task, ModelArch, record_model_properties
from test.models.models_utils import build_optimum_cli_command
from test.utils import download_model

variants = ["microsoft/phi-1"]


@pytest.mark.out_of_memory
@pytest.mark.nightly
@pytest.mark.skip("Insufficient host DRAM to run this model (requires a bit more than 22 GB during compile time)")
@pytest.mark.parametrize("variant", variants)
def test_phi_causal_lm_onnx(variant, forge_tmp_path):

    # Record Forge Property
    module_name = record_model_properties(
        framework=Framework.ONNX,
        model=ModelArch.PHI1,
        variant=variant,
        source=Source.HUGGINGFACE,
        task=Task.CAUSAL_LM,
    )

    # Load tokenizer and model from HuggingFace
    framework_model = download_model(PhiForCausalLM.from_pretrained, variant, return_dict=False, use_cache=False)
    tokenizer = download_model(AutoTokenizer.from_pretrained, variant)

    # input_prompt
    input_prompt = "Africa is an emerging economy because"
    inputs = tokenizer(input_prompt, return_tensors="pt")

    input_ids = inputs["input_ids"]
    attn_mask = inputs["attention_mask"]
    sample_inputs = [input_ids, attn_mask]

    # Export model to ONNX
    onnx_path = f"{forge_tmp_path}/model.onnx"
    command = build_optimum_cli_command(variant, forge_tmp_path)
    subprocess.run(command, check=True)

    # Load framework model
    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_path)
    framework_model = forge.OnnxModule(module_name, onnx_model, onnx_path)

    # Forge compile framework model
    compiled_model = forge.compile(framework_model, sample_inputs, module_name=module_name)

    # Model Verification
    verify(
        sample_inputs,
        framework_model,
        compiled_model,
    )
