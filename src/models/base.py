from typing import Generic, List, TypeVar
from pydantic import RootModel

T = TypeVar('T')

class ListTemplate(RootModel[T], Generic[T]):
    root: List[T]