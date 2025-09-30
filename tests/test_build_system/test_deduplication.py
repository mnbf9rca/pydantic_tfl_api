"""Tests for model deduplication utilities."""

from pydantic import BaseModel, Field, RootModel

from scripts.build_system.utilities import (
    are_models_equal,
    deduplicate_models,
    update_model_references,
)


class TestAreModelsEqual:
    """Test the are_models_equal function for comparing Pydantic models."""

    def test_identical_models_are_equal(self) -> None:
        """Test that two identical models are detected as equal."""

        class Model1(BaseModel):
            id: str
            name: str

        class Model2(BaseModel):
            id: str
            name: str

        assert are_models_equal(Model1, Model2)

    def test_different_field_names_not_equal(self) -> None:
        """Test that models with different field names are not equal."""

        class Model1(BaseModel):
            id: str
            name: str

        class Model2(BaseModel):
            id: str
            title: str

        assert not are_models_equal(Model1, Model2)

    def test_different_field_types_not_equal(self) -> None:
        """Test that models with different field types are not equal."""

        class Model1(BaseModel):
            id: str
            count: int

        class Model2(BaseModel):
            id: str
            count: str

        assert not are_models_equal(Model1, Model2)

    def test_different_aliases_not_equal(self) -> None:
        """Test that models with different field aliases are not equal."""

        class Model1(BaseModel):
            user_id: str = Field(alias="userId")

        class Model2(BaseModel):
            user_id: str = Field(alias="user_id")

        assert not are_models_equal(Model1, Model2)

    def test_different_required_fields_not_equal(self) -> None:
        """Test that models with different required/optional fields are not equal."""

        class Model1(BaseModel):
            id: str
            name: str | None = None

        class Model2(BaseModel):
            id: str
            name: str

        assert not are_models_equal(Model1, Model2)

    def test_non_basemodel_types_not_equal(self) -> None:
        """Test that non-BaseModel types return False."""

        class Model1(BaseModel):
            id: str

        class NotAModel:
            pass

        assert not are_models_equal(Model1, NotAModel)
        assert not are_models_equal(NotAModel, Model1)


class TestDeduplicateModels:
    """Test the deduplicate_models function."""

    def test_no_duplicates_returns_all_models(self) -> None:
        """Test that when there are no duplicates, all models are returned."""

        class Model1(BaseModel):
            id: str

        class Model2(BaseModel):
            name: str

        models: dict[str, type[BaseModel]] = {"Model1": Model1, "Model2": Model2}
        deduplicated, reference_map = deduplicate_models(models)

        assert len(deduplicated) == 2
        assert "Model1" in deduplicated
        assert "Model2" in deduplicated
        assert len(reference_map) == 0

    def test_duplicate_basemodels_detected(self) -> None:
        """Test that duplicate BaseModels are detected and deduplicated."""

        class PlaceCategory(BaseModel):
            id: str = Field(alias="id")
            name: str = Field(alias="name")

        class StopPointCategory(BaseModel):
            id: str = Field(alias="id")
            name: str = Field(alias="name")

        models = {"PlaceCategory": PlaceCategory, "StopPointCategory": StopPointCategory}
        deduplicated, reference_map = deduplicate_models(models)

        # Should keep only one model
        assert len(deduplicated) == 1
        # Should have mapping for the duplicate
        assert len(reference_map) == 1
        assert "StopPointCategory" in reference_map
        assert reference_map["StopPointCategory"] == "PlaceCategory"

    def test_rootmodel_arrays_with_same_inner_type_are_duplicates(self) -> None:
        """Test that RootModel[list[X]] with the same X are detected as duplicates."""

        class TestModel(BaseModel):
            id: str

        # Create two RootModel arrays wrapping the same model
        Array1 = type("Array1", (RootModel[list[TestModel]],), {"__module__": __name__})
        Array2 = type("Array2", (RootModel[list[TestModel]],), {"__module__": __name__})

        models = {"Array1": Array1, "Array2": Array2}
        deduplicated, reference_map = deduplicate_models(models)

        # Should keep only one array model
        assert len(deduplicated) == 1
        assert len(reference_map) == 1
        assert "Array2" in reference_map
        assert reference_map["Array2"] == "Array1"

    def test_rootmodel_arrays_with_different_inner_types_not_duplicates(self) -> None:
        """Test that RootModel[list[X]] with different X are not duplicates."""

        class Model1(BaseModel):
            id: str

        class Model2(BaseModel):
            name: str

        Array1 = type("Array1", (RootModel[list[Model1]],), {"__module__": __name__})
        Array2 = type("Array2", (RootModel[list[Model2]],), {"__module__": __name__})

        models = {"Array1": Array1, "Array2": Array2}
        deduplicated, reference_map = deduplicate_models(models)

        # Should keep both since inner types differ
        assert len(deduplicated) == 2
        assert len(reference_map) == 0


