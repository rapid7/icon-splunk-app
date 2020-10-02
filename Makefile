VERSION?=$(shell grep 'version: ' extension.spec.yaml | sed 's/version: //')

# Package Splunk app source for import into the Splunk Add-on Builder
importable:
	rm -rf rapid7-insightconnect
	mkdir rapid7-insightconnect
	cp -r appserver bin default local metadata README static app.manifest rapid7-insightconnect.aob_meta README.txt rapid7-insightconnect/
	tar -zcv rapid7-insightconnect > r7_icon_app_aob_importable_$(VERSION).tgz
	rm -rf rapid7-insightconnect

# Run a local Splunk Enterprise server container for app testing/Add-on Builder development/packaging
container:
	docker run -it -p 8000:8000 -e "SPLUNK_PASSWORD=password" -e "SPLUNK_START_ARGS=--accept-license" splunk/splunk:latest

container804:
	docker run -it -p 8000:8000 -e "SPLUNK_PASSWORD=password" -e "SPLUNK_START_ARGS=--accept-license" splunk/splunk:8.0.4.1-debian

container805:
	docker run -it -p 8000:8000 -e "SPLUNK_PASSWORD=password" -e "SPLUNK_START_ARGS=--accept-license" splunk/splunk:8.0.5.1-debian

