import uvicorn

from server.core.app import create_app
from server.core.database import get_sessionlocal, init_db
from server.core.dependencies import CACHE
from server.utils import tabulation_util
from server.utils.path_util import ensure_paths


def main():
    ensure_paths()
    app = create_app()
    init_db()

    # initialize our cache
    db = get_sessionlocal()()
    tabulation_util.update_cache(CACHE, db)
    db.close()

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")


if __name__ == "__main__":
    main()
