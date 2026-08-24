[app]

title = Safivox
package.name = safivox
package.domain = org.safivox

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,wav,mp3,ogg,atlas,ttf

version = 1.0.0

requirements = python3,kivy==2.3.1,kivymd==1.2.0,plyer,pyjnius

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,CAMERA,RECORD_AUDIO,SEND_SMS,VIBRATE

android.archs = arm64-v8a
android.minapi = 23
android.api = 35

[buildozer]

log_level = 2
warn_on_root = 1