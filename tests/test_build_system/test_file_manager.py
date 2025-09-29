"""Tests for FileManager class that handles all file I/O operations for the build system."""

import os
import shutil
import tempfile
from enum import Enum
from pathlib import Path

import pytest
from pydantic import BaseModel, Field, RootModel

from scripts.build_system.file_manager import FileManager


class TestFileManager:
    """Test the FileManager class for file I/O operations."""

    @pytest.fixture
    def file_manager(self):
        """Create a FileManager instance for testing."""
        return FileManager()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_models(self):
        """Create sample models for testing file operations."""

        class User(BaseModel):
            id: str = Field(...)
            name: str = Field(...)
            age: int | None = Field(None)

        class Profile(BaseModel):
            user_id: str = Field(...)
            bio: str | None = Field(None)

        class UserArray(RootModel[list[User]]):
            pass

        class StatusEnum(Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"

        return {"User": User, "Profile": Profile, "UserArray": UserArray, "StatusEnum": StatusEnum}

    @pytest.fixture
    def sample_dependency_graph(self):
        """Create sample dependency graph for testing."""
        return {"User": set(), "Profile": {"User"}, "UserArray": {"User"}, "StatusEnum": set()}

    def test_init_creates_empty_state(self, file_manager):
        """Test that FileManager initializes properly."""
        assert hasattr(file_manager, "_generated_files")
        assert isinstance(file_manager._generated_files, list)

    def test_save_models_creates_directory_structure(
        self, file_manager, temp_dir, sample_models, sample_dependency_graph
    ):
        """Test that save_models creates the expected directory structure."""
        circular_models: set[str] = set()
        sorted_models = ["User", "Profile", "UserArray", "StatusEnum"]

        file_manager.save_models(sample_models, str(temp_dir), sample_dependency_graph, circular_models, sorted_models)

        # Check that models directory was created
        models_dir = temp_dir / "models"
        assert models_dir.exists()
        assert models_dir.is_dir()

        # Check that __init__.py was created
        init_file = models_dir / "__init__.py"
        assert init_file.exists()

    def test_save_models_creates_model_files(self, file_manager, temp_dir, sample_models, sample_dependency_graph):
        """Test that individual model files are created."""
        circular_models: set[str] = set()
        sorted_models = ["User", "Profile", "UserArray", "StatusEnum"]

        file_manager.save_models(sample_models, str(temp_dir), sample_dependency_graph, circular_models, sorted_models)

        models_dir = temp_dir / "models"

        # Check that model files were created
        assert (models_dir / "User.py").exists()
        assert (models_dir / "Profile.py").exists()
        assert (models_dir / "UserArray.py").exists()
        assert (models_dir / "StatusEnum.py").exists()

    def test_save_model_file_content_structure(self, file_manager, temp_dir, sample_models, sample_dependency_graph):
        """Test that model files have the correct content structure."""
        circular_models: set[str] = set()
        sorted_models = ["User"]

        file_manager.save_models(
            {"User": sample_models["User"]}, str(temp_dir), {"User": set()}, circular_models, sorted_models
        )

        user_file = temp_dir / "models" / "User.py"
        content = user_file.read_text()

        # Check for expected content
        assert "from pydantic import BaseModel, Field, ConfigDict" in content
        assert "class User(BaseModel):" in content
        assert "id: str = Field(...)" in content
        assert "name: str = Field(...)" in content
        assert "age: int | None = Field(None)" in content
        assert "model_config = ConfigDict(from_attributes=True)" in content

    def test_save_root_model_file_content(self, file_manager, temp_dir, sample_models, sample_dependency_graph):
        """Test that RootModel files have the correct content structure."""
        circular_models: set[str] = set()
        sorted_models = ["User", "UserArray"]

        file_manager.save_models(
            {"User": sample_models["User"], "UserArray": sample_models["UserArray"]},
            str(temp_dir),
            {"User": set(), "UserArray": {"User"}},
            circular_models,
            sorted_models,
        )

        array_file = temp_dir / "models" / "UserArray.py"
        content = array_file.read_text()

        # Check for expected RootModel content
        assert "from pydantic import RootModel, ConfigDict" in content
        assert "from .User import User" in content
        assert "class UserArray(RootModel[list[User]]):" in content
        assert "model_config = ConfigDict(from_attributes=True)" in content

    def test_save_enum_file_content(self, file_manager, temp_dir, sample_models, sample_dependency_graph):
        """Test that enum files have the correct content structure."""
        circular_models: set[str] = set()
        sorted_models = ["StatusEnum"]

        file_manager.save_models(
            {"StatusEnum": sample_models["StatusEnum"]},
            str(temp_dir),
            {"StatusEnum": set()},
            circular_models,
            sorted_models,
        )

        enum_file = temp_dir / "models" / "StatusEnum.py"
        content = enum_file.read_text()

        # Check for expected enum content
        assert "from enum import Enum" in content
        assert "class StatusEnum(Enum):" in content
        assert "ACTIVE = 'active'" in content
        assert "INACTIVE = 'inactive'" in content

    def test_save_models_with_circular_dependencies(
        self, file_manager, temp_dir, sample_models, sample_dependency_graph
    ):
        """Test that models with circular dependencies have model_rebuild() calls."""
        circular_models = {"User"}  # Simulate User having circular dependency
        sorted_models = ["User", "Profile"]

        file_manager.save_models(
            {"User": sample_models["User"], "Profile": sample_models["Profile"]},
            str(temp_dir),
            sample_dependency_graph,
            circular_models,
            sorted_models,
        )

        user_file = temp_dir / "models" / "User.py"
        content = user_file.read_text()

        # Should have model_rebuild() call for circular dependency
        assert "User.model_rebuild()" in content

    def test_init_file_content(self, file_manager, temp_dir, sample_models, sample_dependency_graph):
        """Test that __init__.py has the correct import structure."""
        circular_models: set[str] = set()
        sorted_models = ["User", "Profile", "UserArray", "StatusEnum"]

        file_manager.save_models(sample_models, str(temp_dir), sample_dependency_graph, circular_models, sorted_models)

        init_file = temp_dir / "models" / "__init__.py"
        content = init_file.read_text()

        # Check for expected imports
        assert "from .User import User" in content
        assert "from .Profile import Profile" in content
        assert "from .UserArray import UserArray" in content
        assert "from .StatusEnum import StatusEnum" in content

        # Check for GenericResponseModel import
        assert "from ..core.package_models import GenericResponseModel" in content

        # Check for Literal type
        assert "from typing import Literal" in content
        assert "ResponseModelName = Literal[" in content

        # Check for __all__
        assert "__all__ = [" in content

    def test_get_pydantic_imports_base_model(self, file_manager):
        """Test getting imports for BaseModel."""
        imports = file_manager.get_pydantic_imports("User", is_root_model=False)
        assert "BaseModel" in imports
        assert "Field" in imports
        assert "ConfigDict" in imports
        assert "RootModel" not in imports

    def test_get_pydantic_imports_root_model(self, file_manager):
        """Test getting imports for RootModel."""
        imports = file_manager.get_pydantic_imports("UserArray", is_root_model=True)
        assert "RootModel" in imports
        assert "ConfigDict" in imports
        assert "BaseModel" not in imports
        assert "Field" not in imports

    def test_get_model_config(self, file_manager):
        """Test getting model configuration."""
        config = file_manager.get_model_config("User")
        assert "model_config = ConfigDict(from_attributes=True)" in config

    def test_write_import_statements_dependency_order(self, file_manager, temp_dir):
        """Test that import statements are written in dependency-aware order."""
        models = {"A": object, "B": object, "C": object}
        sorted_models = ["A", "B", "C"]  # Predefined order

        models_dir = temp_dir / "models"
        models_dir.mkdir(exist_ok=True)
        init_file = models_dir / "__init__.py"

        with open(init_file, "w") as f:
            file_manager.write_import_statements(f, models, str(models_dir), sorted_models)

        content = init_file.read_text()

        # Should maintain the specified order
        lines = content.strip().split("\n")
        import_lines = [line for line in lines if line.startswith("from .")]

        assert import_lines[0] == "from .A import A"
        assert import_lines[1] == "from .B import B"
        assert import_lines[2] == "from .C import C"

    def test_sanitize_field_name(self, file_manager):
        """Test field name sanitization for Python keywords."""
        # Normal field names should remain unchanged
        assert file_manager.sanitize_field_name("normal_field") == "normal_field"
        assert file_manager.sanitize_field_name("camelCase") == "camelCase"

        # Python keywords should be suffixed
        assert file_manager.sanitize_field_name("class") == "class_field"
        assert file_manager.sanitize_field_name("def") == "def_field"
        assert file_manager.sanitize_field_name("import") == "import_field"

    def test_get_generated_files(self, file_manager, temp_dir, sample_models, sample_dependency_graph):
        """Test tracking of generated files."""
        circular_models: set[str] = set()
        sorted_models = ["User", "Profile"]

        file_manager.save_models(
            {"User": sample_models["User"], "Profile": sample_models["Profile"]},
            str(temp_dir),
            sample_dependency_graph,
            circular_models,
            sorted_models,
        )

        generated_files = file_manager.get_generated_files()

        # Should include all generated files
        assert any("User.py" in file_path for file_path in generated_files)
        assert any("Profile.py" in file_path for file_path in generated_files)
        assert any("__init__.py" in file_path for file_path in generated_files)

    def test_clear_generated_files(self, file_manager):
        """Test clearing the generated files list."""
        # Simulate some generated files
        file_manager._generated_files = ["file1.py", "file2.py"]

        assert len(file_manager.get_generated_files()) == 2

        file_manager.clear_generated_files()

        assert len(file_manager.get_generated_files()) == 0

    def test_create_directory_structure(self, file_manager, temp_dir):
        """Test creating directory structure."""
        models_dir = temp_dir / "models"

        # Directory shouldn't exist initially
        assert not models_dir.exists()

        # Save models should create the directory
        file_manager.save_models({}, str(temp_dir), {}, set(), [])

        # Directory should now exist
        assert models_dir.exists()
        assert models_dir.is_dir()

    def test_handle_file_permissions(self, file_manager, temp_dir, sample_models, sample_dependency_graph):
        """Test that files are created with proper permissions."""
        circular_models: set[str] = set()
        sorted_models = ["User"]

        file_manager.save_models(
            {"User": sample_models["User"]}, str(temp_dir), {"User": set()}, circular_models, sorted_models
        )

        user_file = temp_dir / "models" / "User.py"

        # File should be readable and writable
        assert os.access(user_file, os.R_OK)
        assert os.access(user_file, os.W_OK)

    def test_overwrite_existing_files(self, file_manager, temp_dir, sample_models, sample_dependency_graph):
        """Test that existing files are properly overwritten."""
        models_dir = temp_dir / "models"
        models_dir.mkdir(exist_ok=True)

        # Create an existing file with different content
        user_file = models_dir / "User.py"
        user_file.write_text("# Old content")

        circular_models: set[str] = set()
        sorted_models = ["User"]

        file_manager.save_models(
            {"User": sample_models["User"]}, str(temp_dir), {"User": set()}, circular_models, sorted_models
        )

        # File should have new content
        content = user_file.read_text()
        assert "# Old content" not in content
        assert "class User(BaseModel):" in content

    def test_no_optional_import_with_union_none(self, file_manager, temp_dir):
        """REGRESSION: Test that Optional is not imported when using X | None syntax."""

        class TestModel(BaseModel):
            optional_field: str | None = Field(None)
            required_field: str = Field(...)

        circular_models: set[str] = set()
        sorted_models = ["TestModel"]

        file_manager.save_models(
            {"TestModel": TestModel}, str(temp_dir), {"TestModel": set()}, circular_models, sorted_models
        )

        test_file = temp_dir / "models" / "TestModel.py"
        content = test_file.read_text()

        # Should NOT import Optional when using X | None
        assert "from typing import Optional" not in content
        assert "Optional[" not in content
        assert "optional_field: str | None" in content

    def test_no_unused_type_import(self, file_manager, temp_dir):
        """REGRESSION: Test that Type is not imported when only appearing in model names."""

        class PathAttribute(BaseModel):
            name: str = Field(...)

        class TestModel(BaseModel):
            path_attribute: PathAttribute | None = Field(None)

        circular_models: set[str] = set()
        sorted_models = ["PathAttribute", "TestModel"]

        file_manager.save_models(
            {"PathAttribute": PathAttribute, "TestModel": TestModel},
            str(temp_dir),
            {"PathAttribute": set(), "TestModel": {"PathAttribute"}},
            circular_models,
            sorted_models,
        )

        test_file = temp_dir / "models" / "TestModel.py"
        content = test_file.read_text()

        # "Type" appears in "PathAttribute" but should not be imported from typing
        assert "from typing import Type" not in content
        # PathAttribute should be imported from relative module
        assert "from .PathAttribute import PathAttribute" in content
