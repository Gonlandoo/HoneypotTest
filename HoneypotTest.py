import logging
import subprocess

import symExec

filename = ""
def analyze(filename, disasm_file, source_map = None):
    disasm_out = ""
    try:
        command = 'evm disasm '+filename+'.bytecode'
        disasm_p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        disasm_out=disasm_p.communicate()[0]
        with open(disasm_file, 'w') as of:
            of.write(disasm_out)
        symExec.main(disasm_file, None)
    except:
        logging.critical("Disassembly failed.")

        exit()
def main():
    filename = input("Please input contract name:")
    disasm_file = filename+'.txt'
    analyze(filename, disasm_file)
if __name__ == '__main__':
    main()