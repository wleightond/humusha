#!/usr/bin/env python

import json
from typing import Sequence, Union
from subprocess import Popen, PIPE, STDOUT
from collections.abc import Iterator
from re import findall
from os import system, chdir, remove, listdir

# import dolcetaxonomy as tax
HEADER = """module Main where

import CommonLogic.AS_CommonLogic as AS
import Common.Id as Id
import Common.GlobalAnnotations (PrefixMap)
import Common.Parsec
import CommonLogic.Parse_CLIF

import Data.Either (lefts, rights)
import qualified Data.Set as Set
import qualified Data.Map as Map
import Data.Foldable (for_)
import CommonLogic.Tools as Tools

import Text.ParserCombinators.Parsec as Parsec

"""

FOOTER = """
splitSents _ = Nothing


parseText :: [Char] -> Either ParseError TEXT_META
parseText = parse (cltext $ Map.fromList []) ""

extractText :: Either ParseError TEXT_META -> TEXT
extractText textmeta = getText $ rights [textmeta] !! 0

extractPhrases :: TEXT -> [PHRASE]
extractPhrases (Text sentences range) = sentences

keepSplit sentence = (splitSents sentence, AS.printPhrase sentence)

nonesFilter (split, sent) = split /= Nothing

makeStr (split, sent) = "INSTANCE\\n" ++ (show split) ++ "\\n" ++ (show sent)

main = do
    input <- getContents
    let starr = map makeStr $ filter nonesFilter $ map keepSplit $ (extractPhrases . extractText . parseText) input in for_ starr putStrLn

"""

TARGET = ["./simple_parse"]
FUNCNAME = "splitSents"

cabal_header = """cabal-version:      2.4
name:               clsents
version:            0.1.0.0

-- A short (one-line) description of the package.
-- synopsis:

-- A longer description of the package.
-- description:

-- A URL where users can report bugs.
-- bug-reports:

-- The license under which the package is released.
-- license:
author:             William Leighton Dawson
maintainer:         dwswil002@myuct.ac.za

-- A copyright notice.
-- copyright:
-- category:
extra-source-files:
    CHANGELOG.md
    README.md
"""

cabal_executable = (
    lambda pattern: f"""
executable clsents{pattern}
    main-is:          {pattern}.hs

    -- Modules included in this executable, other than Main.
    other-modules:
        Codec.Binary.UTF8.Generic
        Codec.Binary.UTF8.String
        Common.AS_Annotation
        Common.AnnoParser
        Common.AnnoState
        Common.ConvertLiteral
        Common.Doc
        Common.DocUtils
        Common.GlobalAnnotations
        Common.IRI
        Common.Id
        Common.Keywords
        Common.LaTeX_funs
        Common.LaTeX_maps
        Common.Lexer
        Common.Lib.MapSet
        Common.Lib.Pretty
        Common.Lib.Rel
        Common.Parsec
        Common.Percent
        Common.Prec
        Common.Token
        Common.Utils
        CommonLogic.AS_CommonLogic
        CommonLogic.Lexer_CLIF
        CommonLogic.Parse_CLIF
        CommonLogic.Tools
        Data.ByteString.UTF8
        OWL2.ColonKeywords
        OWL2.Keywords

    -- LANGUAGE extensions used by modules in this package.
    -- other-extensions:
    build-depends:    
        base,
        parsec,
        fgl,
        bytestring ^>=0.11.3.1,
        containers ^>=0.6.5.1,
        directory ^>=1.3.6.2,
        filepath ^>=1.4.2.2,
        process ^>=1.6.13.2
    hs-source-dirs:   app
    default-language: Haskell2010
"""
)


class Enc(Iterator):  # pylint: disable=too-few-public-methods
    def __next__(self):
        return "UTF8"


lower_first = lambda s: s[0].lower() + s[1:]


def get_parsed(sentences: Sequence[str]) -> str:
    with Popen(TARGET, stdin=PIPE, stdout=PIPE, stderr=STDOUT) as proc:
        byte_list = map(lambda x: bytes(*x), zip(sentences, Enc()))
        byte_sents = b"\n".join(byte_list)
        parsed = proc.communicate(input=byte_sents)
    return parsed[0]


def make_constraints(
    constraints: Sequence[tuple[str, Union[str, Sequence[str]]]] = []
) -> str:
    conds = []
    for obj, names in constraints:
        if isinstance(names, str):
            names = [names]
        cond_str = " || ".join(
            [f'({lower_first(obj)}_0 == Id.mkSimpleId "{name}")' for name in names]
        )
        if len(names) > 1:
            cond_str = f"({cond_str})"
        conds.append(cond_str)

    return " && ".join(conds)


