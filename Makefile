app:
	rm -rf rapid7_insightconnect_A
	mkdir rapid7_insightconnect_A
	cp -r bin default metadata README README.md static appserver rapid7_insightconnect_A/
	tar -zcv rapid7_insightconnect_A > InsightConnect.spl
	rm -rf rapid7_insightconnect_A
