from __future__ import print_function
import argparse
import codecs
import sys
import re
import os
import cpplint
from cpplint import _cpplint_state
from pylint import epylint

CXX_SUFFIX = {'cc', 'c', 'cpp', 'h', 'cu', 'hpp'}
PYTHON_SUFFIX = {'py'}

def filepath_enumerate(paths):
    """Enumerate the file paths of all subfiles of the list of paths."""
    out = []
    for path in paths:
        if os.path.isfile(path):
            out.append(path)
        else:
            for root, dirs, files in os.walk(path):
                for name in files:
                    out.append(os.path.normpath(os.path.join(root, name)))
    return out

class LintHelper:
    """Class to help run lint checks and record summaries."""

    @staticmethod
    def _print_summary_map(strm, result_map, ftype):
        """Print summary of certain result map."""
        if not result_map:
            return 0
        npass = len([x for x in result_map.values() if not x])
        strm.write(f'====={npass}/{len(result_map)} {ftype} files passed check=====\n')
        for fname, emap in result_map.items():
            if not emap:
                continue
            strm.write(f'{fname}: {sum(emap.values())} Errors of {len(emap)} Categories map={emap}\n')
        return len(result_map) - npass

    def __init__(self):
        self.project_name = None
        self.cpp_header_map = {}
        self.cpp_src_map = {}
        self.python_map = {}
        pylint_disable = ['superfluous-parens', 'too-many-instance-attributes', 'too-few-public-methods']
        self.pylint_opts = ['--extension-pkg-whitelist=numpy', f'--disable={",".join(pylint_disable)}']
        self.pylint_cats = {'error', 'warning', 'convention', 'refactor'}

        cpplint_args = ['.', f'--extensions={",".join(CXX_SUFFIX)}']
        _ = cpplint.ParseArguments(cpplint_args)
        cpplint._SetFilters(','.join(['-build/c++11', '-build/namespaces', '-build/include,',
                                      '+build/include_what_you_use', '+build/include_order']))
        cpplint._SetCountingStyle('toplevel')
        cpplint._line_length = 100

    def process_cpp(self, path, suffix):
        """Process a cpp file."""
        _cpplint_state.ResetErrorCounts()
        cpplint.ProcessFile(str(path), _cpplint_state.verbose_level)
        _cpplint_state.PrintErrorCounts()
        errors = _cpplint_state.errors_by_category.copy()

        if suffix == 'h':
            self.cpp_header_map[str(path)] = errors
        else:
            self.cpp_src_map[str(path)] = errors

    def process_python(self, path):
        """Process a python file."""
        (pylint_stdout, pylint_stderr) = epylint.py_run(
            ' '.join([str(path)] + self.pylint_opts), return_std=True)
        emap = {}
        err = pylint_stderr.read()
        if err:
            print(err)
        for line in pylint_stdout:
            sys.stderr.write(line)
            key = line.split(':')[-1].split('(')[0].strip()
            if key in self.pylint_cats:
                emap[key] = emap.get(key, 0) + 1
        self.python_map[str(path)] = emap

    def print_summary(self, strm):
        """Print summary of lint checks."""
        nerr = 0
        nerr += LintHelper._print_summary_map(strm, self.cpp_header_map, 'cpp-header')
        nerr += LintHelper._print_summary_map(strm, self.cpp_src_map, 'cpp-source')
        nerr += LintHelper._print_summary_map(strm, self.python_map, 'python')
        if nerr == 0:
            strm.write('All passed!\n')
        else:
            strm.write(f'{nerr} files failed lint\n')
        return nerr

_HELPER = LintHelper()

def get_header_guard_dmlc(filename):
    """Get Header Guard Convention for DMLC Projects."""
    fileinfo = cpplint.FileInfo(filename)
    file_path_from_root = fileinfo.RepositoryName()
    inc_list = ['include', 'api', 'wrapper', 'contrib']
    if os.name == 'nt':
        inc_list.append("mshadow")

    if 'src/' in file_path_from_root and _HELPER.project_name is not None:
        idx = file_path_from_root.find('src/')
        file_path_from_root = _HELPER.project_name + file_path_from_root[idx + 3:]
    else:
        idx = file_path_from_root.find("include/")
        if idx != -1:
            file_path_from_root = file_path_from_root[idx + 8:]
        for spath in inc_list:
            prefix = spath + '/'
            if file_path_from_root.startswith(prefix):
                file_path_from_root = re.sub(f'^{prefix}', '', file_path_from_root)
                break
    return re.sub(r'[-./\s]', '_', file_path_from_root).upper() + '_'

cpplint.GetHeaderGuardCPPVariable = get_header_guard_dmlc

def process(fname, allow_type):
    """Process a file based on its type."""
    fname = str(fname)
    arr = fname.rsplit('.', 1)
    if '#' in fname or arr[-1] not in allow_type:
        return
    if arr[-1] in CXX_SUFFIX:
        _HELPER.process_cpp(fname, arr[-1])
    if arr[-1] in PYTHON_SUFFIX:
        _HELPER.process_python(fname)

def main():
    """Main entry function."""
    parser = argparse.ArgumentParser(description="Lint source codes.")
    parser.add_argument('project', help='Project name.')
    parser.add_argument('filetype', choices=['python', 'cpp', 'all'], help='Source code type.')
    parser.add_argument('path', nargs='+', help='Path to traverse.')
    parser.add_argument('--exclude_path', nargs='+', default=[], help='Paths to exclude.')
    parser.add_argument('--pylint-rc', default=None, help='Pylint RC file.')
    args = parser.parse_args()

    _HELPER.project_name = args.project
    if args.pylint_rc:
        _HELPER.pylint_opts = [f'--rcfile={args.pylint_rc}']
    file_type = args.filetype
    allow_type = set()
    if file_type in {'python', 'all'}:
        allow_type.update(PYTHON_SUFFIX)
    if file_type in {'cpp', 'all'}:
        allow_type.update(CXX_SUFFIX)
    
    if sys.version_info.major == 2 and os.name != 'nt':
        sys.stderr = codecs.StreamReaderWriter(sys.stderr,
                                               codecs.getreader('utf8'),
                                               codecs.getwriter('utf8'),
                                               'replace')
    
    excluded_paths = filepath_enumerate(args.exclude_path)
    for path in args.path:
        if os.path.isfile(path):
            normpath = os.path.normpath(path)
            if normpath not in excluded_paths:
                process(path, allow_type)
        else:
            for root, dirs, files in os.walk(path):
                for name in files:
                    file_path = os.path.normpath(os.path.join(root, name))
                    if file_path not in excluded_paths:
                        process(file_path, allow_type)
    
    nerr = _HELPER.print_summary(sys.stderr)
    sys.exit(nerr > 0)

if __name__ == '__main__':
    main()
