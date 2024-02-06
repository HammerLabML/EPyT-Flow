from abc import ABC, abstractmethod
import numpy
import numpy as np

from .utils import generate_deep_random_gaussian_noise, create_deep_random_pattern
from ..serialization import serializable, Serializable, GAUSSIAN_UNCERTAINTY_ID,\
    UNIFORM_UNCERTAINTY_ID, DEEP_UNIFORM_UNCERTAINTY_ID, DEEP_GAUSSIAN_UNCERTAINTY_ID,\
    DEEP_UNCERTAINTY_ID


class Uncertainty(ABC):
    """
    Base class for uncertainties -- i.e. perturbations of data/signals.

    Parameters
    ----------
    min_value : `float`, optional
        Lower bound on the data/signal that is perturbed by this uncertainty.

        The default is None.
    max_value : `float`, optional
        Upper bound on the data/signal that is perturbed by this uncertainty.

        The default is None.
    """
    def __init__(self, min_value:float=None, max_value:float=None, **kwds):
        super().__init__(**kwds)

        self.__min_value = min_value
        self.__max_value = max_value

    @property
    def min_value(self) -> float:
        return self.__min_value

    @property
    def max_value(self) -> float:
        return self.__max_value

    def get_attributes(self) -> dict:
        return {"min_value": self.__min_value, "max_value": self.__max_value}

    def __eq__(self, other) -> bool:
        return self.__min_value == other.min_value and self.__max_value == other.max_value

    def __str__(self) -> str:
        return f"min_value: {self.__min_value} max_value: {self.__max_value}"

    def clip(self, data:numpy.ndarray) -> numpy.ndarray:
        if self.__min_value is not None:
            data = np.min([data, self.__min_value])
        if self.__max_value is not None:
            data = np.max([data, self.__max_value])

        return data

    @abstractmethod
    def apply(self, data:float):
        raise NotImplementedError()

    def apply_batch(self, data:numpy.ndarray) -> numpy.ndarray:
        for t in range(data.shape[0]):
            data[t] = self.apply(data[t])
        return data


@serializable(GAUSSIAN_UNCERTAINTY_ID)
class GaussianUncertainty(Uncertainty, Serializable):
    """
    Class implementing Gaussian uncertainty -- i.e. Gaussian noise is added to the data.

    Parameters
    ----------
    mean : `float`, optional
        Mean of the Gaussian noise.

        If None, mean will be assigned a random value between 0 and 1.

        The default is None.
    scale : `float`, optional
        Scale (i.e. standard deviation) of the Gaussian noise.

        If None, scale will be assigned a random value between 0 and 1.

        The default is None.
    """
    def __init__(self, mean:float=None, scale:float=None, **kwds):
        super().__init__(**kwds)

        self.__mean = np.random.rand() if mean is None else mean
        self.__scale = np.random.rand() if scale is None else scale

        self.__create_uncertainties()

    @property
    def mean(self) -> float:
        return self.__mean

    @property
    def scale(self) -> float:
        return self.__scale

    def get_attributes(self) -> dict:
        return super().get_attributes() | {"mean": self.__mean, "scale": self.__scale}

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.__mean == other.mean and self.__scale == other.scale

    def __str__(self) -> str:
        return super().__str__() + f" mean: {self.__mean} scale: {self.__scale}"

    def __create_uncertainties(self, n_samples:int=500) -> None:
        self.__uncertainties_idx = 0
        self.__uncertainties = np.random.normal(self.__mean, self.__scale, size=n_samples)

    def apply(self, data:float) -> float:
        data += self.__uncertainties[self.__uncertainties_idx]

        self.__uncertainties_idx += 1
        if self.__uncertainties_idx >= len(self.__uncertainties):
            self.__create_uncertainties()

        return self.clip(data)


@serializable(UNIFORM_UNCERTAINTY_ID)
class UniformUncertainty(Uncertainty, Serializable):
    """
    Class implementing uniform uncertainty -- i.e. uniform noise is added to the data.
    
    Parameters
    ----------
    low : `float`, optional
        Lower bound of the uniform noise.

        The default is zero.
    high : `float`, optional
        Upper bound of the uniform noise.

        The default is one.
    """
    def __init__(self, low:float=0., high:float=1., **kwds):
        super().__init__(**kwds)

        self.__min = low
        self.__max = high

    @property
    def min(self) -> float:
        return self.__min

    @property
    def max(self) -> float:
        return self.__max

    def get_attributes(self) -> dict:
        return super().get_attributes() | {"min": self.__min, "low": self.__max}

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.__min == other.min and self.__max == other.max

    def __str__(self) -> str:
        return super().__str__() + f" min: {self.__min} max: {self.__max}"

    def apply(self, data:float) -> float:
        data += np.random.uniform(low=self.__min, high=self.__max)

        return self.clip(data)


