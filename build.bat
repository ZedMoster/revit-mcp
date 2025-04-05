python -m build

twine upload dist/*

rmdir /S /Q dist

pause