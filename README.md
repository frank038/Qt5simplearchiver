# Qt5simplearchiver
A simple archive manager.

Version 0.3.5 (testing - development)

No warranty at all. Free to use and modify.

Requirements:
- pyqt5
- python3-xdg
- 7z

Features:
- should work with all archive files managed by 7z
- opens the passworded files supported by 7z: asks for a password
- double click to open the file with the default viewer, if any
- Control key for multiple selections.

Limitations: Drag and drop only works with my file manager SimpleFM and my Qt5desktop program because of a custom mimetype. By default the files are extracted without any parent folders; folders are extract with parent folders if the case. The files to open will be extracted in the /tmp directory.
