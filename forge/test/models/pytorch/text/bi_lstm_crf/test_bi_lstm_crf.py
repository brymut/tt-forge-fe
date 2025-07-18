# SPDX-FileCopyrightText: © 2024 Tenstorrent AI ULC
#
# SPDX-License-Identifier: Apache-2.0

import pytest

import forge
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

from test.models.pytorch.text.bi_lstm_crf.model_utils.model import get_model


@pytest.mark.nightly
@pytest.mark.xfail
def test_birnn_crf():

    # Record Forge Property
    module_name = record_model_properties(
        framework=Framework.PYTORCH,
        model=ModelArch.BIRNNCRF,
        task=Task.NLP_TOKEN_CLS,
        source=Source.GITHUB,
        group=ModelGroup.RED,
        priority=ModelPriority.P1,
    )

    test_sentence = ["apple", "corporation", "is", "in", "georgia"]

    # Load model and input tensor
    model, test_input = get_model(test_sentence)
    model.eval()

    # Forge compile framework model
    compiled_model = forge.compile(model, sample_inputs=(test_input,), module_name=module_name)

    # Model Verification
    verify(test_input, model, compiled_model)
