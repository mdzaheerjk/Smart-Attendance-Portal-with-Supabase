# Attendence/clients.py
from supabase import create_client
from github import Github
from .config import get_env
from .logger import get_logger

logger = get_logger(__name__)

def create_supabase_client():
    """
    Create and return a supabase client using st.secrets or env variables.
    """
    try:
        url = get_env("SUPABASE_URL")
        key = get_env("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL / SUPABASE_KEY are not set.")
        client = create_client(url, key)
        return client
    except Exception as e:
        logger.exception("Failed to create Supabase client")
        raise

def create_github_repo():
    """
    Create and return a (Github, repo) tuple. 
    If GitHub settings are not provided, returns (None, None).
    """
    try:
        token = get_env("GITHUB_TOKEN")
        username = get_env("GITHUB_USERNAME")
        repo_name = get_env("GITHUB_REPO")

        if not token or not username or not repo_name:
            logger.info("GitHub credentials not fully configured; GitHub features will be disabled.")
            return None, None

        gh = Github(token)
        repo = gh.get_user(username).get_repo(repo_name)
        return gh, repo
    except Exception:
        logger.exception("Failed to create GitHub repo client")
        raise
