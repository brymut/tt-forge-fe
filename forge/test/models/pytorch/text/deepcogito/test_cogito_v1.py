# SPDX-FileCopyrightText: (c) 2025 Tenstorrent AI ULC
#
# SPDX-License-Identifier: Apache-2.0
import pytest

import forge
from forge.forge_property_utils import (
    Framework,
    ModelArch,
    Source,
    Task,
    record_model_properties,
)
from forge.verify.verify import verify

from test.models.pytorch.text.deepcogito.model_utils.model import get_input_model


@pytest.mark.out_of_memory
@pytest.mark.xfail
@pytest.mark.nightly
@pytest.mark.parametrize("variant", ["deepcogito/cogito-v1-preview-llama-3B"])
def test_cogito_generation(variant):

    # Record Forge Property
    module_name = record_model_properties(
        framework=Framework.PYTORCH,
        model=ModelArch.COGITO,
        variant=variant,
        task=Task.NLP_TEXT_GEN,
        source=Source.HUGGINGFACE,
    )
    pytest.xfail(reason="Requires multi-chip support")

    # Load model and tokenizer
    input_tensor_list, framework_model = get_input_model(variant)
    sample_inputs = [input_tensor_list]

    # Compile with Forge
    compiled_model = forge.compile(
        framework_model,
        sample_inputs=sample_inputs,
        module_name=module_name,
    )

    # Run verification
    verify(sample_inputs, framework_model, compiled_model)
