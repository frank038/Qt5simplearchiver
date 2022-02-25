# Qt5simplearchiver
A simple archive manager.

Version 0.6.0

No warranty at all. Free to use and modify.

Requirements:
- pyqt5
- python3-xdg
- 7z (p7zip-full is suggested; p7zip-rar is required for rar archives; it is used for extracions and for reading the archive content - read below)
- python3-libarchive-c (for reading the archive files; libarchive can be disabled by changing the line 14 of the main file from USE_LIBARCHIVE = 1 to USE_LIBARCHIVE = 0 ; In this case 7z will be used for reading the archive files).

Features:
- should work with all archive files managed by both libarchive and 7z (for extraction 7z is used);
- opens the passworded archives supported by 7z: asks for a password
- double click to open the file with the default viewer, if any
- Control key for multiple selections.

Limitations: Drag and drop only works with my file manager SimpleFM and my Qt5desktop program because of a custom mimetype. By default the files are extracted without any parent folders; folders are extract with parent folders if the case. The files to open will be extracted in the /tmp directory. Folder cannot be opened by double clicking. Icons: only folder for folders and file for not folders.
