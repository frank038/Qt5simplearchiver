# Qt5simplearchiver
A simple archive manager.

Version 0.2 (testing - development)

No warranty at all. Free to use and modify.

Requirements:
- pyqt5
- python3-xdg
- 7z

Features:
- should work with all archive files managed by 7z
- opens the passworded files supported by 7z: asks for a password
- double click to open the file with the default viewer, if any.

Limitations: only one item at time can be extracted. Drag and drop only works with my file manager SimpleFM because both use a custom mimetype. By default the files are extracted without any parent folders; folders are extract with parent folders if the case. The files to open will be extracted in the /tmp directory.
