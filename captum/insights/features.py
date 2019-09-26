import base64
from collections import namedtuple
from io import BytesIO
from typing import Callable, List, Optional, Union

from captum.attr._utils import visualization as viz

import numpy as np
from matplotlib import pyplot as plt

FeatureOutput = namedtuple("FeatureOutput", "name base modified type contribution")


def _convert_img_base64(img):
    buff = BytesIO()

    plt.imsave(buff, img, format="png")
    base64img = base64.b64encode(buff.getvalue()).decode("utf-8")
    return base64img


def _convert_figure_base64(fig):
    buff = BytesIO()
    fig.savefig(buff, format="png")
    base64img = base64.b64encode(buff.getvalue()).decode("utf-8")
    return base64img


class BaseFeature:
    def __init__(
        self,
        name: str,
        baseline_transforms: Optional[Union[Callable, List[Callable]]],
        input_transforms: Optional[Union[Callable, List[Callable]]],
        visualization_transform: Optional[Callable],
    ):
        self.name = name
        self.baseline_transforms = baseline_transforms
        self.input_transforms = input_transforms
        self.visualization_transform = visualization_transform

    def visualization_type(self) -> str:
        raise NotImplementedError

    def visualize(self, attribution, data) -> FeatureOutput:
        raise NotImplementedError


class ImageFeature(BaseFeature):
    def __init__(
        self,
        name: str,
        input_transforms: Union[Callable, List[Callable]],
        baseline_transforms: Union[Callable, List[Callable]],
        visualization_transforms: Optional[Union[Callable, List[Callable]]] = None,
    ):
        super().__init__(
            name,
            baseline_transforms=baseline_transforms,
            input_transforms=input_transforms,
            visualization_transform=None,
        )

    def visualization_type(self) -> str:
        return "image"

    def visualize(self, attribution, data) -> FeatureOutput:
        attribution.squeeze_()
        data.squeeze_()
        data_t = np.transpose(data.cpu().detach().numpy(), (1, 2, 0))
        attribution_t = np.transpose(
            attribution.squeeze().cpu().detach().numpy(), (1, 2, 0)
        )

        fig, axis = viz.visualize_image_attr(
            attribution_t, (data_t / 2) + 0.5, method="heat_map", sign="absolute_value"
        )

        attr_img_64 = _convert_figure_base64(fig)
        img_64 = _convert_img_base64(data_t)

        return FeatureOutput(
            name=self.name,
            base=img_64,
            modified=attr_img_64,
            type=self.visualization_type(),
            contribution=100,  # TODO implement contribution
        )
