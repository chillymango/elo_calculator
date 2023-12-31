import os


class Path(str):
    def __call__(self, *paths):
        # Join the current path with the new paths
        new_path = '/'.join([self.rstrip('/')] + [p.strip('/') for p in paths])
        # Return a new Path instance
        return Path(new_path)


PROJECT_ROOT = Path(os.getcwd())
RESOURCES = PROJECT_ROOT("resources")
DATABASE = RESOURCES("primary.db")
TEST_DATABASE = RESOURCES("test.db")


def path_to_sqlalchemy_uri(path: Path) -> str:
    return f"sqlite:///{path}"


def ensure_paths():
    for path in [RESOURCES]:
        os.makedirs(path, exist_ok=True)