@serializable(DEEP_UNIFORM_UNCERTAINTY_ID)
class DeepUniformUncertainty(Uncertainty, Serializable):
    """
    Class implementing deep uniform uncertainty -- i.e. random uniform noise
    (shape of the noise is changing over time) is added to the data.
    """
    def __init__(self, **kwds):
        super().__init__(**kwds)

        self.__create_uncertainties()

    def __create_uncertainties(self, n_samples:int=500):
        self.__uncertainties_idx = 0
        rand_low = create_deep_random_pattern(n_samples)
        rand_high = create_deep_random_pattern(n_samples)
        rand_low = np.minimum(rand_low, rand_high)
        rand_high = np.maximum(rand_low, rand_high)
        self.__uncertainties = [np.random.uniform(l, h) for l, h in zip(rand_low, rand_high)]

    def get_attributes(self) -> dict:
        return super().get_attributes()

    def apply(self, data:float) -> float:
        data += self.__uncertainties[self.__uncertainties_idx]

        self.__uncertainties_idx += 1
        if self.__uncertainties_idx >= len(self.__uncertainties):
            self.__create_uncertainties()

        return self.clip(data)


@serializable(DEEP_GAUSSIAN_UNCERTAINTY_ID)
class DeepGaussianUncertainty(Uncertainty, Serializable):
    """
    Class implementing deep Gaussian uncertainty -- i.e. random Gaussian noise
    (mean and variance are changing over time) is added to the data.
    """
    def __init__(self, **kwds):
        super().__init__(**kwds)

        self.__create_uncertainties()

    def get_attributes(self) -> dict:
        return super().get_attributes()

    def __create_uncertainties(self, n_samples:int=500) -> None:
        self.__uncertainties_idx = 0
        self.__uncertainties = generate_deep_random_gaussian_noise(n_samples)

    def apply(self, data:float) -> float:
        data += self.__uncertainties[self.__uncertainties_idx]

        self.__uncertainties_idx += 1
        if self.__uncertainties_idx >= len(self.__uncertainties):
            self.__create_uncertainties()

        return self.clip(data)


@serializable(DEEP_UNCERTAINTY_ID)
class DeepUncertainty(Uncertainty, Serializable):
    """
    Class implementing deep uncertainty -- i.e. completly random noise is added to the data.
    """
    def __init__(self, min_noise_value:float=0., max_noise_value:float=1., **kwds):
        super().__init__(**kwds)

        self.__min_noise_value = min_noise_value
        self.__max_noise_value = max_noise_value

        self.__uncertainties_idx = None
        self.__create_uncertainties()

    @property
    def min_noise_value(self) -> float:
        return self.__min_noise_value

    @property
    def max_noise_value(self) -> float:
        return self.__max_noise_value

    def get_attributes(self) -> dict:
        return super().get_attributes() | {"min_noise_value": self.__min_noise_value,
                                           "max_noise_value": self.__max_noise_value}

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.__min_noise_value == other.min_noise_value and \
            self.__max_noise_value == other.max_noise_value

    def __str__(self) -> str:
        return super().__str__() + f" min_noise_value: {self.__min_noise_value} "+\
            "max_noise_value: {self.__max_noise_value}"

    def __create_uncertainties(self, n_samples:int=500) -> None:
        init_value = None
        if self.__uncertainties_idx is not None:
            init_value = self.__uncertainties[-1]

        self.__uncertainties_idx = 0
        self.__uncertainties = create_deep_random_pattern(n_samples, self.__min_value,
                                                          self.__max_value, init_value)

    def apply(self, data:float) -> float:
        data += self.__uncertainties[self.__uncertainties_idx]

        self.__uncertainties_idx += 1
        if self.__uncertainties_idx >= len(self.__uncertainties):
            self.__create_uncertainties()

        return self.clip(data)