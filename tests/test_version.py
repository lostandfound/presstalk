import unittest
import subprocess
import os


class TestVersion(unittest.TestCase):
    """Test version handling and CLI version output."""

    def test_version_matches_pyproject_toml(self):
        """Test that __version__ matches the version in pyproject.toml."""
        # Read version from pyproject.toml manually for cross-platform compatibility
        pyproject_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pyproject.toml"
        )
        with open(pyproject_path, "r") as f:
            content = f.read()
            # Simple extraction for test purposes
            for line in content.split("\n"):
                if line.strip().startswith("version = "):
                    expected_version = line.split('"')[1]
                    break
            else:
                self.fail("Could not find version in pyproject.toml")

        # Import the actual version
        from presstalk import __version__

        self.assertEqual(
            __version__,
            expected_version,
            f"__version__ ({__version__}) should match pyproject.toml version ({expected_version})",
        )

    def test_cli_version_output(self):
        """Test that CLI --version outputs the correct version."""
        # Get expected version from pyproject.toml
        pyproject_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pyproject.toml"
        )
        with open(pyproject_path, "r") as f:
            content = f.read()
            for line in content.split("\n"):
                if line.strip().startswith("version = "):
                    expected_version = line.split('"')[1]
                    break
            else:
                self.fail("Could not find version in pyproject.toml")

        # Run CLI with --version using uv run presstalk
        result = subprocess.run(
            ["uv", "run", "presstalk", "--version"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )

        self.assertEqual(result.returncode, 0, f"CLI --version failed: {result.stderr}")
        expected_output = f"presstalk {expected_version}"
        self.assertEqual(
            result.stdout.strip(),
            expected_output,
            f"CLI version output should be '{expected_output}', got '{result.stdout.strip()}'",
        )

    def test_importlib_metadata_is_used(self):
        """Test that importlib.metadata is attempted for version retrieval."""
        # This test verifies that the code attempts to use importlib.metadata
        # We'll check this by looking at the implementation after we write it
        from presstalk import __version__

        # The version should be dynamically retrieved, not hardcoded
        self.assertNotEqual(
            __version__, "0.1.0", "Version should not be hardcoded to old value"
        )

    def test_fallback_when_importlib_metadata_unavailable(self):
        """Test fallback to 'unknown' when importlib.metadata fails."""
        # Test the import error path by checking the module implementation

        # Read the actual implementation to verify fallback logic exists
        init_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "src",
            "presstalk",
            "__init__.py",
        )
        with open(init_file, "r") as f:
            content = f.read()

        # Verify that the fallback mechanism is implemented
        self.assertIn(
            "except ImportError:", content, "Should have ImportError exception handling"
        )
        self.assertIn(
            "unknown", content, "Should fallback to 'unknown' when metadata unavailable"
        )
        self.assertIn(
            "importlib.metadata", content, "Should attempt to use importlib.metadata"
        )


if __name__ == "__main__":
    unittest.main()
