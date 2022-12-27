# Qt5simplearchiver
A simple archive manager.

Version 0.9.3 (testing)

Free to use and modify.

Requirements:
- pyqt5
- python3-xdg
- 7z (p7zip-full is suggested; p7zip-rar is required for rar archives; it is used for extracions and for reading the archive content - read below)
- python3-libarchive-c (for reading the archive files instead of 7z; libarchive can be enabled by changing the line 14 of the main file from USE_LIBARCHIVE = 0 to USE_LIBARCHIVE = 1 ; 7z cannot list the compressed real files inside a tar.gz archives or other double compressed archives).

Features:
- should work with all archive files managed by both libarchive and 7z (for extraction 7z is always used);
- opens the passworded archives supported by 7z: asks for a password
- double click to open the file with the default viewer, if any
- Control key for multiple selections
- items can be added and deleted from the archive
- it is possible to create a completely new archive.

Limitations: Drag and drop, for item extraction, only works with my file manager SimpleFM and my Qt5desktop program because of a custom mimetype. By default the files are extracted with the parent folders; a button in the toolbar can change this behaviour. The files to open/read will be extracted in the /tmp directory first. Folder cannot be opened by double clicking. Icons: only folder for folders and file for not folders.
