from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union

from pydantic import BaseModel
from pydantic.generics import GenericModel

DataT = TypeVar("DataT", bound=Union[BaseModel, Dict[str, Any]])


class ExceptionModel(BaseModel):
    code: int = 1000
    message: str = ""


class Wrapper(GenericModel, Generic[DataT]):
    code: int = 0
    message: str = ""
    exceptions: Optional[List[ExceptionModel]] = None
    data: DataT


class ApiException(Exception):
    status: int = 500
    code: int = 1000
    message: str = "Unknown Error"

    def __init__(
        self, status: int = 500, code: int = 1000, message: str = "Unknown Error"
    ):
        self.status = status
        self.code = code
        self.message = message.strip()


def wrap(
    data: Optional[Union[DataT]] = None,
    code: Optional[int] = None,
    message: str = "",
    exceptions: Optional[
        List[
            Union[
                ExceptionModel,
                Dict[str, Union[int, str]],
                Tuple[int, str],
                ApiException,
            ]
        ]
    ] = None,
    *,
    error: Union[
        ExceptionModel,
        Dict[str, Union[int, str]],
        Tuple[int, str],
        ApiException,
    ] = None,
):
    """
    Usage:
      wrap(YourModel)  # By default, message will be an empty string
      wrap({foo: "bar"}, 0, "Done!")  # Using a BaseModel is good but dict() is okay
      wrap(code=1011, message="An error has occurred!")  # `code` >= 1000 for errors
      wrap(
          code=1012,
          message="Wrong!",
          exceptions=[
              {"code": 1099, message: "One field is required"},
              (1098, "Another field is wrong!"),
              ("One other field is wrong!", 1097),
              ApiException(1096, "Another Error!"),
              ExceptionModel(code=1095, message="Yet another error!"),
          ]
      )  # `exceptions` can accept these formats, so does `error`

      # If `error` parameter is specified, it will overwrite code and message:
      wrap(error=ApiException(code=1011, message="An error has occurred!"))

      Please be aware that the code will, and should NEVER be 0 if your `data` is None.
    """
    if data is None:
        data = {}
        code = code or 1000
        message = message or "Unknown Error"
    else:
        code = code or 0

    if error is not None:
        if isinstance(error, ExceptionModel) or isinstance(error, ApiException):
            code = error.code
            message = error.message
        elif isinstance(error, dict):
            code = error.get("code", code or 0)
            message = error.get("message", message or "")
        elif isinstance(error, tuple):
            code = error[0] if isinstance(error[0], int) else error[1]
            message = error[0] if isinstance(error[0], str) else error[1]

    parsed_exceptions = []
    if exceptions:
        for item in exceptions:
            if isinstance(item, ExceptionModel):
                parsed_exceptions.append(item)
            elif isinstance(item, ApiException):
                parsed_exceptions.append(
                    ExceptionModel.parse_obj(
                        {
                            "code": item.code,
                            "message": item.message,
                        }
                    )
                )
            elif isinstance(item, dict):
                parsed_exceptions.append(ExceptionModel.parse_obj(item))
            elif isinstance(item, tuple):
                parsed_exceptions.append(
                    ExceptionModel.parse_obj(
                        {
                            "code": item[0] if isinstance(item[0], int) else item[1],
                            "message": item[0] if isinstance(item[0], str) else item[1],
                        }
                    )
                )
    return Wrapper[DataT](
        code=code, message=message, exceptions=parsed_exceptions, data=data
    )


__all__ = ["Wrapper", "ExceptionModel", "wrap"]
