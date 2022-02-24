# Qt5simplearchiver
A simple archive manager.

Version 0.4.4 (testing - development)

No warranty at all. Free to use and modify.

Requirements:
- pyqt5
- python3-xdg
- 7z (p7zip-full is suggested; p7zip-rar is required for rar archives)

Features:
- should work with all archive files managed by 7z
- opens the passworded files supported by 7z: asks for a password
- double click to open the file with the default viewer, if any
- Control key for multiple selections.

Limitations: Drag and drop only works with my file manager SimpleFM and my Qt5desktop program because of a custom mimetype. By default the files are extracted without any parent folders; folders are extract with parent folders if the case. The files to open will be extracted in the /tmp directory. Folder cannot be opened by double clicking. Icons: only folder for folders and file for not folders.

Starting with the version 0.4.0 this program use a different way to parse the archives, by using only the option 'l' instead of the options 'l -ba -slt' that don't give the same output for different kind of archives.
