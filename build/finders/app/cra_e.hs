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

-- CRA_e_f1
splitSents (Sentence (Quant_sent Universal [Name x_0] (Bool_sent (BinOp Implication (Atom_sent (Atom (Name_term a_0) [Term_seq (Name_term x_1)]) _) (Quant_sent Existential [Name y_0] (Bool_sent (Junction Conjunction [Atom_sent (Atom (Name_term b_0) [Term_seq (Name_term x_2),Term_seq (Name_term y_1)]) _,Quant_sent Existential [Name z_0] (Atom_sent (Atom (Name_term c_0) [Term_seq (Name_term y_2),Term_seq (Name_term z_1)]) _) _]) _) _)) _) _))  | (x_0 == x_1) && (x_0 == x_2) && (y_0 == y_1) && (y_0 == y_2) && (z_0 == z_1) && (c_0 == Id.mkSimpleId "hasDataValue") = Just ("CRA_e_f1", [show a_0, show b_0, show c_0]) | otherwise = Nothing

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

