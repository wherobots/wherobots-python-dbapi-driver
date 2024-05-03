# Contributor Guidance

## Publish package to PyPI
When we are ready to release a new version `vx.y.z`, one of the maintainers should:
1. Execute `poetry version {minor,patch}` to update the project version
2. Create a new tag `git tag vx.y.z`, if the tag doesn't match with the project version, step 4 validation will fail  
3. push the tag to the repo `git push origin vx.y.z`
4. There will be a GitHub Action triggered automatically, which will build and publish to PyPI