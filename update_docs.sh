#!/usr/bin/env bash

set -e

TMP_DIR=$(mktemp -d)


pushd docs

make clean
sphinx-apidoc -o source ..
make html

cp -r build/html/* ${TMP_DIR}

popd


git checkout gh-pages
rm -rf *
touch .nojekyll
cp -r ${TMP_DIR}/* .
