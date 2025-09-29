"""DependencyResolver class for handling model dependencies and circular references."""

import logging
import types
from collections import defaultdict
from typing import Any, ForwardRef, Union, get_origin, get_args
from pydantic import BaseModel
from .utilities import sanitize_name, get_builtin_types, extract_inner_types


class DependencyResolver:
    """Handles model dependency analysis, circular reference detection, and resolution."""

    def __init__(self):
        """Initialize the DependencyResolver with empty state."""
        self._dependency_graph: dict[str, set[str]] = {}
        self._circular_models: set[str] = set()
        self._sorted_models: list[str] = []
        self.logger = logging.getLogger(__name__)

    def extract_inner_types(self, annotation: Any) -> list[Any]:
        """Extract inner types using the shared utility function."""
        return extract_inner_types(annotation)

    def build_dependency_graph(
        self, models: dict[str, type[BaseModel] | type[list]]
    ) -> dict[str, set[str]]:
        """Build a dependency graph where each model depends on other models."""
        graph = defaultdict(set)

        for model_name, model in models.items():
            if isinstance(model, type) and hasattr(model, "model_fields"):
                # Iterate over each field in the model
                for field in model.model_fields.values():
                    # Recursively unwrap and extract the inner types
                    inner_types = self.extract_inner_types(field.annotation)

                    for inner_type in inner_types:
                        # Handle ForwardRef (string-based references)
                        if isinstance(inner_type, ForwardRef):
                            graph[model_name].add(inner_type.__forward_arg__)

                        # Handle direct model references
                        elif (
                            hasattr(inner_type, "__name__")
                            and inner_type.__name__ in models
                        ):
                            graph[model_name].add(sanitize_name(inner_type.__name__))

                        # If it's a generic type, keep unwrapping
                        elif hasattr(inner_type, "__origin__"):
                            nested_types = self.extract_inner_types(inner_type)
                            for nested_type in nested_types:
                                if isinstance(nested_type, ForwardRef):
                                    graph[model_name].add(nested_type.__forward_arg__)
                                elif (
                                    hasattr(nested_type, "__name__")
                                    and nested_type.__name__ in models
                                ):
                                    graph[model_name].add(
                                        sanitize_name(nested_type.__name__)
                                    )

            # Handle List models (arrays)
            elif hasattr(model, "__origin__") and (
                model.__origin__ is list or model.__origin__ is dict
            ):
                inner_type = model.__args__[0]
                if hasattr(inner_type, "__name__") and inner_type.__name__ in models:
                    graph[model_name].add(sanitize_name(inner_type.__name__))
            else:
                self.logger.warning(
                    f"Model '{model_name}' is not a Pydantic model, dict or list type"
                )

        # finally, add any models which have zero dependencies
        for model_name in models:
            if model_name not in graph:
                graph[model_name] = set()

        self._dependency_graph = dict(graph)
        return self._dependency_graph

    def detect_circular_dependencies(self, graph: dict[str, set[str]]) -> set[str]:
        """Detect circular dependencies in the dependency graph."""
        circular_models = set()
        visited = set()
        stack = set()

        # Use a copy of the graph's keys to avoid modifying the dictionary during iteration
        def visit(model: str):
            if model in visited:
                return
            if model in stack:
                circular_models.add(model)
                return
            stack.add(model)
            for dep in graph.get(model, []):
                visit(dep)
            stack.remove(model)
            visited.add(model)

        # Iterate over a copy of the graph's keys
        for model in list(graph.keys()):
            visit(model)

        self._circular_models = circular_models
        return circular_models

    def topological_sort(self, graph: dict[str, set[str]]) -> list[str]:
        """Perform topological sorting of the dependency graph."""
        # Exclude Python built-in types from the graph
        built_in_types = get_builtin_types()
        sorted_graph = sorted(graph)

        # Filter out built-in types from the graph
        in_degree = {model: 0 for model in sorted_graph if model not in built_in_types}

        for model in sorted_graph:
            if model in built_in_types:
                continue  # Skip built-in types

            for dep in sorted(graph[model]):
                if dep not in built_in_types:
                    if dep not in in_degree:
                        in_degree[dep] = 0
                    in_degree[dep] += 1

        # Initialize the queue with nodes that have an in-degree of 0
        queue = sorted([model for model in in_degree if in_degree[model] == 0])
        sorted_models = []

        while queue:
            model = queue.pop(
                0
            )  # Use pop(0) instead of popleft() for deterministic behavior
            sorted_models.append(model)
            for dep in sorted(graph[model]):
                if dep in built_in_types:
                    continue  # Skip built-in types
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
            queue.sort()  # Sort the queue after each iteration

        if len(sorted_models) != len(in_degree):
            missing_models = sorted(set(in_degree.keys()) - set(sorted_models))
            self.logger.warning(
                f"Circular dependencies detected among models: {missing_models}"
            )
            sorted_models.extend(missing_models)

        self._sorted_models = sorted_models
        return sorted_models

    def replace_circular_references(self, annotation: Any, circular_models: set[str]) -> Any:
        """Recursively replace circular model references in annotations with ForwardRef."""
        origin = get_origin(annotation)
        args = get_args(annotation)

        if not args:
            # Base case: simple type, check if it's circular
            if isinstance(annotation, type) and annotation.__name__ in circular_models:
                return ForwardRef(annotation.__name__)
            return annotation

        # Recurse into generic types
        new_args = tuple(self.replace_circular_references(arg, circular_models) for arg in args)

        if origin is None:
            return annotation

        # Handle different origin types
        if isinstance(origin, types.UnionType):
            # For Python 3.10+ union syntax (X | Y), reconstruct using Union
            return Union[new_args]
        else:
            # For traditional generic types like List[T], Dict[K, V], etc.
            try:
                return origin[new_args]
            except TypeError as e:
                if "not subscriptable" in str(e):
                    # Fallback for any other UnionType-like cases
                    if hasattr(origin, "__name__") and "Union" in str(origin):
                        return Union[new_args]
                    # If we can't handle it, return the original annotation
                    self.logger.warning(f"Could not reconstruct type {origin} with args {new_args}: {e}")
                    return annotation
                raise

    def break_circular_dependencies(
        self, models: dict[str, type[BaseModel]], circular_models: set[str]
    ):
        """Replace circular references in models with ForwardRef."""
        for model_name in circular_models:
            model = models[model_name]
            for field_name, field in model.model_fields.items():
                # Modify field.annotation directly
                field.annotation = self.replace_circular_references(field.annotation, circular_models)

    def resolve_dependencies(self, models: dict[str, type[BaseModel] | type]) -> tuple[dict[str, set[str]], set[str], list[str]]:
        """Complete workflow for resolving model dependencies."""
        graph = self.build_dependency_graph(models)
        circular_models = self.detect_circular_dependencies(graph)
        sorted_models = self.topological_sort(graph)
        self.break_circular_dependencies(models, circular_models)

        return graph, circular_models, sorted_models

    def get_dependency_graph(self) -> dict[str, set[str]]:
        """Get the current dependency graph."""
        return self._dependency_graph.copy()

    def get_circular_models(self) -> set[str]:
        """Get the set of models with circular dependencies."""
        return self._circular_models.copy()

    def get_sorted_models(self) -> list[str]:
        """Get the topologically sorted model list."""
        return self._sorted_models.copy()

    def clear(self) -> None:
        """Clear all resolver state."""
        self._dependency_graph.clear()
        self._circular_models.clear()
        self._sorted_models.clear()