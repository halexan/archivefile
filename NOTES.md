A small notes file to keep track of the behaviors and quirks of different
archive formats, or the libraries I’m using for them, that I’ve discovered
during development.

I often found myself repeatedly testing various operations on each library to
see how they behave, and then weeks later, I would forget the results and do
it all over again. So I decided it is worth writing it all down in one place.

## Reading Non-Files (e.g., directories)

| Archive Type       | Behavior when attempting to read a directory |
| ------------------ | -------------------------------------------- |
| tarfile.TarFile    | Returns `None`                               |
| zipfile.ZipFile    | Returns empty `b""`                          |
| rarfile.RarFile    | Raises `io.UnsupportedOperation`             |
| py7zr.SevenZipFile | Raises `KeyError`                            |

I find returning empty bytes unacceptable, since you can no longer tell
apart an empty file and a directory. So I am left with either returning
`None` or raising an Exception. I ended up going with an Exception (I think
I'll call it `ArchiveMemberNotAFileError`) because 2 out of 4 libraries do
it and it seems the most "correct" behavior to me. Reading a directory is
an error (pathlib will also raise if you try reading a directory with
`.read_bytes()`) and it should be treated as such.
