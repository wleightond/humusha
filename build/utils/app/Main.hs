module Main where

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

-- COP_f1a -- COP_f1b
splitSents (Sentence (Quant_sent Universal [Name x,Name y] (Bool_sent (BinOp Implication (Atom_sent (Atom (Name_term a) [Term_seq (Name_term x_0),Term_seq (Name_term y_0)]) _) (Atom_sent (Atom (Name_term b) [Term_seq (Name_term y_1),Term_seq (Name_term x_1)]) _)) _) _))  | (x == x_0) && (x == x_1) && (y == y_0) && (y == y_1) && (a == Id.mkSimpleId "PC") = Just ("COP_f1a", [show a, show b]) | (x == x_0) && (x == x_1) && (y == y_0) && (y == y_1) && (b == Id.mkSimpleId "PC") = Just ("COP_f1b", [show a, show b]) | otherwise = Nothing

-- COP_f2
splitSents (Sentence (Quant_sent Universal [Name x,Name y] (Bool_sent (BinOp Implication (Bool_sent (Junction Conjunction [Atom_sent (Atom (Name_term a) [Term_seq (Name_term x_0)]) _,Atom_sent (Atom (Name_term b) [Term_seq (Name_term y_0)]) _]) _) (Bool_sent (Junction Conjunction [Atom_sent (Atom (Name_term c) [Term_seq (Name_term x_1),Term_seq (Name_term y_1)]) _,Atom_sent (Atom (Name_term d) [Term_seq (Name_term y_2),Term_seq (Name_term x_2)]) _]) _)) _) _))  | (x == x_0) && (x == x_1) && (x == x_2) && (y == y_0) && (y == y_1) && (y == y_2) && (c == Id.mkSimpleId "PC") = Just ("COP_f2", [show a, show b, show c, show d]) | otherwise = Nothing

-- PCOP_f1
splitSents (Sentence (Quant_sent Universal [Name x] (Bool_sent (BinOp Implication (Bool_sent (Junction Conjunction [Atom_sent (Atom (Name_term a) [Term_seq (Name_term x_0)]) _,Atom_sent (Atom (Name_term b) [Term_seq (Name_term x_1)]) _]) _) (Atom_sent (Atom (Name_term c) [Term_seq (Name_term x_2)]) _)) _) _))  | (x == x_0) && (x == x_1) && (x == x_2) && (c == Id.mkSimpleId "ED") = Just ("PCOP_f1", [show a, show b, show c]) | otherwise = Nothing

-- PCOP_f2 -- RR_f1 -- RR_f2
splitSents (Sentence (Quant_sent Universal [Name x] (Bool_sent (BinOp Implication (Atom_sent (Atom (Name_term a) [Term_seq (Name_term x_0)]) _) (Atom_sent (Atom (Name_term b) [Term_seq (Name_term x_1)]) _)) _) _))  | (x == x_0) && (x == x_1) && (b == Id.mkSimpleId "PD") = Just ("PCOP_f2", [show a, show b]) | (x == x_0) && (x == x_1) && ((b == Id.mkSimpleId "POB") || (b == Id.mkSimpleId "APO")) = Just ("RR_f1", [show a, show b]) | (x == x_0) && (x == x_1) && ((b == Id.mkSimpleId "SOB") || (b == Id.mkSimpleId "ASO") || (b == Id.mkSimpleId "SAG")) = Just ("RR_f2", [show a, show b]) | otherwise = Nothing

-- QDP
splitSents (Sentence (Quant_sent Universal [Name x] (Bool_sent (BinOp Implication (Atom_sent (Atom (Name_term a) [Term_seq (Name_term x_0)]) _) (Quant_sent Existential [Name y] (Bool_sent (Junction Conjunction [Atom_sent (Atom (Name_term b) [Term_seq (Name_term y_0)]) _,Atom_sent (Atom (Name_term c) [Term_seq (Name_term y_1),Term_seq (Name_term x_1)]) _,Quant_sent Existential [Name z] (Bool_sent (Junction Conjunction [Atom_sent (Atom (Name_term d) [Term_seq (Name_term z_0)]) _,Atom_sent (Atom (Name_term e) [Term_seq (Name_term z_1),Term_seq (Name_term y_2)]) _,Quant_sent Existential [Name v] (Atom_sent (Atom (Name_term f) [Term_seq (Name_term z_2),Term_seq (Name_term v_0)]) _) _]) _) _]) _) _)) _) _))  | (x == x_0) && (x == x_1) && (y == y_0) && (y == y_1) && (y == y_2) && (z == z_0) && (z == z_1) && (z == z_2) && (v == v_0) && (c == Id.mkSimpleId "qt") && (e == Id.mkSimpleId "ql") && (f == Id.mkSimpleId "hasDataValue") = Just ("QDP", [show a, show b, show c, show d, show e, show f]) | otherwise = Nothing

-- RR_f3
splitSents (Sentence (Quant_sent Universal [Name x] (Bool_sent (BinOp Implication (Atom_sent (Atom (Name_term a) [Term_seq (Name_term x_0)]) _) (Quant_sent Existential [Name y] (Bool_sent (Junction Conjunction [Atom_sent (Atom (Name_term b) [Term_seq (Name_term y_0)]) _,Atom_sent (Atom (Name_term r) [Term_seq (Name_term x_1),Term_seq (Name_term y_1)]) _]) _) _)) _) _))  | (x == x_0) && (x == x_1) && (y == y_0) && (y == y_1) && ((r == Id.mkSimpleId "OD") || (r == Id.mkSimpleId "OGD")) = Just ("RR_f3", [show a, show b, show r]) | otherwise = Nothing

-- CDP_f1
splitSents (Sentence (Quant_sent Universal [Name x] (Bool_sent (BinOp Implication (Atom_sent (Atom (Name_term a) [Term_seq (Name_term x_0)]) _) (Quant_sent Existential [Name y] (Bool_sent (Junction Conjunction [Atom_sent (Atom (Name_term b) [Term_seq (Name_term y_0)]) _,Atom_sent (Atom (Name_term c) [Term_seq (Name_term x_1),Term_seq (Name_term y_1)]) _]) _) _)) _) _))  | (x == x_0) && (x == x_1) && (y == y_0) && (y == y_1) = Just ("CDP_f1", [show a, show b, show c]) | otherwise = Nothing

splitSents _ = Nothing


parseText :: [Char] -> Either ParseError TEXT_META
parseText = parse (cltext $ Map.fromList []) ""

extractText :: Either ParseError TEXT_META -> TEXT
extractText textmeta = getText $ rights [textmeta] !! 0

extractPhrases :: TEXT -> [PHRASE]
extractPhrases (Text sentences range) = sentences

keepSplit sentence = (splitSents sentence, AS.printPhrase sentence)

nonesFilter (split, sent) = split /= Nothing

makeStr (split, sent) = "INSTANCE\n" ++ (show split) ++ "\n" ++ (show sent)

main = do
    input <- getContents
    let starr = map makeStr $ filter nonesFilter $ map keepSplit $ (extractPhrases . extractText . parseText) input in for_ starr putStrLn

