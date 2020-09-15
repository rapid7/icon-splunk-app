VERSION?=$(shell grep 'version: ' extension.spec.yaml | sed 's/version: //')

# Package a Splunk app for Splunkbase upload
app:
	rm -rf rapid7_insightconnect
	mkdir rapid7_insightconnect
	cp -r bin default metadata README README.md static appserver rapid7_insightconnect/
	tar -zcv rapid7_insightconnect > Rapid7_InsightConnect_$(VERSION).spl
	rm -rf rapid7_insightconnect

# Package Splunk app source for import into the Splunk Add-on Builder
importable:
	rm -rf rapid7_insightconnect
	mkdir rapid7_insightconnect
	cp -r appserver bin default local metadata README static app.manifest rapid7_insightconnect.aob_meta README.txt rapid7_insightconnect/
	tar -zcv rapid7_insightconnect > r7_icon_app_aob_importable_$(VERSION).tgz
	rm -rf rapid7_insightconnect

# Run a local Splunk Enterprise server container for app testing/Add-on Builder use
container:
	docker run -it -p 8000:8000 -e "SPLUNK_PASSWORD=password" -e "SPLUNK_START_ARGS=--accept-license" splunk/splunk:latest