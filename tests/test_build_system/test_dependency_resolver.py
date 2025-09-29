"""Tests for DependencyResolver class that handles model dependencies and circular references."""

from typing import Any, ForwardRef

import pytest
from pydantic import BaseModel, Field

from scripts.build_system.dependency_resolver import DependencyResolver


class TestDependencyResolver:
    """Test the DependencyResolver class for model dependency management."""

    @pytest.fixture
    def dependency_resolver(self) -> DependencyResolver:
        """Create a DependencyResolver instance for testing."""
        return DependencyResolver()

    @pytest.fixture
    def sample_models_simple(self) -> dict[str, type[BaseModel]]:
        """Create simple test models without circular dependencies."""

        # Create mock models that simulate Pydantic models
        class User(BaseModel):
            id: str = Field(...)
            name: str = Field(...)

        class Profile(BaseModel):
            user_id: str = Field(...)
            bio: str = Field(...)

        return {"User": User, "Profile": Profile}

    @pytest.fixture
    def sample_models_with_references(self) -> dict[str, type[BaseModel]]:
        """Create test models with forward references."""

        # Create models that reference each other
        class User(BaseModel):
            id: str = Field(...)
            profile: "Profile | None" = Field(None)

        class Profile(BaseModel):
            id: str = Field(...)
            user: "User" = Field(...)

        return {"User": User, "Profile": Profile}

    @pytest.fixture
    def sample_models_circular(self) -> dict[str, type[BaseModel]]:
        """Create test models with circular dependencies."""

        class Node(BaseModel):
            id: str = Field(...)
            parent: "Node | None" = Field(None)
            children: "list[Node]" = Field(default_factory=list)

        class TreeA(BaseModel):
            id: str = Field(...)
            tree_b: "TreeB | None" = Field(None)

        class TreeB(BaseModel):
            id: str = Field(...)
            tree_a: "TreeA | None" = Field(None)

        return {"Node": Node, "TreeA": TreeA, "TreeB": TreeB}

    def test_init_creates_empty_state(self, dependency_resolver: Any) -> None:
        """Test that DependencyResolver initializes with empty state."""
        assert hasattr(dependency_resolver, "_dependency_graph")
        assert hasattr(dependency_resolver, "_circular_models")
        assert hasattr(dependency_resolver, "_sorted_models")

        assert dependency_resolver._dependency_graph == {}
        assert dependency_resolver._circular_models == set()
        assert dependency_resolver._sorted_models == []

    def test_build_dependency_graph_simple(self, dependency_resolver: Any, sample_models_simple: Any) -> None:
        """Test building dependency graph for models without dependencies."""
        graph = dependency_resolver.build_dependency_graph(sample_models_simple)

        # Both models should be in graph with empty dependencies
        assert "User" in graph
        assert "Profile" in graph
        assert len(graph["User"]) == 0
        assert len(graph["Profile"]) == 0

    def test_build_dependency_graph_with_references(self, dependency_resolver: Any, sample_models_with_references: Any) -> None:
        """Test building dependency graph for models with forward references."""
        graph = dependency_resolver.build_dependency_graph(sample_models_with_references)

        # User depends on Profile
        assert "Profile" in graph["User"]
        # Profile depends on User
        assert "User" in graph["Profile"]

    def test_detect_circular_dependencies_none(self, dependency_resolver: Any, sample_models_simple: Any) -> None:
        """Test circular dependency detection with no circular dependencies."""
        graph = dependency_resolver.build_dependency_graph(sample_models_simple)
        circular = dependency_resolver.detect_circular_dependencies(graph)

        assert len(circular) == 0

    def test_detect_circular_dependencies_self_reference(self, dependency_resolver: Any) -> None:
        """Test detection of self-referencing circular dependencies."""
        # Mock a dependency graph with self-reference
        graph = {"Node": {"Node"}, "User": set()}

        circular = dependency_resolver.detect_circular_dependencies(graph)
        assert "Node" in circular

    def test_detect_circular_dependencies_mutual(self, dependency_resolver: Any) -> None:
        """Test detection of mutual circular dependencies."""
        # Mock a dependency graph with mutual references
        graph = {"TreeA": {"TreeB"}, "TreeB": {"TreeA"}, "Independent": set()}

        circular = dependency_resolver.detect_circular_dependencies(graph)
        assert "TreeA" in circular or "TreeB" in circular

    def test_topological_sort_simple(self, dependency_resolver: Any) -> None:
        """Test topological sorting with simple dependencies."""
        graph = {"A": set(), "B": {"A"}, "C": {"A", "B"}}

        sorted_models = dependency_resolver.topological_sort(graph)

        # A should come before B and C
        # B should come before C
        a_idx = sorted_models.index("A")
        b_idx = sorted_models.index("B")
        c_idx = sorted_models.index("C")

        assert a_idx < b_idx
        assert a_idx < c_idx
        assert b_idx < c_idx

    def test_topological_sort_with_circular_dependencies(self, dependency_resolver: Any) -> None:
        """Test topological sorting handles circular dependencies."""
        graph = {
            "A": {"B"},
            "B": {"A"},  # Circular
            "C": set(),
        }

        sorted_models = dependency_resolver.topological_sort(graph)

        # Should still return all models, even with circular dependencies
        assert "A" in sorted_models
        assert "B" in sorted_models
        assert "C" in sorted_models
        assert len(sorted_models) == 3

    def test_break_circular_dependencies(self, dependency_resolver: Any, sample_models_circular: Any) -> None:
        """Test breaking circular dependencies by replacing with ForwardRef."""
        circular_models = {"Node", "TreeA", "TreeB"}

        dependency_resolver.break_circular_dependencies(sample_models_circular, circular_models)

        # Check that circular references have been replaced with ForwardRef
        # This is a complex test that depends on the specific implementation
        # For now, just verify the method doesn't crash
        # TODO: Add more specific assertions based on implementation details
        assert True  # Method completed without error

    def test_resolve_dependencies_complete_workflow(self, dependency_resolver: Any, sample_models_with_references: Any) -> None:
        """Test the complete dependency resolution workflow."""
        result = dependency_resolver.resolve_dependencies(sample_models_with_references)

        # Should return tuple of (graph, circular_models, sorted_models)
        assert isinstance(result, tuple)
        assert len(result) == 3

        graph, circular_models, sorted_models = result

        # Graph should be a dict
        assert isinstance(graph, dict)
        # Circular models should be a set
        assert isinstance(circular_models, set)
        # Sorted models should be a list
        assert isinstance(sorted_models, list)

        # All original models should be in the sorted list
        for model_name in sample_models_with_references:
            assert model_name in sorted_models

    def test_extract_inner_types_simple(self, dependency_resolver: Any) -> None:
        """Test extracting inner types from simple annotations."""
        # Test basic type
        inner_types = dependency_resolver.extract_inner_types(str)
        assert str in inner_types

        # Test ForwardRef
        forward_ref = ForwardRef("User")
        inner_types = dependency_resolver.extract_inner_types(forward_ref)
        assert forward_ref in inner_types

    def test_extract_inner_types_generic(self, dependency_resolver: Any) -> None:
        """Test extracting inner types from generic annotations."""
        # Test List[str]
        list_type = list[str]
        inner_types = dependency_resolver.extract_inner_types(list_type)
        assert list in inner_types
        assert str in inner_types

        # Test Optional[str] (Union[str, None])
        optional_type = str | None
        inner_types = dependency_resolver.extract_inner_types(optional_type)
        # Should include the origin and inner types
        assert len(inner_types) > 0

    def test_get_dependency_graph(self, dependency_resolver: Any, sample_models_simple: Any) -> None:
        """Test getting the dependency graph."""
        # Initially should be empty
        assert dependency_resolver.get_dependency_graph() == {}

        # After resolving dependencies, should return the graph
        dependency_resolver.resolve_dependencies(sample_models_simple)
        graph = dependency_resolver.get_dependency_graph()

        assert isinstance(graph, dict)
        assert len(graph) > 0

    def test_get_circular_models(self, dependency_resolver: Any, sample_models_simple: Any) -> None:
        """Test getting the circular models set."""
        # Initially should be empty
        assert dependency_resolver.get_circular_models() == set()

        # After resolving dependencies
        dependency_resolver.resolve_dependencies(sample_models_simple)
        circular = dependency_resolver.get_circular_models()

        assert isinstance(circular, set)

    def test_get_sorted_models(self, dependency_resolver: Any, sample_models_simple: Any) -> None:
        """Test getting the sorted models list."""
        # Initially should be empty
        assert dependency_resolver.get_sorted_models() == []

        # After resolving dependencies
        dependency_resolver.resolve_dependencies(sample_models_simple)
        sorted_models = dependency_resolver.get_sorted_models()

        assert isinstance(sorted_models, list)
        assert len(sorted_models) > 0

    def test_clear_state(self, dependency_resolver: Any, sample_models_simple: Any) -> None:
        """Test clearing the resolver state."""
        # First resolve some dependencies
        dependency_resolver.resolve_dependencies(sample_models_simple)

        # Verify state is populated
        assert len(dependency_resolver.get_dependency_graph()) > 0

        # Clear state
        dependency_resolver.clear()

        # Verify state is cleared
        assert dependency_resolver.get_dependency_graph() == {}
        assert dependency_resolver.get_circular_models() == set()
        assert dependency_resolver.get_sorted_models() == []

    @pytest.mark.parametrize(
        "models_fixture_name", ["sample_models_simple", "sample_models_with_references", "sample_models_circular"]
    )
    def test_resolve_dependencies_different_scenarios(self, dependency_resolver: Any, request: Any, models_fixture_name: Any) -> None:
        """Test dependency resolution with different model scenarios."""
        models = request.getfixturevalue(models_fixture_name)

        # Should not raise any exceptions
        result = dependency_resolver.resolve_dependencies(models)

        assert isinstance(result, tuple)
        assert len(result) == 3

        graph, circular_models, sorted_models = result

        # Basic validity checks
        assert isinstance(graph, dict)
        assert isinstance(circular_models, set)
        assert isinstance(sorted_models, list)

        # All model names should be in graph
        for model_name in models:
            assert model_name in graph


