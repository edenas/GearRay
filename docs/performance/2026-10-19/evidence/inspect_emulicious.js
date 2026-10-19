// Reflection probe only; no changes to the installed emulator.
for each (var name in ['system.GameGear','system.MasterSystem','components.cpu.Z80','components.cpu.Z80$State','system.Emulation','platform.Emulicious']) {
  try {
    var c=Java.type(name).class;
    print('\nCLASS '+name);
    for each (var x in c.getDeclaredConstructors()) print(x);
    for each (var x in c.getDeclaredMethods()) print(x);
    for each (var x in c.getDeclaredFields()) print(x);
  } catch(e) { print(e); }
}
