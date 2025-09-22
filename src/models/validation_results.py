from typing import List, Literal, Union
from pydantic import BaseModel

class Issue(BaseModel):
    id: int
    issue_code: str
    message: str
    primitive: str
    severity: str

class PassedName(BaseModel):
    name: str
    passed: Literal[True]

class FailureName(BaseModel):
    name: str
    passed: Literal[False]
    issues: List[Issue]

# validatorsの要素は、PassedNameまたはFailureNameのどちらかになる
ValidatorResult = Union[PassedName, FailureName]

class PassedResult(BaseModel):
    id: str
    passed: Literal[True]
    validators: List[ValidatorResult] # リストの要素を柔軟にする

class FailureResult(BaseModel):
    id: str
    passed: Literal[False]
    validators: List[ValidatorResult] # こちらも同様

class ValidationResults(BaseModel):
    requirements: List[Union[PassedResult, FailureResult]]
    version: str