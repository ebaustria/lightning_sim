#!/opt/anaconda1anaconda2anaconda3/bin/python3

import re
from argparse import ArgumentParser
from os import environ
from pathlib import Path
from tempfile import TemporaryDirectory
from subprocess import Popen
from typing import List, Tuple

CXXFLAGS = [
    "-g",
    "-emit-llvm",
    "-Xclang",
    "-no-opaque-pointers",
    "-c",
    "-S",
    "-I/usr/include/x86_64-linux-gnu/c++/11",
    "-I/usr/include/c++/11",
    "-isystem",
    Path(environ["PREFIX"]) / "include",
    ]

REPLACEMENT_MAP: List[Tuple[re.Pattern, str]] = [
    (
        re.compile(r"i"),
        r"{{len(T)}}{{T}}",
    ),
    (
        re.compile(r"float"),
        r"{{T}}",
    ),
    (
        re.compile(r",? align 4"),
        r"",
    ),
    (
        re.compile(r" noundef 4"),
        r" noundef {{(N + 7) // 8}}",
    ),
    (
        re.compile(r"dereferenceable\(4\)"),
        r"dereferenceable({{(N + 7) // 8}})",
    ),
    (
        re.compile(r"float @_ZSt16__deque_buf_sizem\(float 4\)"),
        r"float @_ZSt16__deque_buf_sizem(float {{(N + 7) // 8}})",
    ),
    (
        re.compile(r"mul float %([\w\.]+), 4,"),
        r"mul float %\1, {{(N + 7) // 8}},",
    ),
    (
        re.compile(r"4611686018427387903"),
        r"{{0xffffffffffffffff // ((N + 7) // 8)}}",
    ),
    (
        re.compile(r"2305843009213693951"),
        r"{{0x7fffffffffffffff // ((N + 7) // 8)}}",
    ),
    (
        re.compile(r"sdiv exact i64 %([\w\.]+), 4,"),
        r"sdiv exact i64 %\1, {{(N + 7) // 8}},",
    ),
    (
        re.compile(r"\[50 x i8\]"),
        r"[{{(len(T) * 3) + 23}} x i8]",
    ),
    (
        re.compile(r'c"float _autotb_FifoRead_float\(float \*\)\\00"'),
        r'c"{{T}} _autotb_FifoRead_{{T}}({{T}} *)\\00"',
    ),
]

FIRST_COPY_LINE = "!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())\n"


def main():
    parser = ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("-c", "--cxx", type=str, default="clang-15")
    args = parser.parse_args()

    with TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        subprocess_generate_float = Popen(
            [
                args.cxx,
                args.input,
                *CXXFLAGS,
                "-DT=float",
                "-D_autotb_FifoRead_float=_autotb_FifoRead_float",
                "-D_autotb_FifoWrite_float=_autotb_FifoWrite_float",
                "-o",
                tmpdir / "fifo_float.ll",
                ]
        )
        if subprocess_generate_float.wait() != 0:
            raise RuntimeError("failed to generate fifo_float.ll")

        with open(args.output, "w") as out:
            with open(tmpdir / "fifo_float.ll") as fl:
                for line_no, (line_float) in enumerate(fl):
                    # assert len(line_i32) == len(line_i64)
                    i = 0
                    line = ""
                    # while i < len(line_float):
                    #     for pattern_float, replacement in REPLACEMENT_MAP:
                    #         match_float = pattern_float.match(line_float, i)
                    #         if match_float is None:
                    #             continue
                    #
                    #         line += match_float.expand(replacement)
                    #         i = match_float.end()
                    #         break
                    #     else:
                    #         print("No replacement found "
                    #               f"on line {line_no + 1} "
                    #               f"({line_float!r})")
                    #         line += line_float[i]
                    #         i += 1
                    out.write(line_float)


if __name__ == "__main__":
    main()
