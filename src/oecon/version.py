import os
import tomllib


def get_version_from_pyproject(pyproject_path=None):
    """
    Retrieve the version string from pyproject.toml.

    Args:
        pyproject_path (str, optional): Path to pyproject.toml. If None, searches up from current file.

    Returns:
        str: The version string.

    Raises:
        FileNotFoundError: If pyproject.toml is not found.
        KeyError: If version is not found in pyproject.toml.
    """
    if pyproject_path is None:
        # Search for pyproject.toml up the directory tree
        dir_path = os.path.dirname(os.path.abspath(__file__))
        while True:
            candidate = os.path.join(dir_path, "pyproject.toml")
            if os.path.isfile(candidate):
                pyproject_path = candidate
                break
            parent = os.path.dirname(dir_path)
            if parent == dir_path:
                raise FileNotFoundError("pyproject.toml not found.")
            dir_path = parent

    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)
        return pyproject["project"]["version"]


# Example usage:
# version = get_version_from_pyproject()
