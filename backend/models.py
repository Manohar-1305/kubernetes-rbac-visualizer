from typing import List, Optional
from pydantic import BaseModel


class Rule(BaseModel):
    apiGroups: List[str]
    resources: List[str]
    verbs: List[str]
    resourceNames: Optional[List[str]] = None
    nonResourceURLs: Optional[List[str]] = None


class RBACObject(BaseModel):
    kind: str
    name: str
    namespace: Optional[str] = None
    rules: List[Rule] = []


class GraphNode(BaseModel):
    id: str
    label: str
    kind: str
    namespace: Optional[str] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]