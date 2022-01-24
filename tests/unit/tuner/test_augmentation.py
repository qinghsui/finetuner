import os

import numpy as np
import pytest
from docarray import Document

from finetuner.tuner.augmentation import _vision_preprocessor

cur_dir = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize('phase', ['train', 'validation'])
@pytest.mark.parametrize(
    'doc, height, width, num_channels, default_channel_axis, target_channel_axis',
    [
        (Document(tensor=np.random.rand(224, 224, 3)), 224, 224, 3, -1, 0),
        (Document(tensor=np.random.rand(256, 256, 3)), 256, 256, 3, -1, 0),
        (
            Document(tensor=np.random.rand(256, 256, 3).astype('uint8')),
            256,
            256,
            3,
            -1,
            0,
        ),
        (Document(tensor=np.random.rand(256, 256, 1)), 256, 256, 1, -1, 0),  # grayscale
        (
            Document(tensor=np.random.rand(256, 256, 3)),
            256,
            256,
            3,
            -1,
            -1,
        ),  # different target channel axis
        (
            Document(tensor=np.random.rand(3, 224, 224)),
            224,
            224,
            3,
            0,
            0,
        ),  # channel axis at 0th position
        (
            Document(uri=os.path.join(cur_dir, 'resources/lena.png')),
            512,
            512,
            3,
            1,
            0,
        ),  # load from uri
    ],
)
def test_vision_preprocessor(
    doc, height, width, num_channels, default_channel_axis, target_channel_axis, phase
):
    original_tensor = doc.tensor
    augmented_tensor = _vision_preprocessor(
        doc, height, width, default_channel_axis, target_channel_axis, phase
    )
    assert augmented_tensor is not None
    assert not np.array_equal(original_tensor, augmented_tensor)
    assert np.issubdtype(augmented_tensor.dtype, np.floating)
    if target_channel_axis == -1:
        assert augmented_tensor.shape == (height, width, num_channels)
    elif target_channel_axis == 0:
        assert augmented_tensor.shape == (num_channels, height, width)


def test_vision_preprocessor_fail_given_no_tensor_and_uri():
    doc = Document()
    with pytest.raises(AttributeError):
        _vision_preprocessor(doc)