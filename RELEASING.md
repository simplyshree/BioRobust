# Releasing BioRobust

BioRobust is distributed as a Python package and as source code on GitHub. The release workflow builds a source archive and wheel and attaches them to a GitHub Release. It does not publish to PyPI automatically.

## Before releasing

1. Choose a `MAJOR.MINOR.PATCH` version.
2. Update the version in `pyproject.toml` and `src/biorobust/__init__.py`.
3. Add a matching entry to `CHANGELOG.md`.
4. Update README commands or documentation when the user workflow changes.
5. Run the tests and build the artifacts:

   ```powershell
   python -m pip install -e ".[test,release]"
   python -m pytest -q
   Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
   python -m build
   ```

6. Confirm that `dist/` contains one `.tar.gz` source archive and one `.whl` wheel.
7. When practical, install the wheel into a clean virtual environment and run `biorobust --version`.

## Create a GitHub Release

Commit the versioned changes, then create and push an annotated tag:

```powershell
git add README.md CHANGELOG.md pyproject.toml src/biorobust/__init__.py src/biorobust/rules.py
git commit -m "Release BioRobust 0.4.1"
git tag -a v0.4.1 -m "BioRobust 0.4.1"
git push origin main
git push origin v0.4.1
```

Pushing the tag starts `.github/workflows/release.yml`. The workflow rebuilds the package and creates a GitHub Release with the source archive and wheel. Replace `0.4.1` with the next release version when repeating the process. Do not tag until the tests, changelog, package version, and rule-pack version agree.

## Optional PyPI publication

PyPI publication is a separate maintainer decision. Configure PyPI trusted publishing for the repository before publishing there; never commit a PyPI token or place one in workflow source.

Until a PyPI release exists, users can install the tagged source directly:

```powershell
python -m pip install "biorobust @ git+https://github.com/simplyshree/BioRobust.git@v0.4.1"
```

## Release hygiene

- Do not commit generated reports, cloned repositories, `build/`, or `dist/`.
- Keep report schema and rule IDs compatible unless the change is documented in an ADR.
- Do not describe BioRobust as scientifically validated, clinically certified, secure, or AI-proof.
- After release, install the tagged version and verify `biorobust --version`.
