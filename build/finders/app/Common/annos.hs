{- |
Module      :  $Id$
Description :  test some parsers (and printers) for annotations
Copyright   :  (c) Christian Maeder, Uni Bremen 2002-2005
License     :  GPLv2 or higher, see LICENSE.txt

Maintainer  :  Christian.Maeder@dfki.de
Stability   :  experimental
Portability :  portable

test some parsers (and printers) for annotations
-}

module Main where

import Common.Token
import Common.RunParsers
import Common.AnnoParser
import Common.Doc
import Common.DocUtils
import Common.AnalyseAnnos
import Common.ConvertGlobalAnnos ()

main :: IO ()
main = exec lineParser fileParser

lineParser :: [(String, StringParser)]
lineParser =
  [ ("MixIds", fromAParser $ parseId [])
  , ("VarIds", fromAParser $ varId [])
  , ("SortIds", fromAParser $ sortId [])
  , ("Annos", fromAParser annotationL) ]

fileParser :: [(String, StringParser)]
fileParser =
  [ ("Annotations", \ ga -> fmap
     (show . useGlobalAnnos ga . vcat . map pretty)
     annotations)
  , ("GlobalAnnos", \ ga -> fmap
     (show . useGlobalAnnos ga . pretty . addGlobalAnnos ga)
     annotations) ]
