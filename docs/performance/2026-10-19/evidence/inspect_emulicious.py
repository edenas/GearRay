import pathlib,sys
sys.path.insert(0,str(pathlib.Path('build-perf-20261019/python-tools').resolve()))
import jpype
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll', classpath=['D:/Emulicious-with-Java64/Emulicious.jar'])
for name in sys.argv[1:] or ['system.GameGear','system.MasterSystem','components.cpu.Z80','components.cpu.Z80$State','system.Emulation','platform.Emulicious']:
    try:
        c=jpype.JClass(name).class_
        print('\nCLASS',name)
        for x in list(c.getDeclaredConstructors())+list(c.getDeclaredMethods())+list(c.getDeclaredFields()):print(x)
    except Exception as e: print(e)
jpype.shutdownJVM()
