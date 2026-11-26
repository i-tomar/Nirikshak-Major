"""Cross-platform runner shared by Make and PowerShell."""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
TARGETS = ("setup", "test", "check", "seed", "run", "evaluate", "real-eval", "security")


def run(*args: object, cwd: Path = ROOT) -> None:
    command = [str(arg) for arg in args]
    print("+", *command, flush=True)
    subprocess.run(command, cwd=cwd, check=True, env={**os.environ, "PYTHONUTF8": "1"})


def npm(*args: str) -> None:
    run(
        shutil.which("npm.cmd" if os.name == "nt" else "npm") or "npm",
        *args,
        cwd=FRONTEND,
    )


def security() -> None:
    run(PYTHON, "-m", "bandit", "-r", "app", cwd=BACKEND)
    run(PYTHON, "-m", "pip_audit", cwd=BACKEND)
    npm("audit", "--omit=dev", "--audit-level=high")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", choices=TARGETS)
    target = parser.parse_args().target
    if target == "setup":
        if not PYTHON.is_file():
            if sys.version_info[:2] != (3, 11):
                parser.exit(1, "Setup requires Python 3.11.\n")
            run(sys.executable, "-m", "venv", ROOT / ".venv")
        run(PYTHON, "-c", "import sys; sys.exit(sys.version_info[:2] != (3,11))")
        run(PYTHON, "-m", "pip", "install", "-r", "requirements-dev.txt", cwd=BACKEND)
        npm("ci")
    elif target == "test":
        run(PYTHON, "-m", "pytest", "-q", "tests", cwd=BACKEND)
    elif target == "seed":
        run(PYTHON, "scripts/seed_demo.py", cwd=BACKEND)
    elif target == "run":
        run("docker", "compose", "up", "--build")
    elif target == "security":
        security()
    elif target == "check":
        run(PYTHON, "-c", "from app.main import app", cwd=BACKEND)
        run(PYTHON, "-m", "pytest", "-q", "tests", cwd=BACKEND)
        for script in sorted((BACKEND / "scripts").glob("verify_phase*.py")):
            run(PYTHON, script, cwd=BACKEND)
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", "main", "--", "*.py"],
            cwd=ROOT,
            text=True,
        ).splitlines()
        if changed:
            run(PYTHON, "-m", "ruff", "check", *changed)
            run(PYTHON, "-m", "mypy", *changed)
        security()
        npm("run", "lint")
        npm("run", "build")
        run("docker", "compose", "build", "backend")
        run(
            "docker",
            "compose",
            "run",
            "--rm",
            "backend",
            "python",
            "scripts/seed_demo.py",
        )
        run("docker", "compose", "run", "--rm", "backend", "pytest", "-q")
    else:
        filename = "evaluate.py" if target == "evaluate" else "external/real_eval.py"
        path = BACKEND / "scripts" / filename
        if not path.is_file():
            parser.exit(
                1,
                f"{target} is scheduled for Phase {7 if target == 'evaluate' else 4}.\n",
            )
        run(PYTHON, path, cwd=BACKEND)


if __name__ == "__main__":
    main()