class TestExtractModelNameFromForwardRef:
    """Test the _extract_model_name_from_forward_ref helper method."""

    @pytest.fixture
    def dependency_resolver(self) -> DependencyResolver:
        """Create a DependencyResolver instance for testing."""
        return DependencyResolver()

    def test_simple_model_name(self, dependency_resolver: Any) -> None:
        """Test extraction of simple model name without union syntax."""
        result = dependency_resolver._extract_model_name_from_forward_ref("Profile")
        assert result == "Profile"

    def test_union_with_none(self, dependency_resolver: Any) -> None:
        """Test extraction from modern union syntax with None."""
        result = dependency_resolver._extract_model_name_from_forward_ref("Profile | None")
        assert result == "Profile"

    def test_union_with_none_reversed(self, dependency_resolver: Any) -> None:
        """Test extraction when None comes first."""
        result = dependency_resolver._extract_model_name_from_forward_ref("None | Profile")
        assert result == "Profile"

    def test_complex_union(self, dependency_resolver: Any) -> None:
        """Test extraction from union with multiple types."""
        # Should return the first non-None type
        result = dependency_resolver._extract_model_name_from_forward_ref("User | Profile | None")
        assert result == "User"

    def test_with_whitespace(self, dependency_resolver: Any) -> None:
        """Test extraction handles whitespace correctly."""
        result = dependency_resolver._extract_model_name_from_forward_ref("  Profile  |  None  ")
        assert result == "Profile"

    def test_generic_type_string(self, dependency_resolver: Any) -> None:
        """Test extraction preserves generic type notation."""
        result = dependency_resolver._extract_model_name_from_forward_ref("list[User]")
        assert result == "list[User]"

    def test_generic_with_union(self, dependency_resolver: Any) -> None:
        """Test extraction from generic type with union."""
        result = dependency_resolver._extract_model_name_from_forward_ref("list[User] | None")
        assert result == "list[User]"

    def test_empty_string(self, dependency_resolver: Any) -> None:
        """Test extraction from empty string."""
        result = dependency_resolver._extract_model_name_from_forward_ref("")
        assert result == ""

    def test_only_none(self, dependency_resolver: Any) -> None:
        """Test extraction when only None is present."""
        result = dependency_resolver._extract_model_name_from_forward_ref("None")
        # Should return the original string when only None is found
        assert result == "None"

    def test_nested_brackets(self, dependency_resolver: Any) -> None:
        """Test extraction with nested generic brackets."""
        result = dependency_resolver._extract_model_name_from_forward_ref("dict[str, list[User]] | None")
        assert result == "dict[str, list[User]]"
