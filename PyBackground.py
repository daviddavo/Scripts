#Esta vez intenta no cargartelo todo, pedazo de subnormal retrasado gilipollas
import os, random, datetime
Dir1 = "/home/davo/Imágenes/Wallpapers/16x9/"
Dir2 = Dir1
Dir3 = "/home/davo/Imágenes/Wallpapers/Vertical/"
log  = "/home/davo/Scripts/BckLog.log"

#feh --bg-fill /Directorio/Imagen.png
#Nota, copia .fehbg a esta carpeta
file1 = Dir1 + random.choice(os.listdir(Dir1))
file2 = Dir2 + random.choice(os.listdir(Dir2))
file3 = "'" + Dir3 + random.choice(os.listdir(Dir3)) + "'"

print(file1, file2, file3)
os.system("DISPLAY=:0 feh --bg-fill " + file1 + " --bg-fill " + file2 + " --bg-fill " + file3)


    
import tempfile

class FileModifierError(Exception):
    pass

class FileModifier(object):

    def __init__(self, fname):
        self.__write_dict = {}
        self.__filename = fname
        self.__tempfile = tempfile.TemporaryFile()
        with open(fname, 'rb') as fp:
            for line in fp:
                self.__tempfile.write(line)
        self.__tempfile.seek(0)

    def write(self, s, line_number = 'END'):
        if line_number != 'END' and not isinstance(line_number, (int, float)):
            raise FileModifierError("Line number %s is not a valid number" % line_number)
        try:
            self.__write_dict[line_number].append(s)
        except KeyError:
            self.__write_dict[line_number] = [s]

    def writeline(self, s, line_number = 'END'):
        self.write('%s\n' % s, line_number)

    def writelines(self, s, line_number = 'END'):
        for ln in s:
            self.writeline(s, line_number)

    def __popline(self, index, fp):
        try:
            ilines = self.__write_dict.pop(index)
            for line in ilines:
                fp.write(line)
        except KeyError:
            pass

    def close(self):
        self.__exit__(None, None, None)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        with open(self.__filename,'w') as fp:
            for index, line in enumerate(self.__tempfile.readlines()):
                self.__popline(index, fp)
                #fp.write(str(line))
            for index in sorted(self.__write_dict):
                for line in self.__write_dict[index]:
                    fp.write(line)
        self.__tempfile.close()

with FileModifier(log) as fp:
    fp.writeline(file1, 0)
    fp.writeline(file2, 1)
    fp.writeline(file3, 2)
    fp.writeline(str(datetime.datetime.today()), 3)
