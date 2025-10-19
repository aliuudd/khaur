[app]
title = ضياء اليمن للنقل
package.name = dyaa_alyemen
package.domain = org.thiaalyemen.dyaa

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db

version = 1.0
requirements = python3, kivy, pyqt5, sqlite3, fpdf, arabic-reshaper, bidi, reportlab, pillow, babel, pytz

orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.10.1

fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1