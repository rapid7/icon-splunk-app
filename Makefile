app:
	rm -rf rapid7_insightconnect
	mkdir rapid7_insightconnect
	cp -r bin default metadata README README.md static appserver rapid7_insightconnect/
	gtar -zcv rapid7_insightconnect > InsightConnect.spl
	rm -rf rapid7_insightconnect
