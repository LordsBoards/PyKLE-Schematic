#!./.venv/bin/python3
from kiutils.schematic import Schematic, SymbolInstance, SchematicSymbol
from kiutils.symbol import SymbolLib  
from kiutils.items.common import Property, Position
import pykle_serial as kle_serial
import json

def create_symbol(schematic, symbol_lib_set, library_path, symbol_name, position, reference, value, properties, footprint):
    symbol_lib = SymbolLib().from_file(library_path)
    symbol = None
    for s in symbol_lib.symbols:
        if s.entryName == symbol_name:
            symbol = s
            break
    if symbol is None:
        raise ValueError('Symbol not found in library')
    else:
        if symbol.entryName not in symbol_lib_set:
            symbol_lib_set.add(symbol.entryName)
            schematic.libSymbols.append(symbol)  

    schematic_symbol = SchematicSymbol()
    schematic_symbol.libName = symbol_name
    schematic_symbol.libId = library_path.split("/")[-1].split(".")[0] + ":" + symbol_name
    schematic_symbol.position = position
    rotation = 0
    if position.angle != 0:
        rotation = 90
    schematic_symbol.onBoard = True
    schematic_symbol.inBom = True
    schematic_symbol.fieldsAutoplaced = True
    schematic_symbol.properties = symbol.properties[0:3]
    schematic_symbol.properties[0].value = reference
    schematic_symbol.properties[1].value = value

    for property in schematic_symbol.properties:
        property.position = Position(
            property.position.X + position.X,
            property.position.Y + position.Y,
            rotation 
        )
    
    if footprint is not None:
        schematic_symbol.properties[2].value = footprint

    schematic.schematicSymbols.append(schematic_symbol)

def custom_round(number):
    return int(number) if number % 1 == 0 else number
  
def generate_schematic(path_to_kle, path_switch_lib, path_stabilizer_lib):

    with open(path_to_kle) as f:
        kle = kle_serial.deserialize(json.load(f))
    
    # Create a new schematic  
    schematic = Schematic.create_new()  
    
    library_symbols = set()
    for i, key in enumerate(kle.keys):
        if (key.height >= 2 or key.width >= 2):
            create_symbol(schematic, library_symbols, path_stabilizer_lib, 'MX_stab', Position(key.x*2.54*10, (key.y)*2.54*10 + 2.54*4, 0), f"STAB{i+1}", f"Stab_{key.labels[0]}", {}, f"PCM_marbastlib-mx:STAB_MX_P_{custom_round(key.width)}u")
            create_symbol(schematic, library_symbols, path_switch_lib, 'MX_SW_solder', Position(key.x*2.54*10, key.y*2.54*10, 0), f"MX{i+1}", f"Key_{key.labels[0]}", {}, f"PCM_marbastlib-mx:SW_MX_1u")
        else:
            create_symbol(schematic, library_symbols, path_switch_lib, 'MX_SW_solder', Position(key.x*2.54*10, key.y*2.54*10, 0), f"MX{i+1}", f"Key_{key.labels[0]}", {}, f"PCM_marbastlib-mx:SW_MX_{custom_round(key.width)}u")
        create_symbol(schematic, library_symbols, '/usr/share/kicad/symbols/Device.kicad_sym', 'D_Small', Position(key.x*2.54*10 + 2.54, key.y*2.54*10 + 1.27*4, 90), f"D{i+1}", "D_Small", {}, None)

    # Save the schematic to a file  
    schematic.to_file('generated_schematic.kicad_sch')  

# Accept args from command line with defaults set
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Generate a KiCad schematic from a KLE file')
    parser.add_argument('--kle', help='Path to KLE file')
    parser.add_argument('--switchlib', help='Path to switch library')
    parser.add_argument('--stabilizerlib', help='Path to stabilizer library')
    args = parser.parse_args()

    if args.kle is None:
        args.kle = './keyboard-layout.json'
    if args.switchlib is None:
        args.switchlib = './marbastlib/symbols/marbastlib-mx.kicad_sym'
    if args.stabilizerlib is None:
        args.stabilizerlib = './marbastlib/symbols/marbastlib-mx.kicad_sym'

    generate_schematic(args.kle, args.switchlib, args.stabilizerlib)