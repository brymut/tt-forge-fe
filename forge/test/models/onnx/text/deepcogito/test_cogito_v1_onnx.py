# SPDX-FileCopyrightText: (c) 2025 Tenstorrent AI ULC
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import torch
import onnx
from onnx import external_data_helper

import forge
from forge.verify.verify import verify
from forge.forge_property_utils import Framework, Source, Task, ModelArch, record_model_properties

from test.models.pytorch.text.deepcogito.model_utils.model import get_input_model


@pytest.mark.out_of_memory
@pytest.mark.nightly
@pytest.mark.parametrize("variant", ["deepcogito/cogito-v1-preview-llama-3B"])
def test_cogito_generation_onnx(forge_tmp_path, variant):
    # Record Forge Property
    module_name = record_model_properties(
        framework=Framework.ONNX,
        model=ModelArch.COGITO,
        variant=variant,
        task=Task.NLP_TEXT_GEN,
        source=Source.HUGGINGFACE,
    )
    pytest.xfail(reason="Requires multi-chip support")

    # Load model and tokenizer
    sample_inputs, framework_model = get_input_model(variant)

    # Export paths
    temp_onnx = forge_tmp_path / "temp_model.onnx"
    final_onnx = forge_tmp_path / "cogito.onnx"
    external_data_file = forge_tmp_path / "cogito.onnx.data"

    # Export to ONNX
    torch.onnx.export(
        framework_model,
        sample_inputs,
        str(temp_onnx),
        input_names=["input_ids"],
        output_names=["logits"],
        dynamic_axes={"input_ids": {0: "batch_size", 1: "seq_len"}},
        export_params=True,
        do_constant_folding=False,
    )

    onnx_model = onnx.load(str(temp_onnx))
    external_data_helper.convert_model_to_external_data(
        onnx_model,
        all_tensors_to_one_file=True,
        location=external_data_file.name,
        size_threshold=1024,
        convert_attribute=False,
    )
    onnx.save(onnx_model, str(final_onnx))

    # Load and validate ONNX model
    loaded_model = onnx.load(str(final_onnx), load_external_data=True)
    onnx.checker.check_model(str(final_onnx))

    # Create Forge ONNX model
    framework_model = forge.OnnxModule(module_name, loaded_model, onnx_path=final_onnx)

    # Compile with Forge
    compiled_model = forge.compile(
        framework_model,
        sample_inputs=sample_inputs,
        module_name=module_name,
    )

    # Run verification
    verify(
        sample_inputs,
        framework_model,
        compiled_model,
    )
