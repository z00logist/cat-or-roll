import abc
import dataclasses as dc
import typing as t
import pathlib as pth


@dc.dataclass(frozen=True)
class ClassifierPrediction:
    label: t.Union[t.Literal["Cat"], t.Literal["Roll"]]
    confidence: float


class ClassifierError(Exception):
    pass


class Classifier(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def classify(self, image_locaion: pth.Path) -> ClassifierPrediction:
        raise NotImplementedError