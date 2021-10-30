# Qt5simplearchiver
A simple archive manager.

Version 0.1 (testing - development)

No warranty at all. Free to use and modify.

Requirements:
- pyqt5
- python3-xdg
- 7z

Features:
- should work with all archive files managed by 7z
- opens almost all passworded files supported by 7z (at the moment with 7z archive type don't): asks for a passwor
- double click to open the file with the default viewer, if any.

Limitations: only one item at time can be extracted. Only files can be extracted, no folders and their content. Drag and drop only works with my file manager SimpleFM because both use a custom mimetype. Press the Control key for changing the drag and drop behaviour: by default only the file is extracted; by switching mode the file is extracted with all the folders of its path.
