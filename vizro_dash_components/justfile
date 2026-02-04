set dotenv-load := false

# Generate components and build the bundle
build:
    npm run build

# Build the webpack bundle
build-js:
    npm run build:js

# Generate the components
generate:
    npm run build:backends

# Rebuild the bundle on change
watch:
    npm run watch

# Install  pip requirements & node modules.
install:
    pip install -r requirements.txt
    npm install

# Package the application for distribution using python wheel.
package: clean build
    python -m build --wheel

# Publish the package to pypi using twine.
publish: package
    npm publish
    twine upload dist/*

# Remove dist & build directories
clean:
    rm -rf dist
    rm -rf build
