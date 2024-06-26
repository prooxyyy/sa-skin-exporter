import os
import struct

class DirEntry:
    def __init__(self, offset, fSize, fSize2, fileName):
        self.offset = offset
        self.fSize = fSize
        self.fSize2 = fSize2
        self.fileName = fileName

class IMGArchiveFile:
    def __init__(self, fileEntry, actualFileOffset, actualFileSize, fileByteBuffer):
        self.fileEntry = fileEntry
        self.actualFileOffset = actualFileOffset
        self.actualFileSize = actualFileSize
        self.fileByteBuffer = fileByteBuffer

class IMGArchive:
    def __init__(self, archiveFilePath):
        self.archiveFilePath = archiveFilePath
        self.archiveFileEntries = []
        self.openArchive(archiveFilePath)

    def openArchive(self, archiveFilePath):
        with open(archiveFilePath, 'rb') as f:
            ver = f.read(4)
            if ver[0] == ord('V') and ver[3] == ord('2'):
                entryCount = struct.unpack('<I', f.read(4))[0]
                for _ in range(entryCount):
                    entry_data = f.read(32)
                    offset, fSize, fSize2, fileName = struct.unpack('<IHH24s', entry_data)
                    fileName = fileName.split(b'\0', 1)[0].decode('ascii').lower()
                    self.archiveFileEntries.append(DirEntry(offset, fSize, fSize2, fileName))

    def getFileByName(self, fileName):
        fileName = fileName.lower()
        for entry in self.archiveFileEntries:
            if entry.fileName == fileName:
                with open(self.archiveFilePath, 'rb') as f:
                    actualFileOffset = entry.offset * 2048
                    actualFileSize = entry.fSize * 2048
                    f.seek(actualFileOffset)
                    fileByteBuffer = f.read(actualFileSize)
                    return IMGArchiveFile(entry, actualFileOffset, actualFileSize, fileByteBuffer)
        return None

def read_peds_ide(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    lines = [line.strip() for line in lines if line.strip() and line.lower() not in ('peds', 'end')]

    dff_files = []
    txd_files = []

    for line in lines:
        parts = line.split(',')
        if len(parts) > 2:
            dff_files.append(parts[1].strip().lower() + '.dff')
            txd_files.append(parts[2].strip().lower() + '.txd')

    return dff_files, txd_files

def extract_file(img_archive, file_name, output_folder):
    archive_file = img_archive.getFileByName(file_name)
    if archive_file:
        output_path = os.path.join(output_folder, file_name)
        with open(output_path, 'wb') as out_file:
            out_file.write(archive_file.fileByteBuffer)
        print(f'Файл {file_name} экспортирован в {output_folder}.')
    else:
        print(f'Файл {file_name} не найдено в {img_archive.archiveFilePath}.')

def main():
    peds_ide_path = 'PEDS.IDE' # Путь до IDE файла
    img_file_path = 'player.img' # Путь до .img файла
    output_folder = 'player' # Папка в которую будут загружены скины

    os.makedirs(output_folder, exist_ok=True)

    dff_files, txd_files = read_peds_ide(peds_ide_path)
    img_archive = IMGArchive(img_file_path)

    for file_name in dff_files + txd_files:
        extract_file(img_archive, file_name, output_folder)

if __name__ == '__main__':
    main()