def make_var_conds(vcounts: tuple[str, int]) -> str:
    conds = ""
    for vname, vcount in vcounts:
        tmpls = [f"({vname}_0 == {vname}_{i})" for i in range(1, vcount + 1)]
        if conds and tmpls:
            conds += " && "
        conds += " && ".join(tmpls)
    return conds


def get_vars(sentence: str) -> list[str]:
    rexp = r"\((forall|exists)\s*\(([^\(\)]+)\)"
    varsets = findall(rexp, sentence)
    return " ".join([i[1] for i in varsets]).split()


class Pattern:  # pylint: disable=too-few-public-methods
    def __init__(self, name="", sentence="", objs=[], constraints=[]):
        self.name = name
        self.sentence = get_parsed([sentence]).decode("UTF8").strip().split("\n", maxsplit=1)[0]
        self.objs = objs
        self.vars = get_vars(sentence)
        self.constraints = constraints

        self.psent = self.sentence
        vcounts = []
        for name in self.objs:
            self.psent = self.psent.replace(
                f"(Name_term {name})", f"(Name_term {lower_first(name)})"
            )
            old_nt = f"(Name_term {lower_first(name)})"
            vcount = self.psent.count(old_nt)
            vcounts.append((lower_first(name), vcount - 1))
            for i in range(vcount):
                new_nt = f"(Name_term {lower_first(name)}_{i})"
                self.psent = self.psent.replace(old_nt, new_nt, 1)
        for name in self.vars:
            self.psent = self.psent.replace(
                f"[Name {name}]", f"[Name {lower_first(name)}_0]"
            )
            old_nt = f"(Name_term {name})"
            vcount = self.psent.count(old_nt)
            vcounts.append((name, vcount))
            for i in range(1, vcount + 1):
                new_nt = f"(Name_term {lower_first(name)}_{i})"
                self.psent = self.psent.replace(old_nt, new_nt, 1)
        self.psent = self.psent.replace("nullRange", "_")
        hfunc = FUNCNAME + f" ({self.psent}) | "
        var_conds = make_var_conds(vcounts)
        constrs = make_constraints(self.constraints)
        if var_conds:
            hfunc += var_conds
            if constrs:
                hfunc += " && " + constrs
        elif constrs:
            hfunc += constrs
        hfunc += f' = Just ("{self.name}", [show {", show ".join(map(lambda v: lower_first(v) + "_0", self.objs))}])'
        hfunc += " | otherwise = Nothing"
        self.psent = hfunc


def combine_funcs(patterns: list[Pattern]):
    prefixes = {}
    for pattern in patterns:
        func = pattern.psent
        prefix = func[: func.index("|")]
        if prefix not in prefixes:
            prefixes[prefix] = []
        prefixes[prefix].append((pattern.name, func[func.index("|") - 1 : -22]))
        assert func[-22:] == " | otherwise = Nothing"

    comp_funcs = []
    for prefix, suffixes in prefixes.items():
        comments = " ".join(["-- " + i[0] for i in suffixes]) + "\n"
        comp = prefix
        comp += "".join([i[1] for i in suffixes])
        comp += " | otherwise = Nothing\n"
        comp_funcs.append(comments + comp)

    return comp_funcs


if __name__ == "__main__":
    with open("config.json") as f:
        state = json.load(f)

    PATTERNS = {
        pattern.lower(): list(
            map(
                lambda f: Pattern(name=f, **state["formulae"][f]),
                state["patterns"][pattern]["formulae"],
            )
        )
        for pattern in state["patterns"]
    }

    headers_added = []
    pattdir = "build/finders/"
    chdir(pattdir)
    cabalname = "finders.cabal"
    remove(cabalname)
    with open(cabalname, "w") as c:
        c.write(cabal_header)
    for pattern_name in PATTERNS:
        outstr = "\n".join(combine_funcs(PATTERNS[pattern_name]))
        d = HEADER + outstr + FOOTER
        filename = f"app/{pattern_name}.hs"
        with open(filename, "w") as f:
            f.write(d)
        if not pattern_name in headers_added:
            with open(cabalname, "a") as c:
                c.write(cabal_executable(pattern_name))
        headers_added.append(pattern_name)
    system("pwd")
    system("cabal build --verbose=2")
    chdir("../..")
    system("pwd")
    print(f'{PATTERNS = }')
    for pattern_name in PATTERNS:
        sys_folder = listdir("build/finders/dist-newstyle/build")[0]
        ghc_folder = listdir(f"build/finders/dist-newstyle/build/{sys_folder}")[0]
        cpbin = f"cp -v build/finders/dist-newstyle/build/{sys_folder}/{ghc_folder}/clsents-0.1.0.0/x/clsents{pattern_name}/build/clsents{pattern_name}/clsents{pattern_name} bin/find_{pattern_name}_instances"
        system(cpbin)


# 000000001111111111222222222233333333334444444444555555555566666666667777777777
# 234567890123456789012345678901234567890123456789012345678901234567890123456789