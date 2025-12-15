.PHONY: install dev build preview test test-watch test-e2e typecheck package dist run-script clean

install:
	npm install

dev:
	npm run dev

build:
	npm run build

preview:
	npm run preview

test:
	npm test

test-watch:
	npm run test:watch

test-e2e:
	npm run test:e2e

typecheck:
	npm run typecheck

package: build
	npx electron-builder --mac --dir

dist: build
	npx electron-builder --mac

run-script:
	npx tsx scripts/$(FILE)

clean:
	rm -rf dist release node_modules

