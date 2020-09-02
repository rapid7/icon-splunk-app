app:
	rm -rf rapid7_insightconnect
	mkdir rapid7_insightconnect
	cp -r bin default metadata README README.md static appserver rapid7_insightconnect/
	tar -zcv rapid7_insightconnect > InsightConnect.spl
	rm -rf rapid7_insightconnect

importable:
	rm -rf rapid7_insightconnect
	mkdir rapid7_insightconnect
	cp -r appserver bin default local metadata README static app.manifest rapid7_insightconnect.aob_meta README.txt rapid7_insightconnect/
	tar -zcv rapid7_insightconnect > r7_icon_app_aob_importable.tgz
	rm -rf rapid7_insightconnect