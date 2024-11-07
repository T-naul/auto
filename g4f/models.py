from __future__  import annotations

from dataclasses import dataclass

from .Provider import IterListProvider, ProviderType
from .Provider import (
    ChatGpt,
    OpenaiChat,
)


@dataclass(unsafe_hash=True)
class Model:
    """
    Represents a machine learning model configuration.

    Attributes:
        name (str): Name of the model.
        base_provider (str): Default provider for the model.
        best_provider (ProviderType): The preferred provider for the model, typically with retry logic.
    """
    name: str
    base_provider: str
    best_provider: ProviderType = None

    @staticmethod
    def __all__() -> list[str]:
        """Returns a list of all model names."""
        return _all_models


### Default ###
default = Model(
    name          = "",
    base_provider = "",
    best_provider = IterListProvider([
    ])
)



############
### Text ###
############

### OpenAI ###
# gpt-3
gpt_3 = Model(
    name          = 'gpt-3',
    base_provider = 'OpenAI',
    best_provider = OpenaiChat
)

# gpt-3.5
gpt_35_turbo = Model(
    name          = 'gpt-3.5-turbo',
    base_provider = 'OpenAI',
    best_provider = IterListProvider([OpenaiChat])
)

# gpt-4
gpt_4o = Model(
    name          = 'gpt-4o',
    base_provider = 'OpenAI',
    best_provider = IterListProvider([OpenaiChat])
)

gpt_4o_mini = Model(
    name          = 'gpt-4o-mini',
    base_provider = 'OpenAI',
    best_provider = IterListProvider([ OpenaiChat, ChatGpt])
)

gpt_4_turbo = Model(
    name          = 'gpt-4-turbo',
    base_provider = 'OpenAI',
    best_provider = IterListProvider([OpenaiChat])
)

gpt_4 = Model(
    name          = 'gpt-4',
    base_provider = 'OpenAI',
    best_provider = IterListProvider([OpenaiChat, gpt_4_turbo.best_provider, gpt_4o.best_provider, gpt_4o_mini.best_provider])
)


class ModelUtils:
    """
    Utility class for mapping string identifiers to Model instances.

    Attributes:
        convert (dict[str, Model]): Dictionary mapping model string identifiers to Model instances.
    """
    convert: dict[str, Model] = {
    
############
### Text ###
############
        
### OpenAI ###
# gpt-3
'gpt-3': gpt_3,

# gpt-3.5
'gpt-3.5-turbo': gpt_35_turbo,

# gpt-4
'gpt-4o': gpt_4o,
'gpt-4o-mini': gpt_4o_mini,
'gpt-4': gpt_4,
'gpt-4-turbo': gpt_4_turbo,
    }

_all_models = list(ModelUtils.convert.keys())
