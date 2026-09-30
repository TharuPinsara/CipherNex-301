Test ID,Module,Scenario / Test Case,Expected Result,Actual Result,Status
TC-01,User Auth,Operator team registration with duplicate email.,Return HTTP 409 and prompt user to log in.,Returned HTTP 409 cleanly.,PASS
TC-02,Flag API,Valid submission for current active stage.,Validate SHA-256 signature; unlock next stage.,Verified in constant time; next stage unlocked.,PASS
TC-03,Anti-Bypass,Submitting Stage 8 flag while at Tier 1.,Reject out-of-order jump; keep earlier stages locked.,Out-of-order submission ignored; lock preserved.,PASS
TC-04,SQLi Audit,Injecting SQL payload (' OR '1'='1) into flag input.,Query parameterized safely; evaluate as invalid flag.,Handled via SQLite parameterized statement.,PASS
TC-05,Stego/Forensics,Running strings on raw memory image (STG-03).,Plaintext flag must not appear in static file dump.,Zero matches; flag built dynamically in RAM.,PASS
TC-06,Sandbox Priv,Reading /root/flag.txt as ground-user (STG-06).,Permission denied without exploiting systemd timer.,Permission denied (chmod 0400 on root flag).,PASS
TC-07,Recovery,Executing /api/admin/reset-team-all.,Wipe team solves and reset player back to Tier 1.,Solves removed; progression returned to 1.,PASS
TC-08,Sandbox Reset,Rebooting Stage 6 container via admin console.,Destroy container and restart clean baseline image.,Container rebuilt; /tmp exploit files cleared.,PASS