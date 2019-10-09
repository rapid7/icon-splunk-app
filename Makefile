app:
	rm -rf rapid7_insightconnect_event_forwarder
	mkdir rapid7_insightconnect_event_forwarder
	cp -r bin default metadata README README.md static appserver rapid7_insightconnect_event_forwarder/
	tar -zcv rapid7_insightconnect_event_forwarder > InsightConnect.spl
	rm -rf rapid7_insightconnect_event_forwarder
