module Main where

import CommonLogic.AS_CommonLogic as AS
import Common.GlobalAnnotations (PrefixMap)
import Common.Parsec
import CommonLogic.Parse_CLIF
import Data.Either (lefts, rights)
import qualified Data.Set as Set
import qualified Data.Map as Map
import Data.Foldable (for_)
import Text.ParserCombinators.Parsec as Parsec

parseText :: [Char] -> Either ParseError TEXT_META
parseText = parse (cltext $ Map.fromList []) ""

extractText :: Either ParseError TEXT_META -> TEXT
extractText textmeta = getText $ rights [textmeta] !! 0

extractPhrases :: TEXT -> [PHRASE]
extractPhrases (Text sentences range) = sentences

main = do
    input <- getContents
    let starr = map show $ (extractPhrases . extractText . parseText) input in for_ starr putStrLn
