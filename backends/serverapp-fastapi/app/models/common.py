from typing import Generic, List

from pydantic.generics import GenericModel

from app.utils.wrapper import DataT


class ListResponse(GenericModel, Generic[DataT]):
    items: List[DataT]
