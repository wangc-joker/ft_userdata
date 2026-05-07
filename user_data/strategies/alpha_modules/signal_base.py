from abc import ABC, abstractmethod

from pandas import DataFrame


class SignalModule(ABC):
    """Base interface for pluggable entry signal modules."""

    name = "base"
    version = "0.1.0"
    entry_tag = "base"
    long_signal_column = "signal_base_long"
    short_signal_column = "signal_base_short"
    score_column = "signal_base_score"
    priority = 100
    min_score = 0

    def add_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    @abstractmethod
    def generate_entry(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        raise NotImplementedError

    def explain(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "idea": "Base signal interface.",
        }
