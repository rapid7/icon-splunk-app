VERSION?=$(shell grep 'version: ' extension.spec.yaml | sed 's/version: //')

app:
	rm -rf rapid7_insightconnect
	mkdir rapid7_insightconnect
	cp -r bin default metadata README README.md static appserver rapid7_insightconnect/
	tar -zcv rapid7_insightconnect > Rapid7_InsightConnect_$(VERSION).spl
	rm -rf rapid7_insightconnect

importable:
	rm -rf rapid7_insightconnect
	mkdir rapid7_insightconnect
	cp -r appserver bin default local metadata README static app.manifest rapid7_insightconnect.aob_meta README.txt rapid7_insightconnect/
	tar -zcv rapid7_insightconnect > r7_icon_app_aob_importable_$(VERSION).tgz
	rm -rf rapid7_insightconnect