class TestUpdateModelReferences:
    """Test the update_model_references function."""

    def test_models_not_in_reference_map_unchanged(self) -> None:
        """Test that models not in the reference map remain unchanged."""

        class Model1(BaseModel):
            id: str

        models = {"Model1": Model1}
        reference_map: dict[str, str] = {}

        updated = update_model_references(models, reference_map)

        assert "Model1" in updated
        assert updated["Model1"] is Model1

    def test_models_in_reference_map_are_replaced(self) -> None:
        """Test that models in the reference map are replaced with canonical versions."""

        class PlaceCategory(BaseModel):
            id: str

        class StopPointCategory(BaseModel):
            id: str

        models = {"PlaceCategory": PlaceCategory, "StopPointCategory": StopPointCategory}
        reference_map = {"StopPointCategory": "PlaceCategory"}

        updated = update_model_references(models, reference_map)

        # StopPointCategory should now reference PlaceCategory
        assert updated["StopPointCategory"] is PlaceCategory

    def test_rootmodel_references_are_updated(self) -> None:
        """Test that RootModel classes have their inner references updated."""

        class PlaceCategory(BaseModel):
            id: str

        class StopPointCategory(BaseModel):
            id: str

        # Create array that references StopPointCategory
        StopPointCategoryArray = type(
            "StopPointCategoryArray",
            (RootModel[list[StopPointCategory]],),
            {"__module__": __name__},
        )

        models = {
            "PlaceCategory": PlaceCategory,
            "StopPointCategory": StopPointCategory,
            "StopPointCategoryArray": StopPointCategoryArray,
        }

        reference_map = {"StopPointCategory": "PlaceCategory"}

        updated = update_model_references(models, reference_map)

        # Check that the array model now references PlaceCategory
        from typing import get_args

        root_field = updated["StopPointCategoryArray"].model_fields["root"]
        inner_type = get_args(root_field.annotation)[0]

        # The inner type should now be PlaceCategory, not StopPointCategory
        assert inner_type is PlaceCategory


class TestTwoPassDeduplication:
    """Test the two-pass deduplication process (first pass base models, second pass arrays)."""

    def test_stoppoint_category_array_deduplication_scenario(self) -> None:
        """
        INTEGRATION TEST: Reproduce the StopPointCategory deduplication bug.

        This test simulates the exact scenario from the build:
        1. PlaceCategory and StopPointCategory are identical models
        2. PlaceCategoryArray and StopPointCategoryArray are created
        3. First deduplication pass removes duplicate base model
        4. Reference update should update array references
        5. Second deduplication pass should remove duplicate array
        """

        # Step 1: Create two identical base models
        class PlaceCategory(BaseModel):
            id: str = Field(alias="id")
            name: str = Field(alias="name")
            available_keys: list[str] | None = Field(None, alias="availableKeys")

        class StopPointCategory(BaseModel):
            id: str = Field(alias="id")
            name: str = Field(alias="name")
            available_keys: list[str] | None = Field(None, alias="availableKeys")

        # Step 2: Create array models wrapping each base model
        PlaceCategoryArray = type(
            "PlaceCategoryArray",
            (RootModel[list[PlaceCategory]],),
            {"__module__": __name__},
        )

        StopPointCategoryArray = type(
            "StopPointCategoryArray",
            (RootModel[list[StopPointCategory]],),
            {"__module__": __name__},
        )

        models = {
            "PlaceCategory": PlaceCategory,
            "StopPointCategory": StopPointCategory,
            "PlaceCategoryArray": PlaceCategoryArray,
            "StopPointCategoryArray": StopPointCategoryArray,
        }

        # Step 3: First deduplication pass (should deduplicate base models)
        deduplicated_models, reference_map = deduplicate_models(models)

        # Verify: Should have 3 models (PlaceCategory, PlaceCategoryArray, StopPointCategoryArray)
        # and StopPointCategory should be in reference map
        assert len(deduplicated_models) == 3
        assert "PlaceCategory" in deduplicated_models
        assert "PlaceCategoryArray" in deduplicated_models
        assert "StopPointCategoryArray" in deduplicated_models
        assert "StopPointCategory" not in deduplicated_models
        assert "StopPointCategory" in reference_map
        assert reference_map["StopPointCategory"] == "PlaceCategory"

        # Step 4: Update model references
        updated_models = update_model_references(deduplicated_models, reference_map)

        # Verify: StopPointCategoryArray should now reference PlaceCategory internally
        from typing import get_args

        root_field = updated_models["StopPointCategoryArray"].model_fields["root"]
        inner_type = get_args(root_field.annotation)[0]
        assert inner_type is PlaceCategory, "Array should reference PlaceCategory after update"

        # Step 5: Second deduplication pass (should deduplicate arrays)
        final_models, additional_refs = deduplicate_models(updated_models)

        # Verify: Should now have only 2 models (PlaceCategory and PlaceCategoryArray)
        # and StopPointCategoryArray should be in the additional references
        assert len(final_models) == 2, "Should have 2 models after second deduplication pass"
        assert "PlaceCategory" in final_models
        assert "PlaceCategoryArray" in final_models
        assert "StopPointCategoryArray" not in final_models, "Duplicate array should be removed"
        assert "StopPointCategoryArray" in additional_refs
        assert additional_refs["StopPointCategoryArray"] == "PlaceCategoryArray"
